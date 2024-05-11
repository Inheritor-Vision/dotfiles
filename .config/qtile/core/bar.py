# Bar
# Creation of the top bar

from core.conf							import (
	colors,
	FONT,
	PATH_LAYOUT_ICONS
)
from core.widget.custom_groupbox 		import CustomGroupBox
from core.widget.custom_textbox 		import CustomTextBox
from core.widget.custom_image 			import CustomImage

from qtile_extras						import widget
from qtile_extras.widget				import modify
from qtile_extras.widget.decorations	import RectDecoration, PowerLineDecoration
from libqtile.bar						import CALCULATED

import psutil, requests, socket, subprocess

# -----------------------------| [LEGACY] Network status |------------------------------ #

# Interfaces names, see:
# https://www.freedesktop.org/wiki/Software/systemd/PredictableNetworkInterfaceNames
def _check_interface(interface):
	interface_addrs = psutil.net_if_addrs().get(interface) or []
	return socket.AF_INET in [snicaddr.family for snicaddr in interface_addrs]

def _icon_check_wifi():
	wifi_interfaces = [i for i in psutil.net_if_addrs().keys() \
		if "wlp" in i and _check_interface(i)]
	return '<span foreground="' + colors["magenta"] + '">直</span>' \
		if wifi_interfaces else '<span foreground="' + colors["light_red"] + '">睊</span>'


def _icon_check_ethernet():
	eth_interfaces = [i for i in psutil.net_if_addrs().keys() \
		if "enp" in i and _check_interface(i)]
	return '<span foreground="' + colors["magenta"] + '"></span>' \
		if eth_interfaces else  '<span foreground="' + colors["light_red"] + '"></span>'

def _icon_check_vpn():
	return '<span foreground="' + colors["magenta"] + '">嬨</span>' \
		if not subprocess.run([
			"systemctl",
			"is-active",
			"--quiet",
			"openvpn@vpn.service"]
		).returncode else  '<span foreground="' + colors["light_red"] + '">嬨</span>'


# -------------------------------| [LEGACY] XMR Ticker |-------------------------------- #

def _crypto_value(crypto):
	raw_price = requests.get("https://eur.rate.sx/1"+crypto).content.decode("utf-8")\
		.split(".")
	return '<span foreground="' + colors["cyan"] + '">' + raw_price[0] + "." \
		+ raw_price[1][:2] + '€</span>'

def _xmr_value(): return _crypto_value("xmr")


# -----------------------------| [LEGACY] Volume Display |------------------------------ #

def _get_current_volume():
	volume = subprocess.getoutput(
		"pacmd list-sinks "
		"| grep volume:\ front | awk '{i++} i==2{print $5+0}'"
	)
	muted  = subprocess.getoutput(
		"pacmd list-sinks "
		"| grep muted | awk '{i++} i==2{print $2}'"
	)
	if(volume == ""):
		return "N/A"
	else:
		if(muted == "yes"):
			return "M"
		else:
			return volume + "%"


# -------------------------| [LEGACY] Keyboard Layout Display |------------------------- #

def _get_kb_layout():
	kb_layout = subprocess.getoutput("setxkbmap -query | grep layout | awk '{print $2}'")
	return kb_layout


# -------------------------------| Qtile Widget Default |------------------------------- #

widget_defaults = dict(
	font		= FONT,
	fontsize	= 15,
)

extension_defaults = widget_defaults.copy()


# -----------------------------------| Bar Widgets  |----------------------------------- #

def _init_widgets_list():
	widgets_list = [
		widget.Spacer(
			length = 2
		),

		modify(
			CustomImage,
			background 	= colors["light_blue"],
			inactive_background = colors["light_white"],
			decorations = [
				RectDecoration(
					filled = True,
					radius = 10,
					use_widget_background = True
				)
			],
			font = FONT,
			fontsize = 16,
			# mouse_callbacks = {
			# 	"Button1": lazy.restart()
			# },
			padding = 20,
			filename = "~/.config/qtile/DATA/icons/Inheritor_logo.png",
		),

		CustomTextBox(
			background = None,
			foreground = colors["light_white"],
			font = FONT,
			fontsize = 16,
			offset = -8,
			padding = 8,
			text = "󰇙"
		),

		CustomGroupBox(
			font = FONT,
			fontsize = 17,
			background = None,
			borderwidth = 1,
			colors = [
				colors["red"], colors["light_red"], colors["yellow"], colors["light_green"], colors["green"], colors["light_blue"], colors["blue"], colors["cyan"], colors["light_magenta"], colors["magenta"]
			],
			highlight_method = "line",
			inactive = colors["light_white"],
			invert = True,
			padding = 7,
			rainbow = True
		),

		CustomTextBox(
			background = None,
			foreground = colors["light_white"],
			font = FONT,
			fontsize = 16,
			offset = 4,
			padding = 4,
			text = "󰇙"
		),

		modify(
			widget.CurrentLayoutIcon,
			custom_icon_paths = [PATH_LAYOUT_ICONS],
			foreground = colors["light_black"],
			background = colors["light_magenta"],
			font = FONT,
			fontsize = 16,
			decorations = [
				RectDecoration(
					filled = True,
					radius = [10, 0, 0, 10],
					use_widget_background = True
				)
			],
			padding = 6,
			scale = 0.5

		),

		modify(
			CustomTextBox,
			foreground = colors["light_black"],
			background = colors["light_magenta"],
			font = FONT,
			fontsize = 1,
			decorations = [
				PowerLineDecoration(
					path = "arrow_right",
					size = 11
				)
			],
			text = " ",
		),

		modify(
			CustomTextBox,
			foreground = colors["light_black"],
			background = colors["light_red"],
			font = FONT,
			fontsize = 13,
			offset = -1,
			text = "",
			x = -5
		),

		modify(
			widget.CheckUpdates,
			foreground = colors["light_black"],
			background = colors["light_red"],
			font = FONT,
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
			distro = "Arch",
			initial_text = "No update  ",
			no_update_string = "No update  ",
			padding = 0,
			update_interval = 3600,
		),

		widget.Spacer(),

		widget.WindowName(
			foreground = colors["light_white"],
			background = None,
			font = FONT,
			fontsize = 13,
			max_chars = 60,
			format = "{name}",
			width = CALCULATED
		),

		widget.Spacer(),

		modify(
			CustomTextBox,
			background 	= colors["light_green"],
			foreground = colors["light_black"],
			decorations = [
				RectDecoration(
					filled = True,
					radius = [10, 0, 0, 10],
					use_widget_background = True
				)
			],
			font = FONT,
			fontsize = 16,
			text = "󰋋",
			x = 4
		),

		# modify(
		widget.PulseVolume(
			background = colors["light_green"],
			foreground = colors["light_black"],
			font = FONT,
			fontsize = 13,
			decorations = [
				PowerLineDecoration(
					path = "arrow_right",
					size = 11
				)
			],
			update_interval = 0.2,
			width = CALCULATED,
			padding = 3,
			fmt = " {} "
		),

		CustomTextBox(
			foreground = colors["light_black"],
			background = colors["light_yellow"],
			font = FONT,
			fontsize = 16,
			offset = -2,
			padding = 5,
			text = "󰍛",
			x = -2
		),

		widget.Memory(
			foreground = colors["light_black"],
			background = colors["light_yellow"],
			font = FONT,
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
			font = FONT,
			fontsize = 13,
			offset = -1,
			text = "󰋊",
			x = -5
		),

		widget.DF(
			foreground = colors["light_black"],
			background = colors["light_cyan"],
			font = FONT,
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
			font = FONT,
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
			font = FONT,
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
			font = FONT,
			fontsize = 13,
			format = "%d %b %Y - %H:%M",
			padding = 6
		),

		widget.Spacer(
			length = 2
		)

		# widget.Prompt(
		#     prompt = "{0}@{1}: ".format(os.environ["USER"], socket.gethostname()),
		#     font = font,
		#     padding = 10,
		#     foreground = colors["light_red"],
		#     background = colors["light_grey"]
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
	]
	return widgets_list

def init_widgets_screen1():
	widgets_screen1 = _init_widgets_list() # Slicing removes unwanted widgets on Monitors 1,3
	return widgets_screen1

def init_widgets_screen2():
	widgets_screen2 = _init_widgets_list()
	return widgets_screen2
