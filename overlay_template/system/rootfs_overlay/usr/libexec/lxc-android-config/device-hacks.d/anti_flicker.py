from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop
import re
import dbus

import lsc

import time

sysfs_path = "/sys/class/lcd/panel/smart_on"
toggle_file = "/home/phablet/.config/anti_flicker"

def log(message):
	print(message)

def is_gracerlte():
	try:
		prop_file = open("/vendor/build.prop", "r")
		model_line = re.compile("^ro.product.vendor.device=(.+)$")
		for line in prop_file.readlines():
			match = model_line.match(line)
			if match is not None:
				return match.group(1) == "gracerlte"
		return False
	except Exception as e:
		log(e)
		return False

def anti_flicker_enabled():
	try:
		f = open(toggle_file, "r")
		f.close()
		return True
	except:
		return False

def anti_flicker_enabled_on_kernel():
	f = open(sysfs_path, "r")
	value = f.read()
	f.close()
	return value == "1\n"

toggled_anti_flicker_on = anti_flicker_enabled_on_kernel()
def screen_on_cb(screen_on):
	global toggled_anti_flicker_on
	if screen_on:
		return
	enabled = anti_flicker_enabled()

	if toggled_anti_flicker_on != enabled:
		value = 0;
		if enabled:
			value = 1
		try:
			f = open(sysfs_path, "w")
			f.write("{0}\n".format(value))
			f.close()
		except Exception as e:
			print(e)
		toggled_anti_flicker_on = enabled

if not is_gracerlte():
	lsc.register_has_active_output_cb(screen_on_cb)
	DBusGMainLoop(set_as_default=True)
	bus = dbus.SystemBus()
	lsc.init(bus, log)
else:
	print("device is gracerlte, doing nothing")

print("starting glib loop")
loop = GLib.MainLoop()
loop.run()
