#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <string.h>

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
#define EGIS_IOC_MAGIC          'k'
#define EGIS_MSGSIZE(N) \
    ((((N)*(sizeof(struct egis_ioc_transfer))) < (1 << _IOC_SIZEBITS)) \
        ? ((N)*(sizeof(struct egis_ioc_transfer))) : 0)
#define EGIS_IOC_MESSAGE(N) _IOW(EGIS_IOC_MAGIC, 0, char[EGIS_MSGSIZE(N)])
#define EGIS_CMD EGIS_IOC_MESSAGE(1)
#define FP_SET_INIT_PID                 0x18
struct egis_ioc_transfer {
	char *tx_buf;
	char *rx_buf;
	int len;
	int speed_hz;
	short delay_usecs;
	char bits_per_word;
	char cs_change;
	char opcode;
	char pad[3];
};

int main (int argc, char** argv) {
	struct egis_ioc_transfer data;
	memset(&data, 0, sizeof(data));
	int input = 0;
	data.tx_buf = &input;
	data.opcode = FP_SET_INIT_PID;
	if(argc != 2){
		printf("this program accepts a single pid as argument\n");
		exit(1);
	}
	input = atoi(argv[1]);
	if(input == 0){
		printf("bad input %s\n", argv[1]);
		exit(1);
	}
	int fd = open("/dev/esfp0", O_WRONLY);
	if(fd == -1){
		printf("failed opening /dev/esfp0\n");
		exit(1);
	}
	int ret = ioctl(fd, EGIS_CMD, &data);
	printf("ioctl return %d\n", ret);
	return 0;
}
