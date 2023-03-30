import time, dbus

lsc_object = None
lsc_prop_interface = None
def init(bus):
	tries = 0
	global lsc_object
	global lsc_prop_interface
	while True:
		try:
			lsc_object = bus.get_object("com.lomiri.SystemCompositor.Display", "/com/lomiri/SystemCompositor/Display")
			lsc_prop_interface = dbus.Interface(lsc_object, "org.freedesktop.DBus.Properties")
			lsc_object.connect_to_signal("PropertiesChanged", active_output_cb, "org.freedesktop.DBus.Properties")
			break
		except Exception as e:
			print(e)
			time.sleep(1)
			tries = tries + 1
			if tries > 20:
				raise("could not connect to lomiri system compositor through dbus")
			continue

has_active_output_cb = None
def active_output_cb(*arg, **karg):
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
