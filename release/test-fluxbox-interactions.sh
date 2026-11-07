#!/bin/sh
set -eu
[ -e /.dockerenv ] || { echo "Disposable test container required" >&2; exit 2; }
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y --no-install-recommends fluxbox xvfb xdotool xterm conky-std x11-utils >/tmp/deps.log 2>&1
mkdir -p /tmp/fb
sed 's|@@CONFIG@@|/tmp/fb|g' /usr/share/daylight/fluxbox/init > /tmp/fb/init
rm -f /tmp/.X91-lock /tmp/.X11-unix/X91
Xvfb :91 -screen 0 1024x768x24 >/tmp/xvfb.log 2>&1 &
export DISPLAY=:91
sleep 1
fluxbox -rc /tmp/fb/init >/tmp/fluxbox.log 2>&1 &
sleep 2
xterm -title DaylightDragTest -geometry 60x20+50+100 >/tmp/xterm.log 2>&1 &
sleep 2
wid=$(xdotool search --name '^DaylightDragTest$' | head -1)
eval "$(xdotool getwindowgeometry --shell "$wid")"
before=$X
Y=$(xwininfo -id "$wid" | awk '/Absolute upper-left Y:/ {print $4}')
xdotool mousemove $((X+100)) $((Y-12)) sleep 0.3 mousedown 1 sleep 0.3 mousemove_relative --sync 10 10 sleep 0.3 mousemove --sync $((X+250)) $((Y+100)) sleep 0.3 mouseup 1
sleep 1
eval "$(xdotool getwindowgeometry --shell "$wid")"
test "$X" -gt "$before"
echo TITLEBAR_DRAG_PASSED
Y=$(xwininfo -id "$wid" | awk '/Absolute upper-left Y:/ {print $4}')
before=$WIDTH
xdotool mousemove $((X+WIDTH-10)) $((Y+HEIGHT-10)) keydown alt mousedown 3 sleep 0.3 mousemove_relative --sync 50 30 sleep 0.3 mouseup 3 keyup alt
sleep 1
eval "$(xdotool getwindowgeometry --shell "$wid")"
test "$WIDTH" -gt "$before"
echo ALT_RESIZE_PASSED
sed 's/@@INTERFACE@@/eth0/g' /usr/share/daylight/conky/balanced.conf >/tmp/conky.conf
mkdir -p /usr/bin
printf '#!/bin/sh\necho unavailable\n' > /usr/bin/daylight
chmod +x /usr/bin/daylight
conky -c /tmp/conky.conf >/tmp/conky.log 2>&1 &
cpid=$!
sleep 3
kill -0 "$cpid"
! grep -qi 'syntax error\|error loading\|parse error' /tmp/conky.log
test -z "$(/usr/bin/daylight sensor | sed '/^unavailable$/d; s/^/ · /')"
echo CONKY_NO_SENSOR_PASSED
cat /tmp/fluxbox.log
