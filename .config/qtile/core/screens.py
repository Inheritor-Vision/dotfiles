# Screens
# How screens are setup!

from core.conf			import colors
from core.bar			import init_widgets_screen1, init_widgets_screen2

from libqtile.bar		import Bar
from libqtile.config	import Screen


# -------------------------------------| Settings |------------------------------------- #

auto_fullscreen = True


# --------------------------------| Screens Generation |-------------------------------- #

def _init_screens():
	return [
		Screen(top=Bar(
			widgets=init_widgets_screen1(),
			size=22,
			background=colors["light_black"],
			border_color=colors["light_black"],
			margin=[10,10,0,10],
			border_width=4,
			opacity = 1)
		),
		Screen(top=Bar(
			widgets=init_widgets_screen2(), 
			size=22,
			background=colors["light_black"],
			border_color=colors["light_black"],
			margin=[10,10,0,10],
			border_width=4,
			opacity = 1)
		)]


screens = _init_screens()