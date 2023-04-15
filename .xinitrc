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
screen_setup_9bf624c60be9dca4fe9379f01da90d905667d8b2

## Swap Caps Lock to Esc
keyboard_setup_9bf624c60be9dca4fe9379f01da90d905667d8b2

## Activate numlock on startup
numlock_9bf624c60be9dca4fe9379f01da90d905667d8b2

## Start picom 
picom -b

## Change wallpaper, before wallpaper.timer take his turn
wallpaper_9bf624c60be9dca4fe9379f01da90d905667d8b2

## Screenshot utility
screenshot_util_9bf624c60be9dca4fe9379f01da90d905667d8b2

## Minefield text cycle
grub_theme_cycle_9bf624c60be9dca4fe9379f01da90d905667d8b2

## Start WM
exec qtile start
