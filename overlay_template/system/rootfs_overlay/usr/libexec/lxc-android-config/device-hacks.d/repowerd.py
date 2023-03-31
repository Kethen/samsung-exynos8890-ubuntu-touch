import dbus, time

repowerd_object = None
repowerd_interface = None
repowerd_prop_interface = None
unity_screen_object = None
unity_screen_interface = None

log_cb = None

def init(bus, log):
	global repowerd_object
	global repowerd_interface
	global repowerd_prop_interface
	global unity_screen_object
	global unity_screen_interface
	global log_cb
	log_cb = log
	tries = 0
	while True:
		try:
			repowerd_service_name = "com.lomiri.Repowerd"
			repowerd_object = bus.get_object(repowerd_service_name, "/com/lomiri/Repowerd")
			repowerd_interface = dbus.Interface(repowerd_object, "com.lomiri.Repowerd")
			repowerd_prop_interface = dbus.Interface(repowerd_object, "org.freedesktop.DBus.Properties")
			unity_screen_service_name = "com.canonical.Unity.Screen"
			unity_screen_object = bus.get_object(unity_screen_service_name, "/com/canonical/Unity/Screen")
			unity_screen_interface = dbus.Interface(unity_screen_object, "com.canonical.Unity.Screen")
			repowerd_object.connect_to_signal("Wakeup", wakeup_cb_wrapper, "com.lomiri.Repowerd")
			break
		except Exception as e:
			log_cb(e)
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
		log_cb(e)
		return None

def clearWakeup(cookie):
	try:
		repowerd_interface.clearWakeup(cookie)
		return True
	except Exception as e:
		log_cb(e)
		return False

def requestWakelock(name):
	try:
		cookie = repowerd_interface.requestSysState(name, 1)
		return cookie
	except Exception as e:
		log_cb(e)
		return None

def clearWakelock(cookie):
	try:
		repowerd_interface.clearSysState(cookie)
		return True
	except Exception as e:
		log_cb(e)
		return False

def getWakelockList():
	try:
		val = repowerd_interface.listSysRequests();
		return val
	except Exception as e:
		log_cb(e)
		return None

def daemonHasActiveWakelock():
	val = getWakelockList()
	if val is None:
		return False
	return len(val) > 0

wakeup_cb = None
def wakeup_cb_wrapper(*arg, **karg):
	if wakeup_cb is not None:
		wakeup_cb()

def register_wakeup_cb(cb):
	global wakeup_cb
	wakeup_cb = cb
