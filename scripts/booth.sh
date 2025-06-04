#!/bin/bash
set +eux

# disable screensaver / blanking
xset s off
xset -dpms
xset s noblank

# open two chrome windows, wait for them to load the right pages
chromium-browser --new-window --kiosk https://karakara.uk/browser3/ 2>/dev/null &
while ! wmctrl -l | grep -q 'KaraKara Browser' ; do sleep 1 ; done

chromium-browser --new-window --kiosk https://karakara.uk/player3/ 2>/dev/null &
while ! wmctrl -l | grep -q 'KaraKara Player' ; do sleep 1 ; done

# move Browser to touchscreen and Player to external screen
fb_width=$(xwininfo -root | grep Width | cut -d ' ' -f 4)
fb_height=$(xwininfo -root | grep Height | cut -d ' ' -f 4)
for prop in sticky maximized_vert maximized_horz hidden fullscreen;
do
    wmctrl -r $WINDOW_TITLE -b remove,$prop
done
wmctrl -r $WINDOW_TITLE -e 0,0,0,$fb_width,$fb_height
