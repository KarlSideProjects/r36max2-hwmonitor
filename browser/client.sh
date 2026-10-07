#!/bin/bash
set -eu
cd /home/ark/device-browser
export LD_LIBRARY_PATH=/home/ark/device-browser/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
xset s off
xset s noblank
xset +dpms
xset dpms 0 0 0
python3 "${1:-device_info.py}" >>/home/ark/device-browser/page.log 2>&1 &
page_pid=$!
browser_pid=
cleanup() {
    kill "$page_pid" ${browser_pid:+"$browser_pid"} 2>/dev/null || true
    wait 2>/dev/null || true
}
trap cleanup EXIT
trap 'exit 0' INT TERM
chromium --disable-gpu --no-first-run --no-default-browser-check --disable-sync \
    --user-data-dir=/home/ark/.config/device-browser --kiosk \
    --window-position=0,0 --window-size=1024,768 "http://127.0.0.1:${2:-8765}" >>/home/ark/device-browser/chromium.log 2>&1 &
browser_pid=$!
while kill -0 "$page_pid" 2>/dev/null && kill -0 "$browser_pid" 2>/dev/null; do sleep 1; done
