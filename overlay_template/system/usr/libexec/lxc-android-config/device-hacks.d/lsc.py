import time, dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

lsc_object = None
lsc_prop_interface = None
logcb = None
bus = None

first_launch = True
def init(in_bus, log):
	tries = 0
	global lsc_object
	global lsc_prop_interface
	global logcb
	global bus
	global first_launch
	logcb = log
	bus = in_bus
	if first_launch:
		setup_name_change_handler()
		first_launch = False
	while True:
		try:
			lsc_object = bus.get_object("com.lomiri.SystemCompositor.Display", "/com/lomiri/SystemCompositor/Display")
			lsc_prop_interface = dbus.Interface(lsc_object, "org.freedesktop.DBus.Properties")
			lsc_object.connect_to_signal("PropertiesChanged", active_output_cb_wrapper, "org.freedesktop.DBus.Properties")
			break
		except Exception as e:
			logcb(e)
			time.sleep(1)
			tries = tries + 1
			if tries > 20:
				raise("could not connect to lomiri system compositor through dbus")
			continue

interface_active = False
def name_change_handler(*arg, **karg):
	global interface_active
	active = arg[2] != ""
	changed = False
	if arg[0] == "com.lomiri.SystemCompositor.Display":
		interface_active = active
		changed = True
	if interface_active and changed:
		logcb("lsc restart detected, re-init")
		init(bus, logcb)

def setup_name_change_handler():
	dbus_service_name = "org.freedesktop.DBus"
	dbus_object = bus.get_object(dbus_service_name, "/org/freedesktop/DBus")
	dbus_object.connect_to_signal("NameOwnerChanged", name_change_handler, "org.freedesktop.DBus")


has_active_output_cb = None
def active_output_cb_wrapper(*arg, **karg):
	logcb("active_output_cb_wrapper reached")
	if has_active_output_cb is None:
		return
	for output_state in arg[1]["ActiveOutputs"]:
		if output_state == 1:
			has_active_output_cb(True)
			return
	has_active_output_cb(False)

def register_has_active_output_cb(cb):
	global has_active_output_cb
	has_active_output_cb = cb

def main_log(message):
	print(message)

def main():
	DBusGMainLoop(set_as_default=True)
	new_bus = dbus.SystemBus()
	try:
		init(new_bus, main_log)
	except Exception as e:
		print(e)

	loop = GLib.MainLoop()
	loop.run()

if __name__ == "__main__":
	main()
