#!/bin/sh

# Wallpaper

ln -sf /home/vision/.config/wallpaper/wallpaper_service_default.conf /home/vision/.config/wallpaper/wallpaper_service.conf

# Spotify

while true
do
	dbus_out=$(dbus-send --print-reply --dest=org.freedesktop.DBus  /org/freedesktop/DBus org.freedesktop.DBus.ListNames)
	sleep 3
	if [[ $dbus_out == *"org.mpris.MediaPlayer2.spotify"* ]]; then
		break
	fi
done


# JAMAIS RIEN VU D AUSSI MYSTIQUE, CA MARCHE PAS SANS LE PRINT REPLY ? ? ? ?? 
dbus-send --print-reply --session --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.OpenUri string:spotify:user:21st4bujrqtj3maqj2z3h35bq:playlist:37i9dQZEVXcHRdx0o4Mjm8 1>/dev/null

# Not working: Spotify DBUS API is DOGSHIT.
# dbus-send --session --dest=org.mpris.MediaPlayer2.spotify --print-reply /org/mpris/MediaPlayer2 org.freedesktop.DBus.Properties.Set string:org.mpris.MediaPlayer2.Player string:Shuffle variant:boolean:true
