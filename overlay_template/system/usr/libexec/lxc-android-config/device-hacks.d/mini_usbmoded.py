#!/usr/bin/python3
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop
import dbus
import dbus.service
import subprocess
import os
import signal

# This was made because usb-moded is not very legacy device friendly

service_name = "com.meego.usb_moded"
interface_name = "com.meego.usb_moded"
object_path = "/com/meego/usb_moded"

mode_setting_script = "/usr/libexec/lxc-android-config/device-hacks.d/setupusb.sh"
config_path = "/userdata/mini_usbmoded_config"

def stop_adbd():
	print("stopping adbd systemd service")
	p = subprocess.run(["/usr/bin/systemctl", "stop", "adbd"], capture_output=True)
	print(p.stdout)
	print(p.stderr)

def start_adbd():
	print("starting adbd systemd service")
	p = subprocess.run(["/usr/bin/systemctl", "start", "adbd"], capture_output=True)
	print(p.stdout)
	print(p.stderr)

class MiniUsbModed(dbus.service.Object):
	def __init__(self, bus, object_path):
		dbus.service.Object.__init__(self, bus, object_path)
		try:
			f = open(config_path, "r")
			self.config = f.read()
		except:
			self.config = "mtp"
		self.set_mode(self.config)

	@dbus.service.method(interface_name, in_signature='', out_signature='s')
	def get_modes(self):
		p = subprocess.run(["/usr/bin/bash", mode_setting_script, "get_modes"], capture_output=True)
		print("responding to get_modes with {}".format(p.stdout))
		return p.stdout

	@dbus.service.method(interface_name, in_signature='', out_signature='s')
	def get_config(self):
		print("responding to get_config with {}".format(self.config))
		return self.config

	@dbus.service.method(interface_name, in_signature='', out_signature='s')
	def mode_request(self):
		print("responding to mode_request with {}".format(self.config))
		return self.config

	@dbus.service.method(interface_name, in_signature='s', out_signature='s')
	def set_config(self, config):
		print("setting usb config to {}".format(config))
		self.config = config
		try:
			f = open(config_path, "w")
			f.write(config)
		except:
			return "failed writing {}".format(config_path)
		return "success"

	@dbus.service.signal(dbus_interface=interface_name, signature="s")
	def sig_usb_current_state_ind(self, mode):
		pass

	@dbus.service.method(interface_name, in_signature='s', out_signature='s')
	def set_mode(self, mode):
		print("setting usb mode to {}".format(mode))
		self.set_config(mode)

		p = subprocess.run(["/usr/bin/bash", mode_setting_script, mode], capture_output=True)
		if mode.find("adb") != -1:
			start_adbd()
			pass
		else:
			stop_adbd()
			pass

		self.sig_usb_current_state_ind(mode)

		# TODO? rndis? ut does not seem to support rndis proper at the moment, and is only used for debugging
		return "success"

DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()
name = dbus.service.BusName(service_name, bus)
object = MiniUsbModed(bus, object_path)

print("starting glib loop")
loop = GLib.MainLoop()
loop.run()
