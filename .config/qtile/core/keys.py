# Keys
# Keybindings used for qtiles

from core.conf			import (
	KEYBOARD_GROUP_SHORTCUT,
	LIST_WALLPAPER_MODES,
	MOD,
	PATH_ICONS_CACHE,
	PATH_WALLPAPER_SCRIPT,
	SOUND_SINK_NAME
)
from core.groups		import icon, group_names

from libqtile.config 	import Key
from libqtile.lazy		import lazy

import json, os, subprocess


# -------------------------------------| Settings |------------------------------------- #

dgroups_key_binder = None


# ---------------------------------| Wallpaper modes |---------------------------------- #

# Toggle from one wallpaper folder to another
# Backend is simply a systemd task that periodically change the wallpaper.
# Configuration of the service is a symlink to one conf
# When toggled, the symlink point to another conf and relaod the service
def _create_change_wallpaper_mode():
	global _wallpaper_modes
	global _wallpaper_current_mode

	_wallpaper_modes         = LIST_WALLPAPER_MODES
	_wallpaper_current_mode  = 0

	def _change_wallpaper_mode(_):
		global _wallpaper_modes
		global _wallpaper_current_mode
		global PATH_WALLPAPER_SCRIPT
		_wallpaper_current_mode = (_wallpaper_current_mode + 1) % len(_wallpaper_modes)
		subprocess.Popen([PATH_WALLPAPER_SCRIPT, _wallpaper_modes[_wallpaper_current_mode]])

	return _change_wallpaper_mode


# ----------------------------------| Sound Settings |---------------------------------- #

# Pulse Audio daemon can take some time to restart when using lazy.restart(). Quite random
def _get_alsa_index(name):
	sinks  = subprocess.getoutput("pacmd list-sinks | grep -e 'name:' -e 'index:'")\
		.split("\n")
	index = None
	lname = None
	for l in sinks:
		if not isinstance(index,int):
			index = int(l[-1])
		else:
			lname = l.split("<")[1].split(">")[0]
			if name in lname:
				return index
			index = None
	else:
		return -1

_sound_index = str(_get_alsa_index(SOUND_SINK_NAME))

@lazy.function
def _increase_volume(qtile):
	if _sound_index == str(-1):
		_sound_index = str(_get_alsa_index(SOUND_SINK_NAME))
		if _sound_index == str(-1):
			return

	os.system("pactl set-sink-volume " + _sound_index + " +2%")

@lazy.function
def _decrease_volume(qtile):
	# Race condition if qtile is started before pulse audio daemon.
	if _sound_index == str(-1):
		_sound_index = str(_get_alsa_index(SOUND_SINK_NAME))
		if _sound_index == str(-1):
			return

	os.system("pactl set-sink-volume " + _sound_index + " -2%")


@lazy.function
def _mute_volume(qtile):
	# Race condition if qtile is started before pulse audio daemon.
	if _sound_index == str(-1):
		_sound_index = str(_get_alsa_index(SOUND_SINK_NAME))
		if _sound_index == str(-1):
			return

	os.system("pactl set-sink-mute " + _sound_index + " toggle")

# -------------------------------| Random Icons Caching |------------------------------- #

# When restarting, groups are not fully updated (i.e. old groups are not deleted, 
# new are added). As consequence, random generates a new icon that is added to the bar
# and the old ones are not deleted. Hence, on restart, icon must be saved and not 
# re-generated.
@lazy.function
def _restart(qtile, icons = [], path = PATH_ICONS_CACHE):
	with open(path, "w") as f:
		json.dump({"icons" : icons}, f)
	qtile.cmd_restart()


# ---------------------------------| Keys Generation |---------------------------------- #

keys = []

keys += [
	# Switch between windows
	Key([MOD], "h", lazy.layout.left(), desc="Move focus to left"),
	Key([MOD], "l", lazy.layout.right(), desc="Move focus to right"),
	Key([MOD], "j", lazy.layout.down(), desc="Move focus down"),
	Key([MOD], "k", lazy.layout.up(), desc="Move focus up"),
	Key([MOD], "space", lazy.layout.next(),
		desc="Move window focus to other window"),

	# Move windows between left/right columns or move up/down in current stack.
	# Moving out of range in Columns layout will create new column.
	Key([MOD, "shift"], "h", lazy.layout.shuffle_left(),
		desc="Move window to the left"),
	Key([MOD, "shift"], "l", lazy.layout.shuffle_right(),
		desc="Move window to the right"),
	Key([MOD, "shift"], "j", lazy.layout.shuffle_down(),
		desc="Move window down"),
	Key([MOD, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),

	# Toggle Floating of a windows
	# Especially useful to put a windows back in the tiling MODe after a missclick
	Key([MOD], "f", lazy.window.toggle_floating(), desc="Toggle window floating"),

	# Grow windows. If current window is on the edge of screen and direction
	# will be to screen edge - window would shrink.
	Key([MOD, "control"], "h", lazy.layout.grow_left(),
		desc="Grow window to the left"),
	Key([MOD, "control"], "l", lazy.layout.grow_right(),
		desc="Grow window to the right"),
	Key([MOD, "control"], "j", lazy.layout.grow_down(),
		desc="Grow window down"),
	Key([MOD, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),
	Key([MOD], "n", lazy.layout.normalize(), desc="Reset all window sizes"),

	# Change Screen Focus
	Key([MOD], "Left", lazy.prev_screen()),
	Key([MOD], "Right",lazy.next_screen()),

	# Sound Control 
	Key([], "XF86AudioLowerVolume", lazy.spawn(
		"pactl set-sink-volume " + _sound_index + " -5%")
	),
	Key([], "XF86AudioRaiseVolume", lazy.spawn(
		"pactl set-sink-volume " + _sound_index + " +5%")
	),
	Key([], "XF86AudioMute", lazy.spawn(
		"pactl set-sink-mute " + _sound_index + " toggle")
	),

	# Track Control, attribuated to Spotify
	Key([], "XF86AudioPrev", lazy.spawn(
		"dbus-send --dest=org.mpris.MediaPlayer2.spotify --print-reply "
		"/org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.Previous")
	),
	Key([], "XF86AudioPlay", lazy.spawn(
		"dbus-send --dest=org.mpris.MediaPlayer2.spotify --print-reply "
		"/org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.PlayPause")
	),
	Key([], "XF86AudioNext", lazy.spawn(
		"dbus-send --dest=org.mpris.MediaPlayer2.spotify --print-reply "
		"/org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.Next")
	),

	# Change Wallpaper mode
	Key([MOD], "x", 
		lazy.function( _create_change_wallpaper_mode()),
		desc= "Change wallpaper mode"
	),

	# App lauch
	Key([MOD], "Return", 
		lazy.spawn("/bin/bash -c "
			+ os.path.expanduser("~/.config/qtile/spawn-alacritty-cwd.sh")
		),
		desc="Launch terminal with cwd set to focused terminal"),
	Key([], "Print", 
		lazy.spawn("flameshot gui"), 
		desc="Screenshot with Flameshot utility"
	),

	# Toggle between different layouts as defined below
	Key([MOD], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
	Key([MOD], "w", lazy.window.kill(), desc="Kill focused window"),

	# Restat, Quit and Execute
	Key([MOD, "control"], "r", _restart([icon]), desc="Restart Qtile"),
	Key([MOD, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
	Key([MOD], "r", lazy.spawn("rofi -show drun"),
		desc="Spawn a command using a prompt widget"),
]

for i, (name, kwargs) in enumerate(group_names, 1):
		# Switch to another group.
		keys.append(Key([MOD], 
			KEYBOARD_GROUP_SHORTCUT[i], 
			lazy.group[name].toscreen(toggle=True))
		)
		# Send current window to another group
		keys.append(Key([MOD, "shift"], 
			KEYBOARD_GROUP_SHORTCUT[i], 
			lazy.window.togroup(name))
		)

# ---------------------------------| Key Mapping Test |--------------------------------- #

# def debug_func(qtile, *args, **kwargs):
#  logger.warning("[DEBUG2_VISION] Key pushed: " + str(args[0])) 

# a = ['Shift_R','Menu','ISO_Level3_Shift','F2','F1','Alt_L','Shift_L','Control_L']
# for k in a:
#   keys += [Key([], k, lazy.function(debug_func, [str(k)], {}))]

# Key mapping of Kb CORSAIR Silent:
# Fn + F5 = XF86AudioMute
# Fn + F7 = XF86AudioLowerVolume
# Fn + F8 = XF86AudioRaiseVolume
# Fn + F9 = XF86AudioStop
# Fn + F10 = XF86AudioPrev
# Fn + F11 = XF86AudioPlay
# Fn + F12 = XF86AudioNext
# Impr Ecr = "Print"
# Arret Defil = "Scroll_Lock"
# Pause Attn = "Pause"
# ² = "twosuperior"
# Inser = "Insert"
# Debut = "Home"
# Page up = "Page_Up"
# Page down = "Page_Down"
# Fin = "End"
# Suppr = "Delete"
# Num pad deactivated + keys  => Same but prefix "KP_" like "KP_Home"
# Shift R = "Shit_R"
# FN = "ISO_Level3_Shift"
# CTRL R same as CTRL L
# Menu = "Menu"
