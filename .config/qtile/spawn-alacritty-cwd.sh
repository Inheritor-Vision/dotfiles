#!/bin/bash

# Credits: [Github-jwilm](https://github.com/alacritty/alacritty/issues/808#issuecomment-334200570)
# Dependencies: xprop (xorg) & xdotool
# Works with compliant apps (terminals mostly) => can be extended for others terminals or supporting apps. 

ACTIVE_WINDOW=$(xdotool getactivewindow)
ACTIVE_WM_CLASS=$(xprop -id $ACTIVE_WINDOW | grep WM_CLASS)

if [[ $ACTIVE_WM_CLASS == *"Alacritty"* ]]
then
	PID=$(xprop -id $ACTIVE_WINDOW | grep _NET_WM_PID | grep -oP "\d+")
	if [[ "$PID" == "" ]]
	then
		alacritty
	fi

	# First child should be the shell
	CHILD_PID=$(pgrep -P $PID)
	if [[ "$PID" == "" ]]
	then
		alacritty
	fi

	pushd "/proc/${CHILD_PID}/cwd"
	SHELL_CWD=$(pwd -P)
	popd
	alacritty --working-directory $SHELL_CWD

else
	alacritty
fi

