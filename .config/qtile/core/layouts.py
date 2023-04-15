# Layouts
# Define layouts used for this config

from core.conf			import FONT

from libqtile			import layout
from libqtile.config	import Match


# ----------------------------------| Tiling Layouts |---------------------------------- #

_layout_theme = {
		"border_width": 2,
		"margin": 20,
		"border_focus": "e1acff",
		"border_normal": "1D2330"
}

layouts = [
	layout.Max(**_layout_theme),
	layout.MonadTall(**_layout_theme, ratio = 0.6),
	layout.TreeTab(
		font = FONT,
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
	layout.Floating(**_layout_theme),
	layout.Zoomy(**_layout_theme)
]


# ---------------------------------| Floating Layouts |--------------------------------- #

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