#!/bin/sh

# Warning: THIS SCRIPT HAS TO HAVE THE SETUID BIT ? MAYBE. BUT OWNER IS NOT ROOT (pls)

ln -sf /home/vision/.config/wallpaper/wallpaper_service_$1.conf /home/vision/.config/wallpaper/wallpaper_service.conf
sudo systemctl daemon-reload
sudo systemctl start wallpaper.service
