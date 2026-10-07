#!/bin/bash
set -eu
export XDG_RUNTIME_DIR=/run/user/$(id -u)
mkdir -p "$XDG_RUNTIME_DIR"
startx /home/ark/device-browser/client.sh -- /home/ark/device-browser/xserver.sh \
    :0 vt2 -config /home/ark/device-browser/xorg.conf -nolisten tcp \
    -logfile /home/ark/device-browser/Xorg.log >>/home/ark/device-browser/launch.log 2>&1
