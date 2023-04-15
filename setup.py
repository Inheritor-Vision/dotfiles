import os, shutil, tempfile

MAGIC       = "9bf624c60be9dca4fe9379f01da90d905667d8b2"    # SHA1("vision_setup_patcher")

#---------------------------------------| Utility |--------------------------------------#

# Return abspath or None
def get_file(file):
    if os.path.exists(file):
        return os.path.abspath(file)
    else:
        return shutil.which(file)

def is_file_existing(file):
    return get_file != None

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

    def warning(self, text):
            print(f"{self.WARNING}[!] setup: {text}{self.ENDC}")

    def error(self, text):
            print(f"{self.FAIL}[X] setup: {text}{self.ENDC}")


#----------------------------------| dotfiles to patch |---------------------------------#

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
    }
}


#----------------------------------------| Core |----------------------------------------#


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
                            log.warning(f"\"{l}\" does not match any keys. Key has been removed")
                            ft.write(b"\n")
                for k in dp[file]:
                    if k not in keys_replaced:
                        log.warning(f"{k} has not been found")
            ft.seek(0)
            with open(file_path, "wb") as f:
                f.write(ft.read())


if __name__ == "__main__":
    patch(dotfiles_patch)
