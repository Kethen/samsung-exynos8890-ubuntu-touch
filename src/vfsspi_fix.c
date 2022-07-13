#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>

// include/uapi/asm-generic/ioctl.h
#define _IOC_NRBITS	8
#define _IOC_TYPEBITS	8

#define _IOC_SIZEBITS	14

#define _IOC_DIRBITS	2

#define _IOC_NRMASK	((1 << _IOC_NRBITS)-1)
#define _IOC_TYPEMASK	((1 << _IOC_TYPEBITS)-1)
#define _IOC_SIZEMASK	((1 << _IOC_SIZEBITS)-1)
#define _IOC_DIRMASK	((1 << _IOC_DIRBITS)-1)

#define _IOC_NRSHIFT	0
#define _IOC_TYPESHIFT	(_IOC_NRSHIFT+_IOC_NRBITS)
#define _IOC_SIZESHIFT	(_IOC_TYPESHIFT+_IOC_TYPEBITS)
#define _IOC_DIRSHIFT	(_IOC_SIZESHIFT+_IOC_SIZEBITS)

#define _IOC_NONE	0U

#define _IOC_WRITE	1U

#define _IOC_READ	2U

#define _IOC(dir,type,nr,size) \
	(((dir)  << _IOC_DIRSHIFT) | \
	 ((type) << _IOC_TYPESHIFT) | \
	 ((nr)   << _IOC_NRSHIFT) | \
	 ((size) << _IOC_SIZESHIFT))

#define _IOC_TYPECHECK(t) (sizeof(t))

#define _IO(type,nr)		_IOC(_IOC_NONE,(type),(nr),0)
#define _IOR(type,nr,size)	_IOC(_IOC_READ,(type),(nr),(_IOC_TYPECHECK(size)))
#define _IOW(type,nr,size)	_IOC(_IOC_WRITE,(type),(nr),(_IOC_TYPECHECK(size)))
#define _IOWR(type,nr,size)	_IOC(_IOC_READ|_IOC_WRITE,(type),(nr),(_IOC_TYPECHECK(size)))
#define _IOR_BAD(type,nr,size)	_IOC(_IOC_READ,(type),(nr),sizeof(size))
#define _IOW_BAD(type,nr,size)	_IOC(_IOC_WRITE,(type),(nr),sizeof(size))
#define _IOWR_BAD(type,nr,size)	_IOC(_IOC_READ|_IOC_WRITE,(type),(nr),sizeof(size))

#define _IOC_DIR(nr)		(((nr) >> _IOC_DIRSHIFT) & _IOC_DIRMASK)
#define _IOC_TYPE(nr)		(((nr) >> _IOC_TYPESHIFT) & _IOC_TYPEMASK)
#define _IOC_NR(nr)		(((nr) >> _IOC_NRSHIFT) & _IOC_NRMASK)
#define _IOC_SIZE(nr)		(((nr) >> _IOC_SIZESHIFT) & _IOC_SIZEMASK)

#define IOC_IN		(_IOC_WRITE << _IOC_DIRSHIFT)
#define IOC_OUT		(_IOC_READ << _IOC_DIRSHIFT)
#define IOC_INOUT	((_IOC_WRITE|_IOC_READ) << _IOC_DIRSHIFT)
#define IOCSIZE_MASK	(_IOC_SIZEMASK << _IOC_SIZESHIFT)
#define IOCSIZE_SHIFT	(_IOC_SIZESHIFT)

// begins
#define VFSSPI_IOCTL_MAGIC    'k'
#define VFSSPI_IOCTL_SET_INIT_PID     _IOW(VFSSPI_IOCTL_MAGIC, 24, unsigned int)

int main (int argc, char** argv) {
	int input = 0;
	if(argc != 2){
		printf("this program accepts a single pid as argument\n");
		exit(1);
	}
	input = atoi(argv[1]);
	if(input == 0){
		printf("bad input %s\n", argv[1]);
		exit(1);
	}
	int fd = open("/dev/vfsspi", O_WRONLY);
	if(fd == -1){
		printf("failed opening /dev/vfsspi\n");
		exit(1);
	}
	int ret = ioctl(fd, VFSSPI_IOCTL_SET_INIT_PID, &input);
	printf("ioctl return %d\n", ret);
	return 0;
}
