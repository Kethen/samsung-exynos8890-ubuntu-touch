import dbus, time

repowerd_object = None
repowerd_interface = None
unity_screen_object = None
unity_screen_interface = None

def init(bus):
	tries = 0
	while True:
		global repowerd_object
		global repowerd_interface
		global unity_screen_object
		global unity_screen_interface
		try:
			repowerd_service_name = "com.lomiri.Repowerd"
			repowerd_object = bus.get_object(repowerd_service_name, "/com/lomiri/Repowerd")
			repowerd_interface = dbus.Interface(repowerd_object, "com.lomiri.Repowerd")
			unity_screen_service_name = "com.canonical.Unity.Screen"
			unity_screen_object = bus.get_object(unity_screen_service_name, "/com/canonical/Unity/Screen")
			unity_screen_interface = dbus.Interface(unity_screen_object, "com.canonical.Unity.Screen")
			repowerd_object.connect_to_signal("Wakeup", wakeup_cb_wrapper, "com.lomiri.Repowerd")
			break
		except Exception as e:
			print(e)
			time.sleep(1)
			tries = tries + 1
			if tries > 20:
				raise Exception("could not connect to repowerd through dbus")
			continue

# time in integer posix time https://en.cppreference.com/w/cpp/chrono/c/time_t
def requestWakeup(name, time):
	try:
		cookie = repowerd_interface.requestWakeup(name, time)
		return cookie
	except Exception as e:
		print(e)
		return None

def clearWakeup(cookie):
	try:
		repowerd_interface.clearWakeup(cookie)
		return True
	except Exception as e:
		print(e)
		return False


screen_match_string = "type='signal',member='PropertiesChanged',interface='org.freedesktop.DBus.Properties',path='/com/lomiri/Repowerd'"
wakeup_match_string = "type='signal',member='Wakeup',interface='com.lomiri.Repowerd',path='/com/lomiri/Repowerd'"

wakeup_cb = None
def wakeup_cb_wrapper(*arg, **karg):
	if wakeup_cb is not None:
		wakeup_cb()

def register_wakeup_cb(cb):
	global wakeup_cb
	wakeup_cb = cb
