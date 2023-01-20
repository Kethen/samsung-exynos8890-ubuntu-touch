FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update
RUN apt install android-tools-mkbootimg bc bison build-essential ca-certificates cpio curl flex git kmod libssl-dev libtinfo5 python2 sudo unzip wget xz-utils -y --no-install-recommends
RUN apt install -y git img2simg jq sudo wget xz-utils
