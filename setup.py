import os, shutil, tempfile

MAGIC       = "9bf624c60be9dca4fe9379f01da90d905667d8b2"    # SHA1("vision_setup_patcher")

# --------------------------------------| Utility |------------------------------------- #

# Return abspath or None
def get_file(file):
    if os.path.exists(file):
        return os.path.abspath(file)
    else:
        return shutil.which(file)

def is_file_existing(file):
    return get_file(file) != None

class log:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def warning(text):
            print(f"{log.WARNING}{log.BOLD}[!]{log.ENDC} setup: {text}")

    def error(text):
            print(f"{log.FAIL}{log.BOLD}[X]{log.ENDC} setup: {text}")


# ---------------------------------| dotfiles to patch |-------------------------------- #

pyenv_setup = """\
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH",
"""

nnn_setup = """\
export NNN_OPTS="eEdU"
export VISUAL=ewrap

n ()
{
    # Block nesting of nnn in subshells
    if [[ "${NNNLVL:-0}" -ge 1 ]]; then
        echo "nnn is already running"
        return
    fi

    # The behaviour is set to cd on quit (nnn checks if NNN_TMPFILE is set)
    # If NNN_TMPFILE is set to a custom path, it must be exported for nnn to
    # see. To cd on quit only on ^G, remove the "export" and make sure not to
    # use a custom path, i.e. set NNN_TMPFILE *exactly* as follows:
    #     NNN_TMPFILE="${XDG_CONFIG_HOME:-$HOME/.config}/nnn/.lastd"
    export NNN_TMPFILE="${XDG_CONFIG_HOME:-$HOME/.config}/nnn/.lastd"
    
    # Unmask ^Q (, ^V etc.) (if required, see `stty -a`) to Quit nnn
    # stty start undef
    # stty stop undef
    # stty lwrap undef
    # stty lnext undef

    # The backslash allows one to alias n to nnn if desired without making an
    # infinitely recursive alias
    \nnn "$@"

    if [ -f "$NNN_TMPFILE" ]; then
            . "$NNN_TMPFILE"
            rm -f "$NNN_TMPFILE" > /dev/null
    fi
}
"""

# {"filename": {"key":("text_replacing_key", "OPTIONAL_condition"), ...}, ...}
dotfiles_patch = {
    ".xinitrc": {
        "screen_setup": ("xrandr --output Virtual1 --primary",),
        "keyboard_setup": ("setxkbmap -option caps:swapescape",),
        "numlock": ("numlockx &", is_file_existing("numlockx")),
        "wallpaper": ("feh --randomize --bg-max ~/.config/qtile/DATA/wallpaper.jpg",),
        "screenshot_util": ("flameshot &", is_file_existing("flameshot")),
        "grub_theme_cycle": ("/boot/grub/themes/minegrub-theme/Cycle/Cycler.sh",
                            is_file_existing("/boot/grub/themes/minegrub-theme/\
                            Cycle/Cycler.sh")),
    },
        "..config/qtile/core/conf.py": {
        "sound_sink_name": ("SOUND_SINK_NAME = \"alsa_output.pci-0000_00_05.0.analog-stereo\"",),
    },
    ".bashrc": {
        "path_rust": ("export PATH=$PATH:/home/vision/.cargo/bin", False),
        "path_pyenv": (pyenv_setup, is_file_existing("pyenv")),
        "nnn": (nnn_setup, is_file_existing("nnn")),
    }
}


# ---------------------------------------| Core |--------------------------------------- #


def patch(dp):
    for file in dp:
        if not is_file_existing(file):
            log.error(f"{file} cannot be found! Passing")
            pass
        keys_replaced = []
        file_path = get_file(file)
        with tempfile.TemporaryFile() as ft:
            with open(file_path, "r") as f:
                for l in f.readlines():
                    if MAGIC not in l:
                        ft.write(l.encode())
                    else:
                        l = l.strip()
                        for key in dp[file]:
                            if (key + "_" + MAGIC) == l:
                                keys_replaced += [key]
                                content = dp[file][key]
                                if len(content) == 2 and not content[1]:
                                    ft.write(b"\n")
                                else:
                                    ft.write(dp[file][key][0].encode() + b"\n")
                                break
                        else: 
                            log.warning(f"\"{l}\" does not match any keys found in {file}. Key has been removed")
                            ft.write(b"\n")
                for k in dp[file]:
                    if k not in keys_replaced:
                        log.warning(f"{k} has not been found in {file}")
            ft.seek(0)
            with open(file_path, "wb") as f:
                f.write(ft.read())


if __name__ == "__main__":
    patch(dotfiles_patch)
