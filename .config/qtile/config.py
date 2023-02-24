from typing import List  

from core.widget.custom_groupbox import CustomGroupBox
from core.widget.custom_textbox import CustomTextBox

from qtile_extras import widget
from qtile_extras.widget import modify
from qtile_extras.widget.decorations import RectDecoration, PowerLineDecoration
from libqtile import bar, layout, hook
from libqtile.backend.x11.xkeysyms import keysyms
from libqtile.bar import CALCULATED
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy
from libqtile.log_utils import logger


import os, socket, subprocess, requests, psutil, random, re

# ----- ALIAS ----- #
alt = "mod1"
mod = "mod4"
terminal = "alacritty" 
font = "FiraCode Nerd Font" # Do not use Mono. Because icons will appears as too small.

available_screens = {
	"primary": "DP-4",
	"secondary": "HDMI-0"
}

sound_output = "alsa_output.usb-Logitech_PRO_X_000000000000-00.analog-stereo"
sound_index = None

wlan_interface = "wlp5s0"

azerty_group_patch = {1:"ampersand", 2:"eacute", 3:"quotedbl", 4:"apostrophe", 5:"parenleft", 6:"minus", 7:"egrave", 8:"underscore", 9:"ccedilla", 10:"agrave"}

colors = {
	"white"			: "#d3d7cf",
	"light_white"	: "#e5e9f0",
	"black"			: "#242831",
	"light_black"	: "#2e3436",
	"red"			: "#ef2929",
	"light_red"		: "#bf616a",
	"blue"		 	: "#3465a4",	
	"light_blue"	: "#81a1c1",	
	"cyan" 			: "#f57900",	
	"light_cyan"	: "#fcaf3e",	
	"green"			: "#8ae234",
	"light_green"	: "#a3be8c",
	"yellow"		: "#edd400",
	"light_yellow"	: "#ebcb8b",
	"magenta"		: "#75507b",
	"light_magenta" : "#b48ead",
	"transparent"	: "#00000000"
}

ENCYCLOPEDIA_PATH = '/mnt/data/Encyclopedia\ Galactica/'

# https://github.com/ryanoasis/nerd-fonts/wiki/Glyph-Sets-and-Code-Points
DICT_FIRA_CODE_POINT = {
		"Custom_Seti-UI":       (0xe5fa, 0xe62b),
		"Devicons":             (0xe700, 0xe7c5),
		"Awesome":              (0xf000, 0xf2e0),
		"Material_Design":      (0xf500, 0xfd46),
		"Weather":              (0xe300, 0xe3eb),
		"Octicons":             (0xf400, 0xf4a8),
		"Powerline":            (0xe0b4, 0xe0c8),
		"Powerline2":           (0xe0cc, 0xe0d2),
		"IEC_Power_Symbols":    (0x23fb, 0x23fe),
		"Font_Linux":           (0xf300, 0xf313),
		"Pomicons":             (0xe000, 0xe00d)
}

# ----- Utils ----- #

def rd_icon():
	family = random.choices([a for a in DICT_FIRA_CODE_POINT.keys()], [((maxi - mini + 0x4) / 0x4) for (mini,maxi) in DICT_FIRA_CODE_POINT.values()])
	(mini, maxi) = DICT_FIRA_CODE_POINT[family[0]]
	return chr(random.randrange(mini, maxi + 0x4, 0x4))

icon = rd_icon()

# For apps with indirection and/or that implements poorly X11 and/or have multiple pids (& fucks with X11 rules)
# See async wait in qtile https://github.com/qtile/qtile/pull/2063
# See example of uncatchable apps (Spotify, that now is catchable tbf) https://github.com/qtile/qtile/issues/1915
# Debug hook: https://gist.github.com/ramnes/2feecfa7aecf7260dd7b65f7cb995c31
# Workaround: https://groups.google.com/g/qtile-dev/c/DYVYuAzYbG4/m/R8IWR-hfAgAJ
# Window page: https://github.com/qtile/qtile/blob/0c049edd96069a7030c4895e9832711c07bb0bfa/libqtile/backend/base.py
# Window.window (set_property?): https://github.com/qtile/qtile/blob/0c049edd96069a7030c4895e9832711c07bb0bfa/libqtile/backend/x11/window.py

dict_sketchy_apps_once  = {"VSCodium": ""}
dict_match              = {re.compile(".* - Oracle VM VirtualBox : 2.*"): icon, re.compile(".* - Oracle VM VirtualBox : 1.*"): ""}

@hook.subscribe.client_new
def catch_sketchy_apps_once(window):
	# logger.warning("NAME: " + window.window.get_name())
	# if re.match(".* - Oracle VM VirtualBox : 1.*", window.window.get_name()):
	#     logger.warning("FOUND IT")
	a = window.window.get_name()

	if type(a) != str:
		if type(a) == None:
			return
		else:
			logger.warning("[LOG] window.get_name(): " + str(a))
			logger.warning("[LOG] window.get_name(): " + str(type(a)))
			return


	if dict_sketchy_apps_once:
		if a in dict_sketchy_apps_once:
			window.cmd_togroup(dict_sketchy_apps_once[a])
			dict_sketchy_apps_once.pop(a)

	for pattern, group in dict_match.items():
		if pattern.match(a):
			window.cmd_togroup(group)
			break
		


# ----- Wallpaper ----- #
def create_change_wallpaper_mode():
	global wallpaper_modes
	global wallpaper_current_mode

	wallpaper_modes         = ["default", "real"]
	wallpaper_current_mode  = 0

	def change_wallpaper_mode(qtile):
		global wallpaper_modes
		global wallpaper_current_mode
		wallpaper_current_mode = (wallpaper_current_mode + 1) % len(wallpaper_modes)
		subprocess.Popen([os.path.expanduser("~/.config/wallpaper/script.sh"), wallpaper_modes[wallpaper_current_mode]])
	return change_wallpaper_mode


# ----- AutoStart ----- #

@hook.subscribe.startup_once
def autostart():
	subprocess.Popen(["/bin/sh", os.path.expanduser("~/.config/qtile/autostart.sh")])

# ----- CHECK NETWORK STATUS ----- #

# Interfaces names, see: https://www.freedesktop.org/wiki/Software/systemd/PredictableNetworkInterfaceNames
def check_interface(interface):
	interface_addrs = psutil.net_if_addrs().get(interface) or []
	return socket.AF_INET in [snicaddr.family for snicaddr in interface_addrs]

def icon_check_wifi():
	wifi_interfaces = [i for i in psutil.net_if_addrs().keys() if "wlp" in i and check_interface(i)]
	return '<span foreground="' + colors["magenta"] + '">直</span>' if wifi_interfaces else '<span foreground="' + colors["light_red"] + '">睊</span>'


def icon_check_ethernet():
	eth_interfaces = [i for i in psutil.net_if_addrs().keys() if "enp" in i and check_interface(i)]
	return '<span foreground="' + colors["magenta"] + '"></span>' if eth_interfaces else  '<span foreground="' + colors["light_red"] + '"></span>'
	
# ----- VPN ----- #

def icon_check_vpn():
	return '<span foreground="' + colors["magenta"] + '">嬨</span>' if not subprocess.run(["systemctl", "is-active", "--quiet", "openvpn@vpn.service"]).returncode else  '<span foreground="' + colors["light_red"] + '">嬨</span>'

# ----- XMR ----- #

def crypto_value(crypto):
	raw_price = requests.get("https://eur.rate.sx/1"+crypto).content.decode("utf-8").split(".")
	return '<span foreground="' + colors["cyan"] + '">' + raw_price[0] + "." + raw_price[1][:2] + '€</span>'
	
def xmr_value(): return crypto_value("xmr")

# ----- SOUND ----- #

def get_alsa_index(name):
	sinks  = subprocess.getoutput("pacmd list-sinks | grep -e 'name:' -e 'index:'").split("\n")
	index = None
	lname = None
	for l in sinks:
		if not isinstance(index,int):
			index = int(l[-1])
		else:
			lname = l.split("<")[1].split(">")[0]
			if lname == name:
				return index
			index = None
	else:
		return -1

sound_index = str(get_alsa_index(sound_output))

# ----- KEYS ----- #

keys = []

keys += [
	# Switch between windows
	Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
	Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
	Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
	Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
	Key([mod], "space", lazy.layout.next(),
		desc="Move window focus to other window"),

	# Move windows between left/right columns or move up/down in current stack.
	# Moving out of range in Columns layout will create new column.
	Key([mod, "shift"], "h", lazy.layout.shuffle_left(),
		desc="Move window to the left"),
	Key([mod, "shift"], "l", lazy.layout.shuffle_right(),
		desc="Move window to the right"),
	Key([mod, "shift"], "j", lazy.layout.shuffle_down(),
		desc="Move window down"),
	Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),

	# Toggle Floating of a windows
	# Especially useful to put a windows back in the tiling mode after a missclick
	Key([mod], "f", lazy.window.toggle_floating(), desc="Toggle window floating"),

	# Grow windows. If current window is on the edge of screen and direction
	# will be to screen edge - window would shrink.
	Key([mod, "control"], "h", lazy.layout.grow_left(),
		desc="Grow window to the left"),
	Key([mod, "control"], "l", lazy.layout.grow_right(),
		desc="Grow window to the right"),
	Key([mod, "control"], "j", lazy.layout.grow_down(),
		desc="Grow window down"),
	Key([mod, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),
	Key([mod], "n", lazy.layout.normalize(), desc="Reset all window sizes"),

	# Change Screen Focus
	Key([mod], "Left", lazy.prev_screen()),
	Key([mod], "Right",lazy.next_screen()),

	# Sound Control 
	Key([], "XF86AudioLowerVolume", lazy.spawn("pactl set-sink-volume " + sound_index + " -5%")),
	Key([], "XF86AudioRaiseVolume", lazy.spawn("pactl set-sink-volume " + sound_index + " +5%")),
	Key([], "XF86AudioMute", lazy.spawn("pactl set-sink-mute " + sound_index + " toggle")),

	# Track Control, attribuated to Spotify
	Key([], "XF86AudioPrev", lazy.spawn("dbus-send --dest=org.mpris.MediaPlayer2.spotify --print-reply /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.Previous")),
	Key([], "XF86AudioPlay", lazy.spawn("dbus-send --dest=org.mpris.MediaPlayer2.spotify --print-reply /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.PlayPause")),
	Key([], "XF86AudioNext", lazy.spawn("dbus-send --dest=org.mpris.MediaPlayer2.spotify --print-reply /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.Next")),

	# Change Wallpaper Mode
	Key([mod], "x", lazy.function(create_change_wallpaper_mode()), desc= "Change wallpaper mode"),

	# App lauch
	Key([mod], "Return", lazy.spawn("/bin/bash -c " + os.path.expanduser("~/.config/qtile/spawn-alacritty-cwd.sh")), desc="Launch terminal with cwd set to focused terminal"),
	Key([], "Print", lazy.spawn("flameshot gui"), desc="Screenshot with Flameshot utility"),

	# Toggle between different layouts as defined below
	Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
	Key([mod], "w", lazy.window.kill(), desc="Kill focused window"),

	# Restat, Quit and Execute
	Key([mod, "control"], "r", lazy.restart(), desc="Restart Qtile"),
	Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
	Key([mod], "r", lazy.spawn("rofi -show drun"),
		desc="Spawn a command using a prompt widget"),
]

# ----- GROUPS ----- #

def init_group_names():
	return [
			("", {'layout':'monadtall'}),
			("", {'layout':'max',        'spawn': 'brave'}),
			("", {'layout':'monadtall'}),
			#(icon, {'layout':'monadtall', "matches": [Match(title=[re.compile(".* - Oracle VM VirtualBox : 2.*")])]}),
			("a", {'layout':'monadtall', "matches": [Match(title=[re.compile(".* - Oracle VM VirtualBox : 2.*")])]}),
			("󰍺", {'layout':'max',        'spawn': 'virtualbox', "matches": [Match(title=[re.compile(".* - Oracle VM VirtualBox : 1.*")])]}),
			("󱅰", {'layout':'treetab',    'spawn': ["discord", 'signal-desktop']}),
			("", {'layout':'monadtall',  'spawn': 'spotify'}),
			("󰒍", {'layout':'monadtall'}),
			("", {'layout':'monadtall',  'spawn': 'vscodium ' + ENCYCLOPEDIA_PATH + '/.vscode/Enc_Gal.code-workspace', "matches": [Match(title= [re.compile(".*Enc_Gal (Workspace).*")] )]})]

group_names = init_group_names()
groups = [Group(name, **kwargs) for name, kwargs in group_names]

for i, (name, kwargs) in enumerate(group_names, 1):
		keys.append(Key([mod], azerty_group_patch[i], lazy.group[name].toscreen(toggle=True)))       	# Switch to another group.
		keys.append(Key([mod, "shift"], azerty_group_patch[i], lazy.window.togroup(name))) 				# Send current window to another group


# ----- LAYOUTS ----- #

layout_theme = {
		"border_width": 2,
		"margin": 20,
		"border_focus": "e1acff",
		"border_normal": "1D2330"
}

layouts = [
	layout.Max(**layout_theme),
	layout.MonadTall(**layout_theme, ratio = 0.6),
	layout.TreeTab(
		font = font,
		fontsize = 11,
		sections = ["Tab"],
		border_width = 2, 
		bg_color = "1c1f24",
		active_bg = "c678dd",
		active_fg = "000000",
		inactive_bg = "a9a1e1",
		inactive_fg = "1c1f24",
		padding_left = 0,
		padding_x = 0,
		padding_y = 5,
		section_top = 10,
		section_bottom = 20,
		level_shift = 8,
		vspace = 3,
		panel_width = 200
	),
	layout.Floating(**layout_theme),
	layout.Zoomy(**layout_theme)
]

widget_defaults = dict(
	font		= font,
	fontsize	= 15,
	# padding		= 3,
	# background 	= colors["light_black"],
	# decorations = [
	# 	BorderDecoration(
	# 		colour=colors["light_black"],
	# 		border_width = [11,0,10,0]
	# 	)
	# ]
)

extension_defaults = widget_defaults.copy()

# ----- Bar ----- #

def get_current_volume():
	volume = subprocess.getoutput("pacmd list-sinks | grep volume:\ front | awk '{i++} i==2{print $5+0}'")
	muted  = subprocess.getoutput("pacmd list-sinks | grep muted | awk '{i++} i==2{print $2}'")
	if(volume == ""):
		return "N/A"
	else:
		if(muted == "yes"):
			return "M"
		else:
			return volume + "%"

def get_kb_layout():
	kb_layout = subprocess.getoutput("setxkbmap -query | grep layout | awk '{print $2}'")
	return kb_layout

def init_widgets_list():
	widgets_list = [
		widget.Spacer(
			length = 2
		),

		modify(
			CustomTextBox,
			background 	= colors["light_blue"],
			foreground 	= colors["light_black"],
			decorations = [ 
				RectDecoration(
					filled = True,
					radius = 10,
					use_widget_background = True
				)
			],
			font = font,
			fontsize = 16,
			# mouse_callbacks = {
			# 	"Button1": lazy.restart()
			# },
			offset = 4,
			padding = 20,
			text = ""
		),

		CustomTextBox(
			background = None,
			foreground = colors["light_white"],
			font = font,
			fontsize = 16,
			offset = -8,
			padding = 8,
			text = "󰇙"
		),

		CustomGroupBox(
			font = font,
			fontsize = 17,
			background = None,
			borderwidth = 1,
			colors = [
				colors["red"], colors["light_red"], colors["yellow"], colors["light_green"], colors["green"], colors["light_blue"], colors["blue"], colors["cyan"], colors["light_magenta"], colors["magenta"]
			],
			highlight_color = colors["light_black"],
			highlight_method = "line",
			inactive = colors["light_white"],
			invert = True,
			padding = 7,
			rainbox = True
		),

		CustomTextBox(
			background = None,
			foreground = colors["light_white"],
			font = font,
			fontsize = 16,
			offset = 4,
			padding = 4,
			text = "󰇙"
		),

		modify(
			CustomTextBox,
			background 	= colors["light_magenta"],
			foreground = colors["light_black"],
			decorations = [ 
				RectDecoration(
					filled = True,
					radius = [10, 0, 0, 10],
					use_widget_background = True
				)
			],
			font = font,
			fontsize = 16,
			text = "󰋋",
			x = 4
		),

		modify(
			widget.PulseVolume,
			foreground = colors["light_black"],
			background = colors["light_magenta"],
			font = font,
			fontsize = 13,
			decorations = [
				PowerLineDecoration(
					path = "arrow_right",
					size = 11
				)
			],
			update_interval = 0.2,
			device = sound_output,
			width = bar.CALCULATED,
			padding = 3,
			fmt = " {} "
		),


		modify(
			CustomTextBox,
			foreground = colors["light_black"],
			background = colors["light_red"],
			font = font,
			fontsize = 13,
			offset = -1,
			text = "",
			x = -5
		),

		modify(
			widget.CheckUpdates,
			foreground = colors["light_black"],
			background = colors["light_red"],
			font = font,
			fontsize = 13,
			decorations = [
				RectDecoration(
					filled = True,
					radius = [0, 10, 10, 0],
					use_widget_background = True
				)
			],
			colour_have_updates = colors["light_black"],
			colour_no_updates = colors["light_black"],
			display_format = "{updates} updates  ",
			distro = "Arch_checkupdates",
			initial_text = "No update  ",
			no_update_string = "No update  ",
			padding = 0,
			update_interval = 3600,
		),

		widget.Spacer(),

		widget.WindowName(
			foreground = colors["light_white"],
			background = None,
			font = font,
			fontsize = 13,
			max_chars = 60,
			format = "{name}",
			width = CALCULATED
		),

		widget.Spacer(),

		modify(
			CustomTextBox,
			foreground = colors["light_black"],
			background = colors["light_green"],
			decorations = [
				RectDecoration(
					filled = True,
					radius = [10, 0, 0, 10],
					use_widget_background = True
				)
			],
			font = font,
			fontsize = 16,
			offset = 3,
			text = "󰻠",
			x = 5
		),

		widget.CPU(
			foreground = colors["light_black"],
			background = colors["light_green"],
			font = font,
			fontsize = 13,
			decorations = [
				PowerLineDecoration(
					path = "arrow_right",
					size = 11
				)
			],
			format = "{load_percent: 3.0f}%"
		),

		CustomTextBox(
			foreground = colors["light_black"],
			background = colors["light_yellow"],
			font = font,
			fontsize = 16,
			offset = -2,
			padding = 5,
			text = "󰍛",
			x = -2
		),

		widget.Memory(
			foreground = colors["light_black"],
			background = colors["light_yellow"],
			font = font,
			fontsize = 13,
			decorations = [
				PowerLineDecoration(
					path = "arrow_right",
					size = 11
				)
			],
			format = "{MemUsed: 2.1f}{mm} ",
			padding = -1,
			measure_mem = "G"
		),

		CustomTextBox(
			foreground = colors["light_black"],
			background = colors["light_cyan"],
			font = font,
			fontsize = 13,
			offset = -1,
			text = "󰋊",
			x = -5
		),

		widget.DF(
			foreground = colors["light_black"],
			background = colors["light_cyan"],
			font = font,
			fontsize = 13,
			decorations = [
				RectDecoration(
					filled = True,
					radius = [0, 10, 10, 0],
					use_widget_background = True
				)
			],
			format = "{f: 3.0f}GB ",
			padding = 0,
			partition = "/",
			visible_on_warn = False,
			warn_color = colors["light_cyan"]
		),

		CustomTextBox(
			background = None,
			foreground = colors["light_white"],
			font = font,
			fontsize = 16,
			padding = 8,
			text = "󰇙"
		),

		modify(
			CustomTextBox,
			foreground = colors["light_black"],
			background = colors["light_magenta"],
			decorations = [
				RectDecoration(
					filled = True,
					radius = [10, 0, 0, 10],
					use_widget_background = True
				)
			],
			font = font,
			fontsize = 16,
			offset = 2,
			text = "󰥔",
			x = 4
		),

		modify(
			widget.Clock,
			foreground = colors["light_black"],
			background = colors["light_magenta"],
			decorations = [
				RectDecoration(
					filled = True,
					radius = [0, 10, 10, 0],
					use_widget_background = True
				)
			],
			font = font,
			fontsize = 13,
			format = "%d %b %Y - %H:%M",
			padding = 6
		),

		widget.Spacer(
			length = 2
		)

		# widget.Image(
		# 	filename = "~/.config/qtile/DATA/icons/Inheritor_logo.png",
		# 	margin = 2,
		# 	margin_x = 5
		# ),

		# widget.GroupBox(
		# 	**group_box_parameters
		# ),

		# widget.Prompt(
		#     prompt = "{0}@{1}: ".format(os.environ["USER"], socket.gethostname()),
		#     font = font,
		#     padding = 10,
		#     foreground = colors["light_red"],
		#     background = colors["light_grey"]
		# ),

		# widget.WindowName(
		# 	foreground = colors["magenta"]
		# ),

		# widget.Image(
		# 	filename    = "~/.config/qtile/DATA/icons/monero-logo.png",
		# 	margin      = 7,
		# 	margin_x    = 3,
		# ),
		
		# widget.GenPollText(
		# 		func    = xmr_value,
		# 		update_interval = 600
		# ),

		# widget.TextBox(
		# 	text = "",
		# 	fontsize = RIGHT_ICON_SIZE
		# ),

		# widget.PulseVolume(
		# 	device = sound_output
		# ),

		# widget.Sep(
		# 		linewidth = 1,
		# 		padding = 10,
		# 		foreground = colors["white"],
		# 		background = colors["light_black"]
		# ),

		# widget.GenPollText(
		# 		func = icon_check_wifi,
		# 		update_interval = 1,
		# 		fontsize = RIGHT_ICON_SIZE
		# ),

		# widget.GenPollText(
		# 		func = icon_check_ethernet,
		# 		update_interval = 1,
		# 		fontsize = RIGHT_ICON_SIZE
		# ),

		# widget.GenPollText(
		# 		func = icon_check_vpn,
		# 		update_interval = 1,
		# 		fontsize = RIGHT_ICON_SIZE
		# ),

		# widget.Sep(
		# 		linewidth = 1,
		# 		padding = 10,
		# 		foreground = colors["white"],
		# 		background = colors["light_black"]
		# ),

		# widget.Clock(
		# 	format='%H:%M:%S' # %S for adding seconds
		# ),

		# widget.CurrentLayoutIcon(
		# 	custom_icon_paths = [os.path.expanduser("~/.config/qtile/DATA/icons")],
		# 	background = colors["light_black"],
		# 	padding = 0,
		# 	scale = 0.5
		# ),
	]
	return widgets_list



# ----- Screens ----- #

def init_widgets_screen1():
	widgets_screen1 = init_widgets_list() # Slicing removes unwanted widgets on Monitors 1,3
	return widgets_screen1

def init_widgets_screen2():
	widgets_screen2 = init_widgets_list()
	return widgets_screen2

def init_screens():
	return [Screen(top=bar.Bar(widgets=init_widgets_screen1(), size=22, background=colors["light_black"], border_color=colors["light_black"], margin=[10,10,0,10], border_width=4, opacity = 1)),
			Screen(top=bar.Bar(widgets=init_widgets_screen1(), size=22, background=colors["light_black"], border_color=colors["light_black"], margin=[10,10,0,10], border_width=4, opacity = 1))]



if __name__ in ["config", "__main__"]:
	screens = init_screens()

# Drag floating layouts.
mouse = [
	Drag([mod], "Button1", lazy.window.set_position_floating(),
		 start=lazy.window.get_position()),
	Drag([mod], "Button3", lazy.window.set_size_floating(),
		 start=lazy.window.get_size()),
	Click([mod], "Button2", lazy.window.bring_to_front())
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: List
main = None  # WARNING: this is deprecated and will be removed soon
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(float_rules=[
	# Run the utility of `xprop` to see the wm class and name of an X client.
	*layout.Floating.default_float_rules,
	Match(wm_class='confirmreset'),  # gitk
	Match(wm_class='makebranch'),  # gitk
	Match(wm_class='maketag'),  # gitk
	Match(wm_class='ssh-askpass'),  # ssh-askpass
	Match(title='branchdialog'),  # gitk
	Match(title='pinentry'),  # GPG key password entry
])
auto_fullscreen = True
focus_on_window_activation = "smart"

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"

# ---- KEY MAPPING TEST ----
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
# Me嬨nu = "Menu"
