#!/usr/bin/python3
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
import subprocess
import gbinder
import time

match_string = "type='signal',member='Changed',interface='org.gtk.Actions',path='/org/ayatana/indicator/power'"

#small_core_io_busy = open('/sys/devices/system/cpu/cpu0/cpufreq/interactive/io_is_busy', "w")
#big_core_io_busy = open('/sys/devices/system/cpu/cpu4/cpufreq/interactive/io_is_busy', "w")
#core_count = open('/sys/power/cpuhotplug/max_online_cpu', "w")

binder_interface = "/dev/hwbinder"
service_name = "android.hardware.power@1.0::IPower/default"
interface_name = "android.hardware.power@1.0::IPower"

set_interactive_tid = 1

was_interactive = False
def set_interactive(is_interactive):
	global was_interactive
	if is_interactive != was_interactive:
		request = client.new_request()
		request.append_bool(is_interactive)
		reply, status = client.transact_sync_reply(set_interactive_tid, request)
		was_interactive = is_interactive

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

if service is None:
	raise Exception("failed oepning {0}".format(service_name))

client = gbinder.Client(service, interface_name)

if client is None:
	raise Exception("failed opening {0}::{1}".format(service_name, interface_name))

print("binder is ready")

DBusGMainLoop(set_as_default=True)

bus = dbus.SessionBus()
bus.add_match_string(match_string)
bus.add_message_filter(filter_cb)

print("starting glib loop")
loop = GLib.MainLoop()
loop.run()

