#!/usr/bin/python3
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
import subprocess
import gbinder
import time
from threading import Thread, Lock

import nm_wifi_cellular as nm

match_string = "type='signal',member='Changed',interface='org.gtk.Actions',path='/org/ayatana/indicator/power'"

#small_core_io_busy = open('/sys/devices/system/cpu/cpu0/cpufreq/interactive/io_is_busy', "w")
#big_core_io_busy = open('/sys/devices/system/cpu/cpu4/cpufreq/interactive/io_is_busy', "w")
#core_count = open('/sys/power/cpuhotplug/max_online_cpu', "w")

binder_interface = "/dev/binder"
service_name = "android.hardware.power.IPower/default"
interface_name = "android.hardware.power.IPower"

# https://cs.android.com/android/platform/superproject/+/android-11.0.0_r48:hardware/interfaces/power/aidl/aidl_api/android.hardware.power/current/android/hardware/power/IPower.aidl
set_mode_id = 1
set_boost_id = 3

# https://cs.android.com/android/platform/superproject/+/android-11.0.0_r48:hardware/interfaces/power/aidl/aidl_api/android.hardware.power/current/android/hardware/power/Mode.aidl
mode_enum_interactive = 7
mode_enum_sustained_performance = 2
mode_enum_expensive_rendering = 6
mode_enum_low_power = 1

# https://cs.android.com/android/platform/superproject/+/android-11.0.0_r48:hardware/interfaces/power/aidl/aidl_api/android.hardware.power/current/android/hardware/power/Boost.aidl
boost_enum_interaction = 0

first_boot_check_file = "/tmp/aidl_perf_boost_booted"

power_saving_toggle_file = "/home/phablet/.config/power_saving"
network_power_saving_toggle_file = "/home/phablet/.config/network_power_saving"

def is_network_power_saving():
	try:
		f = open(network_power_saving_toggle_file, "r")
		f.close()
		return True
	except:
		return False

def is_power_saving():
	try:
		f = open(power_saving_toggle_file, "r")
		f.close()
		return True
	except:
		return False

first_boot_state = None
def is_first_boot():
	global first_boot_state
	if first_boot_state is None:
		try:
			open(first_boot_check_file, "r")
			first_boot_state = False
		except:
			first_boot_state = True
			f = open(first_boot_check_file, "w")
			f.close()
	return first_boot_state

restore_id = 0
restore_id_lock = Lock()
state = None
def disable_network():
	nm.toggle_wifi(False)
	nm.toggle_cellular_data(False)

def restore_network_state():
	global state
	if state is None:
		return
	if state["wifi"]:
		nm.toggle_wifi(True)
	if state["cellular"]:
		nm.toggle_cellular_data(True)

def network_power_saving_thread(assigned_restore_id):
	online_time_sec = 15
	offline_time_sec = 120
	global restore_id
	if restore_id != assigned_restore_id:
		return
	while True:
		time.sleep(online_time_sec)
		restore_id_lock.acquire()
		if restore_id != assigned_restore_id:
			restore_id_lock.release()
			#print("exiting power saving thread")
			return
		#print("power saving thread disabling networking")
		disable_network()
		restore_id_lock.release()

		time.sleep(offline_time_sec)
		restore_id_lock.acquire()
		if restore_id != assigned_restore_id:
			restore_id_lock.release()
			#print("exiting power saving thread")
			return
		#print("power saving thread restoring network state")
		restore_network_state()
		restore_id_lock.release()

def start_network_power_saving():
	global restore_id
	global state
	if nm.is_hotspot_mode():
		return
	# if it goes in and out of interactive more than 3600 times it actually breaks
	restore_id_lock.acquire()
	restore_id = (restore_id + 1) % 3600
	state = {"wifi": nm.is_wifi_on(), "cellular": nm.is_cellular_data_on()}
	t = Thread(target = network_power_saving_thread, args = [restore_id])
	t.start()
	restore_id_lock.release()

def stop_network_power_saving():
	global restore_id
	restore_id_lock.acquire()
	restore_id = (restore_id + 1) % 3600
	restore_network_state()
	restore_id_lock.release()
	global state
	state = None

def set_mode(client, type_enum, enable):
	if enable:
		enable = 1
	else:
		enable = 0
	request = client.new_request()
	request.append_int32(type_enum)
	request.append_int32(enable)
	reply, status = client.transact_sync_reply(set_mode_id, request)
	return (reply, status)

def set_boost(client, type_enum, duration_ms):
	request = client.new_request()
	request.append_int32(type_enum)
	request.append_int32(duration_ms)
	reply, status = client.transact_sync_reply(set_boost_id, request)
	return (reply, status)

was_interactive = not is_first_boot()
set_interactive_client = None
def set_interactive(is_interactive):
	global was_interactive
	global set_interactive_client
	if set_interactive_client is None:
		set_interactive_client = gbinder.Client(service, interface_name)
	client = set_interactive_client

	if client is None:
		raise Exception("failed opening {0}::{1}".format(service_name, interface_name))

	if is_interactive != was_interactive:
		was_interactive = is_interactive
		power_saving = is_power_saving()
		network_power_saving = is_network_power_saving()

		if is_interactive:
			# this is supposed to be triggered by android wm for various animations, instead of on screen-on
			# https://cs.android.com/search?q=Boost.INTERACTION&ss=android%2Fplatform%2Fsuperproject:frameworks%2F
			# note that 8890bootpulse partially does it current by polling user input and setting one of the kernel interfaces directly
			set_boost(client, boost_enum_interaction, 3 * 1000)
		set_mode(client, mode_enum_interactive, is_interactive)
		set_mode(client, mode_enum_sustained_performance, is_interactive and (not power_saving))
		# pre-ramp up gpu clock at least for the s7 https://github.com/8890q/android_device_samsung_universal8890-common/blob/lineage-19.1/configs/power/powerhint.json#L417
		# given the way UT renders currently it helps with the UI, seems to help scrolling in morph browser as well
		set_mode(client, mode_enum_expensive_rendering, is_interactive and (not power_saving))
		set_mode(client, mode_enum_low_power, (not is_interactive) or power_saving)

		if network_power_saving and (not is_interactive):
			start_network_power_saving()
		else:
			stop_network_power_saving()


	#if is_interactive:
	#	p = subprocess.run(['/usr/bin/getprop', '8890.interactive_big_cores'], stdout=subprocess.PIPE)
	#	cores = int(p.stdout) + 4
	#	print(cores)
	#	io_active = 1
	#else:
	#	p = subprocess.run(['/usr/bin/getprop', '8890.idle_big_cores'], stdout=subprocess.PIPE)
	#	cores = int(p.stdout) + 4
	#	print(cores)
	#	io_active = 0

	#small_core_io_busy.write(io_active)
	#big_core_io_busy.write(io_active)
	#core_count.write(cores)

def filter_cb(bus, message):
	arg_list = message.get_args_list()
	for item in arg_list:
		if isinstance(item, dict):
			if 'brightness' in item:
				brightness = item['brightness']
				if brightness < 0:
					set_interactive(False)
				else:
					set_interactive(True)

sm = gbinder.ServiceManager(binder_interface)
intf = sm.list_sync();

service = None
tries = 0
while service is None and tries < 20:
	service, status = sm.get_service_sync(service_name)
	time.sleep(0.5)
	tries = tries + 1

if service is None:
	raise Exception("failed oepning {0}".format(service_name))

print("binder is ready")

DBusGMainLoop(set_as_default=True)

bus = dbus.SessionBus()
bus.add_match_string(match_string)
bus.add_message_filter(filter_cb)

set_interactive(is_first_boot())

print("starting glib loop")
loop = GLib.MainLoop()
loop.run()

