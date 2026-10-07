#!/bin/sh
sudo env LD_LIBRARY_PATH=/home/ark/device-browser/lib /usr/lib/xorg/Xorg -nocursor "$@" &
server_pid=$!
trap 'kill "$server_pid" 2>/dev/null; wait "$server_pid" 2>/dev/null; exit' INT TERM
# sudo sits between Xorg and xinit, so relay readiness after an authenticated connection.
while kill -0 "$server_pid" 2>/dev/null; do
    if DISPLAY="${1:-:0}" xset q >/dev/null 2>&1; then
        if [ "$(cat /proc/$PPID/comm)" = xinit ]; then kill -USR1 "$PPID"; fi
        break
    fi
    sleep .05
done
wait "$server_pid"
