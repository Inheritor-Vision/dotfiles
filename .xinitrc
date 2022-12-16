#!/bin/sh

userresources=$HOME/.Xresources
usermodmap=$HOME/.Xmodmap
sysresources=/etc/X11/xinit/.Xresources
sysmodmap=/etc/X11/xinit/.Xmodmap

# merge in defaults and keymaps

if [ -f $sysresources ]; then







    xrdb -merge $sysresources

fi

if [ -f $sysmodmap ]; then
    xmodmap $sysmodmap
fi

if [ -f "$userresources" ]; then







    xrdb -merge "$userresources"

fi

if [ -f "$usermodmap" ]; then
    xmodmap "$usermodmap"
fi

# start some nice programs

if [ -d /etc/X11/xinit/xinitrc.d ] ; then
 for f in /etc/X11/xinit/xinitrc.d/?*.sh ; do
  [ -x "$f" ] && . "$f"
 done
 unset f
fi


# CUSTOM
## Configure screens
xrandr --output DP-4 --primary --output HDMI-0 --left-of DP-4

## Swap Caps Lock to Esc
setxkbmap -option caps:swapescape

## Activate numlock on startup
numlockx &

## Start picom 
picom -b

## Change wallpaper, before wallpaper.timer take his turn
feh --randomize --bg-max /mnt/data/Encyclopedia\ Galactica/Division/Art_Graphique/Wallpaper/Ressource/Wallpaper

## Screenshot utility
flameshot &

## Start WM
exec qtile start
