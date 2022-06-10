import json
import colorgram
import subprocess

from hashlib import sha256
from tinydb import TinyDB, Query

import target.Alacritty_colors as AC

class ColorSchemeUnifier():

    PATH_COLORPALETTE   = "ColorPalette/colorPalette.js"
    MODE_COLORPALETTE   = "deep"

    COUNT               = 8
    
    DB_NAME             = "db.json"
    DB_DEFAULT_TABLE    = "image_palette"
 
    db                  = None
    alacritty           = None

    def __init__(self):
        self.db                     = TinyDB(self.DB_NAME)
        self.db.default_table_name  = self.DB_DEFAULT_TABLE
        
        self.alacritty              = AC.Alacritty_colors()


    def change_theme(self, image):
        image_hash = sha256(open(image, "rb").read()).hexdigest()
    
        palette = self._get_color_scheme(image, image_hash)         

        

    def _get_color_scheme(self, image, image_hash):
        palette = None

        res = self.db.search(Query().image_hash == image_hash)
        if len(res) > 1:
            raise ValueError("Too much result have been returned, db in an inconsistent state!")

        if res:
            palette = res[0]["palette"]
        else:
            palette = {}
            palette["palette"]      = [AC.rgb_to_hex(i.rgb) for i in colorgram.extract(image,8)]
            # Alacritty
            palette["alacritty"]    = self.alacritty.generate_colors_from_scheme(palette["palette"])

            self._save_color_scheme(image_hash, palette)
        
        self.alacritty.generate_conf_from_colors(palette["alacritty"])
        return palette["palette"]

    def _save_color_scheme(self, image_hash, palette):
        self.db.insert({"image_hash": image_hash, "palette": palette})

