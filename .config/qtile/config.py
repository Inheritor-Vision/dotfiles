# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import List  # noqa: F401

from libqtile import bar, layout, widget, hook
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal
from libqtile.xkeysyms import keysyms
from libqtile.log_utils import logger

import os, socket, subprocess

# ----- ALIAS ----- #

alt = "mod1"
mod = "mod4"
terminal = "alacritty" 
font = "FiraCode Nerd Font Mono Bold"


available_screens = {
    "primary": "DP-4",
    "secondary": "HDMI-0"
}

azerty_group_patch = {1:"ampersand", 2:"eacute", 3:"quotedbl", 4:"apostrophe", 5:"parenleft", 6:"minus", 7:"egrave", 8:"underscore", 9:"ccedilla", 10:"agrave"}

colors = {
    "black_grey" : "#282A36",   # panel_bg
    "dark_grey"  : "#434758",   # current_screen_tab_bg
    "white"      : "#ffffff",   # group_names
    "light_red"  : "#ff5555",   # layout_widget_bg
    "black"      : "#000000",   # other_screen_tabs_bg
    "purple"     : "#A77AC4"   # other_screen_tabs
}

ENCYCLOPEDIA_PATH = '/mnt/data/Encyclopedia\ Galactica/'

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
    Key([], "XF86AudioLowerVolume", lazy.spawn("pactl set-sink-volume 1 -5%")),
    Key([], "XF86AudioRaiseVolume", lazy.spawn("pactl set-sink-volume 1 +5%")),
    Key([], "XF86AudioMute", lazy.spawn("pactl set-sink-mute 0 toggle")),

    # App lauch
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),

    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "w", lazy.window.kill(), desc="Kill focused window"),

    # Restat, Quit and Execute
    Key([mod, "control"], "r", lazy.restart(), desc="Restart Qtile"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod], "r", lazy.spawncmd(),
        desc="Spawn a command using a prompt widget"),
]

# ----- GROUPS ----- #

def init_group_names():
    return [("DEV", {'layout':'monadtall'}),
            ("WWW", {'layout':'max',        'spawn': 'brave'}),
            ("RAN", {'layout':'monadtall'}),
            ("VMM", {'layout':'max'}),
            ("OBS", {'layout':'monadtall'}),
            ("MUS", {'layout':'monadtall',  'spawn': 'alacritty -e spt'}),
            ("GFX", {'layout':'floating'}),
            ("EKS", {'layout':'monadtall'}),
            ("DOC", {'layout':'monadtall',  'spawn': 'alacritty --working-directory ' + ENCYCLOPEDIA_PATH})]

group_names = init_group_names()
groups = [Group(name, **kwargs) for name, kwargs in group_names]

for i, (name, kwargs) in enumerate(group_names, 1):
        keys.append(Key([mod], azerty_group_patch[i], lazy.group[name].toscreen()))        # Switch to another group
        keys.append(Key([mod, "shift"], azerty_group_patch[i], lazy.window.togroup(name))) # Send current window to another group


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
        sections = ["ONE", "TWO", "THREE", "FOUR", "FIVE"],
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
    font=font,
    fontsize=11,
    padding=3,
    background = colors["black_grey"]
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

        widget.Image(
            filename = "~/.config/qtile/DATA/icons/Inheritor_logo.png",
            margin = 2,
            margin_x = 5
        ),

        widget.Sep(
            linewidth = 0,
            padding = 5,
            foreground = colors["white"],
            background = colors["black_grey"],
        ),

        widget.GroupBox(
            font = font,
            margin_x = 0,
            margin_y = 2,
            padding_x = 8,
            padding_y = 8,
            borderwidth = 1,
            active = colors["white"],
            inactive = colors["white"],
            highlight_method = "block",
            rounded = False,
            this_current_screen_border = colors["purple"],
            this_screen_border = colors["dark_grey"],
            other_current_screen_border = colors["black_grey"],
            other_screen_border = colors["black_grey"],
            foreground = colors["white"],
            background = colors["black_grey"]
        ),

        widget.Prompt(
            prompt = "{0}@{1}: ".format(os.environ["USER"], socket.gethostname()),
            font = font,
            padding = 10,
            foreground = colors["light_red"],
            background = colors["dark_grey"]
        ),

        widget.WindowName(
            foreground = colors["purple"]
        ),

        widget.TextBox(
            background = colors["white"],
            foreground = colors["black_grey"],
            text = "Vision-MAIN", 
            name="default"
        ),

        widget.Sep(
            linewidth = 1, 
            padding = 10, 
            foreground = colors["white"], 
            background = colors["black_grey"]
        ),

        widget.Image(
            filename = "~/.config/qtile/DATA/icons/wired.png",
            margin = 2,
            margin_x = 5
        ),

        widget.Net(
            interface = "wlp5s0",
            format = '{down} ▼▲ {up}' # format = '{interface}: {down} ▼▲ {up}'
        ),

        widget.Sep(
            linewidth = 0, 
            padding = 3
        ),

        widget.Image(
            filename = "~/.config/qtile/DATA/icons/processor.png",
            margin = 2,
            margin_x = 5
        ),
        widget.CPU(
            format = '{load_percent}%'
        ),

        widget.Sep(
            linewidth = 0, 
            padding = 3
        ),

        widget.Image(
            filename = "~/.config/qtile/DATA/icons/ram.png",
            margin = 2,
            margin_x = 5
        ),
        widget.Memory(
                foreground = colors["white"],
                background = colors["black_grey"],
                padding = 5,
                format = '{MemUsed}Mb ({MemPercent}%)'
        ),

        widget.Sep(
            linewidth = 0, 
            padding = 3
        ),

        widget.Image(
            filename = "~/.config/qtile/DATA/icons/hard_drive.png",
            margin = 2,
            margin_x = 5
        ),
        widget.DF(
                foreground = colors["white"],
                background = colors["black_grey"],
                padding = 5,
                partition = '/',
                format = '{uf}Gb ({r:.0f}%)',
                visible_on_warn = False,
                warn_space = 10
        ),

        widget.Sep(
            linewidth = 1, 
            padding = 10, 
            foreground = colors["white"], 
            background = colors["black_grey"]
        ),

        widget.CurrentLayoutIcon(
            custom_icon_paths = [os.path.expanduser("~/.config/qtile/DATA/icons")],
            background = colors["black_grey"],
            padding = 0,
            scale = 0.5
        ),

        widget.Sep(
            linewidth = 1, 
            padding = 10, 
            foreground = colors["white"], 
            background = colors["black_grey"]
        ),

        widget.TextBox(
            text = "墳",
            fontsize = 18
        ),

        widget.GenPollText(
                    func=get_current_volume,
                    update_interval=0.2,
        ),

        widget.Sep(
            linewidth = 1, 
            padding = 10, 
            foreground = colors["white"], 
            background = colors["black_grey"]
        ),
        
        widget.TextBox(
            text = "",
            fontsize = 18
        ),

        widget.GenPollText(
            func=get_kb_layout,
            update_interval=0.5,
        ),

        widget.Sep(
            linewidth = 1, 
            padding = 10, 
            foreground = colors["white"], 
            background = colors["black_grey"]
        ),

        widget.TextBox(
            text = "",
            fontsize = 18
        ),
        
        widget.Clock(
            format='%a, %d %b. %Y - %H:%M:%S' # %S for adding seconds
        )
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
    return [Screen(top=bar.Bar(widgets=init_widgets_screen1(), opacity=1.0, size=25)),
            Screen(top=bar.Bar(widgets=init_widgets_screen2(), opacity=1.0, size=25))]


if __name__ in ["config", "__main__"]:
    screens = init_screens()

# screens = [
#     Screen(
#         top=bar.Bar(
#             [
#                 widget.CurrentLayout(),
#                 widget.GroupBox(),
#                 widget.Prompt(),
#                 widget.WindowName(),
#                 widget.Chord(
#                     chords_colors={
#                         'launch': ("#ff0000", "#ffffff"),
#                     },
#                     name_transform=lambda name: name.upper(),
#                 ),
#                 widget.TextBox("default config", name="default"),
#                 widget.TextBox("Press &lt;M-r&gt; to spawn", foreground="#d75f5f"),
#                 widget.Systray(),
#                 widget.Clock(format='%Y-%m-%d %a %I:%M %p'),
#                 widget.QuickExit(),
#             ],
#             24,
#         ),
#     ),
# ]

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

# ---- STARTUP ----
@hook.subscribe.startup_once
def autostart():
    pass

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
# Menu = "Menu"
