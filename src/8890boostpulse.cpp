#include <string>
#include <cstring>
#include <vector>
#include <iostream>
#include <fstream>

#include <unistd.h>
#include <fcntl.h>
#include <poll.h>
#include <stdlib.h>

// largely based on https://github.com/8890q/android_device_samsung_universal8890-common/tree/lineage-18.1/hardware/power

static const std::vector<std::string> cpuInteractivePaths = {
	"/sys/devices/system/cpu/cpu0/cpufreq/interactive",
	"/sys/devices/system/cpu/cpu4/cpufreq/interactive"
};

static const char *evdevs[] = {
	"/dev/input/by-path/platform-14e10000.hsi2c-event",
	"/dev/input/by-path/platform-gpio_keys-event"
};

static struct pollfd evdev_pfds[sizeof(evdevs) / sizeof(char *)] = {0};
static bool stop_polling = false;

template <typename T>
static void set(const std::string& path, const T& value) {
    std::ofstream file(path);
    file << value << std::endl;
}

#if 0
#define LOG_VERBOSE(msg) log(msg)
#else
#define LOG_VERBOSE(msg)
#endif

#define LOG(msg) log(msg)

static void log(std::string message){
	std::cout << message << std::endl;
}
static void pulse(){
	set(cpuInteractivePaths.front() + "/boostpulse", "1");
}

static void evdev_poller(){
	char buf[512];
	int device;
	while(!stop_polling){
		device = poll(evdev_pfds, sizeof(evdevs) / sizeof(char *), 5000);
		if(device < 0){
			LOG_VERBOSE("evdev poll returned errored");
			continue;
		}
		if(device == 0){
			LOG_VERBOSE("evdev poll timed out");
			continue;
		}
		for(int i = 0; i < sizeof(evdevs) / sizeof(char *); i++){
			if((evdev_pfds[i].revents & POLLIN)){
				LOG_VERBOSE(std::string("event received from ") + evdevs[i]);
				pulse();
				usleep(50000);
				read(evdev_pfds[i].fd, buf, sizeof(buf));
			}
		}
	}
}

static void init(){
	int evdev_fd;
	int devices_opened;

	devices_opened = 0;
	for(int i = 0; i < sizeof(evdevs) / sizeof(char *); i++){
		int evdev_fd = open(evdevs[i], O_RDONLY);
		if(evdev_fd == -1){
			LOG(std::string("failed opening evdev ") + evdevs[i] + " for polling");
			break;
		}
		LOG(std::string("opened evdev ") + evdevs[i] + " for polling");
		evdev_pfds[i].fd = evdev_fd;
		evdev_pfds[i].events = POLLIN;
		devices_opened++;
	}
	if(devices_opened != sizeof(evdevs) / sizeof(char *)){
		LOG("some evdevs failed opening, terminating");
		exit(1);
	}
}

int main(){
        init();
        evdev_poller();
}
