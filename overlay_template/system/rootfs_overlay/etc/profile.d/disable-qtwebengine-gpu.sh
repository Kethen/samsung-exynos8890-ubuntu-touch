#!/bin/sh
# This file was part of lxc-android-config, overriden here
# gpu rasterization seems very usable on this device

# leaving viz disabled according to https://github.com/ubports/lxc-android-config/commit/bf7c2dc380543dc9369f1ce8bb4b478729727636

export QTWEBENGINE_CHROMIUM_FLAGS="--enable-gpu-rasterization --enable-zero-copy --disable-viz-display-compositor"

# uncomment this to just use zero copy instead, which gives a big boost to scrolling framerate as well
#export QTWEBENGINE_CHROMIUM_FLAGS="--enable-zero-copy --disable-viz-display-compositor"

# enable OverlayScrollbar
export QTWEBENGINE_CHROMIUM_FLAGS="$QTWEBENGINE_CHROMIUM_FLAGS --enable-features=OverlayScrollbar"
