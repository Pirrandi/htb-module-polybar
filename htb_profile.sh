#!/bin/bash
eval $(xdotool getmouselocation --shell | grep -E 'X=|Y=')
echo "$X,$Y" >pos.txt

python3 ~/.config/polybar/extra-modules/htb_profile/htb_profile.py
