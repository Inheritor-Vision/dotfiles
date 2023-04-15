# Qtile hooks
# Hooks used to manage all sorts of things based on qtile events

from core.conf 				import (
	DICT_MATCH, 
	DICT_SKETCHY_APPS_ONCE,
	PATH_AUTOSTART,
	PATH_ICONS_CACHE
)
from core.debug				import log
from core.groups			import icon

from libqtile 				import hook

import os, subprocess


# -------------------------------------| Settings |------------------------------------- #

focus_on_window_activation = "smart"

# -------------------------------| Random Icons Caching |------------------------------- #

# When restarting, groups are not fully updated (i.e. old groups are not deleted, 
# new are added). As consequence, random generates a new icon that is added to the bar
# and the old ones are not deleted. Hence, on restart, icon must be saved and not 
# re-generated.

@hook.subscribe.startup_complete
def clean_cache():
	try:
		os.remove(PATH_ICONS_CACHE)
	except FileNotFoundError:
		pass

# -------------------------------| Sketchy App Catcher |-------------------------------- #

# Some apps pass though Qtile match process, because it is relies on X11 properties
# that can be poorly / wrongly implemented by the app dev.
# For apps with indirection and/or that implements poorly X11 
# and/or have multiple pids (& fucks with X11 rules)
# See async wait in qtile https://github.com/qtile/qtile/pull/2063
# See example of uncatchable apps (Spotify, that now is catchable tbf):
# https://github.com/qtile/qtile/issues/1915
# Debug hook: 
# https://gist.github.com/ramnes/2feecfa7aecf7260dd7b65f7cb995c31
# Workaround: 
# https://groups.google.com/g/qtile-dev/c/DYVYuAzYbG4/m/R8IWR-hfAgAJ
# Window page: 
# https://github.com/qtile/qtile/blob/0c049edd96069a7030c4895e9832711c07bb0bfa/
# libqtile/backend/base.py
# Window.window (set_property?): 
# https://github.com/qtile/qtile/blob/0c049edd96069a7030c4895e9832711c07bb0bfa/
# libqtile/backend/x11/window.py

@hook.subscribe.client_new
def catch_sketchy_apps_once(window):
	a = window.window.get_name()

	if type(a) != str:
		if type(a) == type(None):
			return
		else:
			log("window.get_name(): " + str(a))
			log("window.get_name(): " + str(type(a)))
			return

	if DICT_SKETCHY_APPS_ONCE:
		if a in DICT_SKETCHY_APPS_ONCE:
			window.cmd_togroup(DICT_SKETCHY_APPS_ONCE[a])
			DICT_SKETCHY_APPS_ONCE.pop(a)

	for pattern, group in DICT_MATCH.items():
		if pattern.match(a):
			if group == "icon":
				group = icon
			window.cmd_togroup(group)
			break

# ------------------------------------| Autostart |------------------------------------- #

# Few things to do before finishing launching Qtile placed in one script
@hook.subscribe.startup_once
def autostart():
	subprocess.Popen(["/bin/sh", PATH_AUTOSTART])