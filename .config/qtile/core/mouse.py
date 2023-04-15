# Mouse
# Mouse related settings.

from core.conf				import MOD

from libqtile.config		import Click, Drag
from libqtile.lazy			import lazy


# -------------------------------------| Settings |------------------------------------- #

bring_front_click 	= "floating_only"
cursor_warp 		= False
follow_mouse_focus 	= True

# -----------------------------------| Mouse Setup |------------------------------------ #

# Drag floating layouts.
mouse = [
	Drag([MOD], "Button1", lazy.window.set_position_floating(),
		 start=lazy.window.get_position()),
	Drag([MOD], "Button3", lazy.window.set_size_floating(),
		 start=lazy.window.get_size()),
	Click([MOD], "Button2", lazy.window.bring_to_front())
]