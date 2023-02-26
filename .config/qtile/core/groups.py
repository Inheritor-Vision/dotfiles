# Groups
# All information about the differents groups can be found here!

from core.conf				import (
	DICT_CODE_POINT,
	PATH_ENCYCLOPEDIA, 
	PATH_ICONS_CACHE
)

from libqtile.config	import Group, Match

import json, random, re

# -------------------------------------| Settings |------------------------------------- #

dgroups_app_rules = []

# -------------------------------| Random Icon Selector |------------------------------- #

def _rd_icon():
	family = random.choices(
		[a for a in DICT_CODE_POINT.keys()], 
		[((maxi - mini + 0x4) / 0x4) for (mini,maxi) in DICT_CODE_POINT.values()]
	)
	(mini, maxi) = DICT_CODE_POINT[family[0]]
	return chr(random.randrange(mini, maxi + 0x4, 0x4))

# Recover icon from cache if present. Only used in case of lazy.restart()
# Else generates a new one!
def _get_icon():
	icon = None
	try:
		with open(PATH_ICONS_CACHE, "r") as f:
			icon = json.load(f)["icons"][0]

	except FileNotFoundError:
		icon = _rd_icon()
	
	return icon

icon = _get_icon()


# ---------------------------------| Groups Generator |--------------------------------- #

def _init_group_names():
	return [
			("", {'layout':'monadtall'}),
			("", {'layout':'max',        'spawn': 'brave'}),
			("", {'layout':'monadtall'}),
			(icon, {'layout':'monadtall', "matches": [
				Match(title=[re.compile(".* - Oracle VM VirtualBox : 2.*")])
			]}),
			# ("i", {'layout':'monadtall', "matches": [
			# 	Match(title=[re.compile(".* - Oracle VM VirtualBox : 2.*")])
			# ]}),
			("󰍺", {'layout':'max', 'spawn': 'virtualbox', "matches": [
				Match(title=[re.compile(".* - Oracle VM VirtualBox : 1.*")])
			]}),
			("󱅰", {'layout':'treetab',    'spawn': ["discord", 'signal-desktop']}),
			("", {'layout':'monadtall',  'spawn': 'spotify'}),
			("󰒍", {'layout':'monadtall'}),
			("", {'layout':'monadtall',  'spawn': 'vscodium ' + PATH_ENCYCLOPEDIA \
				+ '/.vscode/Enc_Gal.code-workspace', "matches": [
					Match(title= [re.compile(".*Enc_Gal (Workspace).*")])
				]})]

group_names = _init_group_names()
groups = [Group(name, **kwargs) for name, kwargs in group_names]