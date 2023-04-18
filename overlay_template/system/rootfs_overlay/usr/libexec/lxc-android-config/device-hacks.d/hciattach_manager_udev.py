import subprocess
import threading
import time
import re
import pathlib
import os

# the first reset goes into a black hole and has no hci return
# it confuses hciattach so it has to be done here
reset_command = bytearray([0x01, 0x03, 0x0C, 0x00])
tty_path = "/dev/ttySAC1"
def first_boot_pre_reset():
	print("resetting bt chip for hciattach")
	target_tty_fd = os.open(tty_path, os.O_RDWR | os.O_NOCTTY)
	bytes_written = os.writev(target_tty_fd, [reset_command])
	print("wrote {0} to {1}, {2} bytes".format(reset_command, tty_path, bytes_written))
	os.close(target_tty_fd)

def btchip_toggle(on):
	if on:
		command = "unblock"
	else:
		command = "block"
	subprocess.run(["rfkill", command, "bluetooth"])
	time.sleep(1)

# could this cause race condition..?
hciattach_on = False
hciattach_process = None
hciattach_process_lock = threading.Lock()

rfkill_ignore = False;
rfkill_ignore_lock = threading.Lock()

hciattach_args = ["hciattach", "-n", "-f", "/vendor/firmware", "-t", "20", "ttySAC1", "bcm43xx", "921600", "flow", "nosleep"]

macaddr_file_path = pathlib.Path("/efs/bluetooth/bt_addr")
if macaddr_file_path.exists():
	macaddr_file = open(macaddr_file_path, "r")
	macaddr = macaddr_file.read()
	macaddr_file.close()
	print("using macaddress from {0}".format(macaddr_file_path))
	hciattach_args.append(macaddr)
else:
	print("cannot open {0} for macaddress".format(macaddr_file_path))

bt_rfkill_state_file = "/userdata/bt_was_off"

launch_attempts = 1;
launch_attempts_lock = threading.Lock()
def hciattach_watchdog_thread():
	global rfkill_ignore
	global hciattach_process
	global launch_attempts
	global hciattach_on
	restart_bt = False
	if hciattach_process is not None:
		ret = hciattach_process.wait()
	while True:
		hciattach_process_lock.acquire()
		print("hciattach_on: {0}".format(hciattach_on))
		if hciattach_on == False:
			print("stopping hciattach watchdog thread")
			hciattach_process_lock.release()
			return

		if restart_bt:
			rfkill_ignore_lock.acquire()
			rfkill_ignore = True
			rfkill_ignore_lock.release()
			btchip_toggle(False)
			btchip_toggle(True)
			rfkill_ignore_lock.acquire()
			rfkill_ignore = False
			rfkill_ignore_lock.release()

		hciattach_process = subprocess.Popen(hciattach_args)
		hciattach_process_lock.release()
		launch_attempts_lock.acquire()
		launch_attempts = launch_attempts + 1
		launch_attempts_lock.release()
		ret = hciattach_process.wait()
		time.sleep(0.5)
		restart_bt = not restart_bt

def start_hciattach():
	global hciattach_on
	global launch_attempts
	global hciattach_process
	launch_attempts = 0
	stop_hciattach()
	hciattach_process_lock.acquire()
	hciattach_on = True
	hciattach_process = subprocess.Popen(hciattach_args)
	hciattach_process_lock.release()
	thread = threading.Thread(target=hciattach_watchdog_thread)
	thread.start()
	bt_rfkill_state = pathlib.Path(bt_rfkill_state_file)
	bt_rfkill_state.unlink(missing_ok=True)

def stop_hciattach():
	global hciattach_process
	global hciattach_on
	if not hciattach_on:
		return
	hciattach_process_lock.acquire()
	if hciattach_process is not None:
		hciattach_process.terminate()
		hciattach_process.wait()
	hciattach_process = None
	hciattach_on = False
	hciattach_process_lock.release()
	bt_rfkill_state = pathlib.Path(bt_rfkill_state_file)
	bt_rfkill_state.touch()

rfkill_id = None
for p in pathlib.Path("/sys/class/rfkill/").iterdir():
	name_path = pathlib.Path("{0}/name".format(p))
	if name_path.exists():
		f = open(name_path, "r")
		name = f.read()
		f.close()
		if name == "bcm4359 Bluetooth\n":
			pattern = re.compile("/sys/class/rfkill/(rfkill[0-9]+)")
			match = pattern.match(str(p))
			rfkill_id = match.group(1)
			print("found bcm4359 rfkill at {0}".format(rfkill_id))
			break

soft_path = pathlib.Path("/sys/class/rfkill/{0}/soft".format(rfkill_id))
f = open(soft_path, "r")
launch_state = f.read()
f.close()

first_boot_detect_file = pathlib.Path("/tmp/hciattach_manager_booted")
first_boot = False
if not first_boot_detect_file.exists():
	first_boot_detect_file.touch()
	first_boot = True

was_activated = True
bt_rfkill_state = pathlib.Path(bt_rfkill_state_file)
if bt_rfkill_state.exists():
	was_activated = False

if first_boot:
	print("restoring rfkill state")
	# give urfkill a brief wait
	time.sleep(3)
	print("bt rfkill is currently {0}".format(launch_state))
	btchip_toggle(True)
	first_boot_pre_reset()
	print("starting hciattach after booting")
	start_hciattach()
	time.sleep(10)
	if not was_activated:
		print("disabling bt")
		stop_hciattach()
		btchip_toggle(False)
	else:
		print("turning hciattach spawned device on")
		btchip_toggle(True)
else:
	if launch_state == "0\n":
		print("manager started with bt unblocked, starting hciattach")
		start_hciattach()

udev_monitor_process = subprocess.Popen(["udevadm", "monitor", "-k", "-s", "rfkill"], stdout=subprocess.PIPE)
pattern = re.compile("^KERNEL\[.+\]\s*change\s*/devices/bluetooth/rfkill/{0}\s*\(rfkill\).*$".format(rfkill_id))
while True:
	line = udev_monitor_process.stdout.readline().decode("utf-8")
	rfkill_ignore_lock.acquire()
	if rfkill_ignore:
		rfkill_ignore_lock.release()
		continue
	match = pattern.match(line)
	print(line)
	if match is not None:
		f = open("/sys/class/rfkill/{0}/soft".format(rfkill_id), "r")
		state = f.read()
		f.close()
		if state == "1\n":
			print("stopping hciattach")
			stop_hciattach()
		else:
			print("starting hciattach")
			start_hciattach()
	rfkill_ignore_lock.release()

