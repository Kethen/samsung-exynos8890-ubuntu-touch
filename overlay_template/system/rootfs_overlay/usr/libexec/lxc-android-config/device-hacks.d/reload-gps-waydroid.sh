echo restarting gnss service to make sure that it is registered for waydroid

setprop ctl.stop sec_gnss_service
setprop ctl.start sec_gnss_service
