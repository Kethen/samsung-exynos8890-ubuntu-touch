import dbus

bus = dbus.SystemBus()

wifi_interface_name = "wlan0"

tries = 0
while True:
	try:
		nm_service_name = "org.freedesktop.NetworkManager"
		nm_object = bus.get_object(nm_service_name, "/org/freedesktop/NetworkManager")
		nm_interface = dbus.Interface(nm_object, "org.freedesktop.NetworkManager")
		nm_props_interface = dbus.Interface(nm_object, "org.freedesktop.DBus.Properties")
		break
	except Exception as e:
		print(e)
		tries = tries + 1
		if tries > 20:
			raise Exception("could not connect to network manager through dbus")
		continue

def is_hotspot_mode():
	try:
		devpath = nm_interface.GetDeviceByIpIface(wifi_interface_name)

		iface_object = bus.get_object(nm_service_name, devpath)
		iface_props_interface = dbus.Interface(iface_object, "org.freedesktop.DBus.Properties")

		iface_mode = iface_props_interface.Get("org.freedesktop.NetworkManager.Device.Wireless", "Mode")

		return iface_mode == 3
	except Exception as e:
		print(e)
		return False

def is_wifi_on():
	try:
		wifi_on = nm_props_interface.Get("org.freedesktop.NetworkManager", "WirelessEnabled")
		return wifi_on == 1
	except Exception as e:
		print(e)
		return False

def toggle_wifi(enabled):
	try:
		nm_props_interface.Set("org.freedesktop.NetworkManager", "WirelessEnabled", enabled)
		return True
	except Exception as e:
		print(e)
		return False

def get_active_cellular_connection():
	try:
		active_connections = nm_props_interface.Get("org.freedesktop.NetworkManager", "ActiveConnections")
		for connection_path in active_connections:
			connection_object = bus.get_object(nm_service_name, connection_path)
			connection_prop_interface = dbus.Interface(connection_object, "org.freedesktop.DBus.Properties")
			if connection_prop_interface.Get("org.freedesktop.NetworkManager.Connection.Active", "Type") == "gsm":
				return connection_path
		return None
	except:
		return None

def is_cellular_data_on():
	return get_active_cellular_connection() is not None

def toggle_cellular_data(enable):
	if enable == is_cellular_data_on():
		return True
	try:
		if not enable:
			active_connection_path = get_active_cellular_connection()
			active_connection_object = bus.get_object(nm_service_name, active_connection_path)
			nm_interface.DeactivateConnection(active_connection_object)
			return True
		else:
			settings_object = bus.get_object(nm_service_name, "/org/freedesktop/NetworkManager/Settings")
			settings_interface = dbus.Interface(settings_object, "org.freedesktop.NetworkManager.Settings")
			connections = settings_interface.ListConnections()
			for path in connections:
				connection_object = bus.get_object(nm_service_name, path)
				connection_interface = dbus.Interface(connection_object, "org.freedesktop.NetworkManager.Settings.Connection")
				connection_settings = connection_interface.GetSettings()
				if 'connection' in connection_settings:
					con = connection_settings["connection"]
					if "id" in con:
						id = con["id"]
						if id == "Internet":
							nm_interface.ActivateConnection(path, "/", "/")
							return True
			return False
	except Exception as e:
		print(e)
		return False
