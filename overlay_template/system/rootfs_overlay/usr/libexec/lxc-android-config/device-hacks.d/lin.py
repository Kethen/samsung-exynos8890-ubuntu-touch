import dbus, time
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

bus = None
log_cb = None
first_run = True

status_prop_interface = None
private_prop_interface = None
private_interface = None

def init(in_bus, log):
	global bus
	global log_cb
	global first_run
	global status_prop_interface
	global private_prop_interface
	global private_interface
	bus = in_bus
	log_cb = log

	if first_run:
		setup_name_change_handler()
		first_run = False
	while True:
		try:
			service_name = "com.lomiri.connectivity1"
			status_object = bus.get_object(service_name, "/com/lomiri/connectivity1/NetworkingStatus")
			status_prop_interface = dbus.Interface(status_object, "org.freedesktop.DBus.Properties")
			private_object = bus.get_object(service_name, "/com/lomiri/connectivity1/Private")
			private_prop_interface = dbus.Interface(private_object, "org.freedesktop.DBus.Properties")
			private_interface = dbus.Interface(private_object, "com.lomiri.connectivity1.Private")
			break
		except Exception as e:
			log_cb(e)
			if __name__ != "__main__":
				time.sleep(1)
			tries = tries + 1
			if tries > 20:
				raise Exception("could not connect to lomiri-indicator-network through dbus")
			continue

def name_change_handler(*arg, **karg):
	if arg[0] == "com.lomiri.connectivity1":
		log_cb("lomiri-indicator-network restart detected, re-init")
		init(bus, log_cb)

def setup_name_change_handler():
	dbus_service_name = "org.freedesktop.DBus"
	dbus_object = bus.get_object(dbus_service_name, "/org/freedesktop/DBus")
	dbus_object.connect_to_signal("NameOwnerChanged", name_change_handler, "org.freedesktop.DBus")

def is_wifi_on():
	try:
		is_on = status_prop_interface.Get("com.lomiri.connectivity1.NetworkingStatus", "WifiEnabled")
		if is_on == 1:
			return True
		else:
			return False
	except Exception as e:
		log_cb(e)
		return False

def is_cellular_data_on():
	try:
		is_on = private_prop_interface.Get("com.lomiri.connectivity1.Private", "MobileDataEnabled")
		if is_on == 1:
			return True
		else:
			return False
	except Exception as e:
		log_cb(e)
		return False

def toggle_wifi(on):
	try:
		private_interface.SetWifiEnabled(on)
		return True
	except Exception as e:
		log_cb(e)
		return False

def toggle_cellular_data(on):
	try:
		val = 0
		if on:
			val = 1
		private_prop_interface.Set("com.lomiri.connectivity1.Private", "MobileDataEnabled", val)
		return True
	except Exception as e:
		log_cb(e)
		return False

def log_main(m):
	print(m)

if __name__ == "__main__":
	try:
		first_run = False
		init(dbus.SessionBus(), log_main)
	except:
		pass

	print(is_wifi_on())
	print(is_cellular_data_on())

	toggle_wifi(0)
	toggle_cellular_data(0)
	time.sleep(5)
	toggle_wifi(1)
	toggle_cellular_data(1)
