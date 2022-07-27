#include <sys/reboot.h>
#include <linux/reboot.h>
#include <sys/syscall.h>
#include <unistd.h>

int main(){
	syscall(__NR_reboot, LINUX_REBOOT_MAGIC1, LINUX_REBOOT_MAGIC2, LINUX_REBOOT_CMD_RESTART2, "recovery");
	return 0;
}
