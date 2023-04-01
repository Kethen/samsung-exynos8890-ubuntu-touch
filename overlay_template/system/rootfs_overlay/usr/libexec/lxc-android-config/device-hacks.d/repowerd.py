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
			if __name__ != "__main__":
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

def requestDisplayOn():
	try:
		cookie = unity_screen_interface.keepDisplayOn()
		return cookie
	except Exception as e:
		log_cb(e)
		return None

def clearDisplayOn(cookie):
	try:
		unity_screen_interface.removeDisplayOnRequest(cookie)
		return True
	except Exception as e:
		log_cb(e)
		return False

# mode as string "on" or "off"
enum_reason_notification = 4
enum_reason_snap_decision = 5
def setScreenPowerMode(mode, reason):
	try:
		ret = unity_screen_interface.setScreenPowerMode(mode, reason)
		return ret
	except Exception as e:
		log_cb(e)
		return False

def getWakelockList():
	try:
		val = repowerd_interface.listSysRequests();
		if "request_sys_state" in val:
			return val["request_sys_state"]
		log_cb("warning: request_sys_state not found in listSysRequests dump")
		return None
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

def main_log(message):
	print(message)

def main():
	bus = dbus.SystemBus()
	try:
		init(bus, main_log)
	except Exception as e:
		print(e)

	print("requesting wakelock")
	wake_cookies = []
	display_on_cookies = []
	for f in range(0,3):
		print("requesting wakelock #{0}".format(f))
		cookie = requestWakelock("test {0}".format(f))
		print("wakelock #{0} has cookie {1}".format(f, cookie))
		wake_cookies.append(cookie)
		print("requesting displayon #{0}".format(f))
		cookie = requestDisplayOn()
		print("displayon #{0} has cookie {1}".format(f, cookie))
		display_on_cookies.append(cookie)
		setScreenPowerMode("on", enum_reason_notification)

	time.sleep(5)

	print(daemonHasActiveWakelock())

	for cookie in wake_cookies:
		print("releasing wakelock with cookie {0}".format(cookie))
		clearWakelock(cookie)
		time.sleep(5)

	print(daemonHasActiveWakelock())

	for cookie in display_on_cookies:
		print("releasing display on with cookie {0}".format(cookie))
		clearDisplayOn(cookie)
		time.sleep(5)

	print(daemonHasActiveWakelock())

	for f in range(0,3):
		print("releasing notifications")
		setScreenPowerMode("off", enum_reason_snap_decision)
		time.sleep(5)

	print(daemonHasActiveWakelock())

if __name__ == "__main__":
	main()
