import json
import subprocess

from hashlib import sha256
from tinydb import TinyDB, Query

class ColorSchemeUnifier():

    PATH_COLORPALETTE   = "ColorPalette/colorPalette.js"
    MODE_COLORPALETTE   = "deep"

    COUNT               = 5
    
    DB_NAME             = "db.json"
    DB_DEFAULT_TABLE    = "image_palette"
 
    db                  = None
    colorpalette_ver    = None

    def __init__(self):
        self.db                     = TinyDB(self.DB_NAME)
        self.db.default_table_name  = self.DB_DEFAULT_TABLE

        self.colorpalette_ver       = subprocess.check_output([
            "node",
            self.PATH_COLORPALETTE,
            "-v"
        ]).decode().replace("\n", "")

    def change_theme(self, image):
        image_hash = sha256(open(image, "rb").read()).hexdigest()

        palette = self._get_color_scheme(image, image_hash)



    def _get_color_scheme(self, image, image_hash):
        res = self.db.search(Query().image_hash == image_hash)

        if res and res[0]["colorpalette_ver"] == self.colorpalette_ver:
            return res[0]["palette"]    
        else:
            output = subprocess.check_output(
                    (
                        "node", 
                        self.PATH_COLORPALETTE,
                        image,
                        self.MODE_COLORPALETTE,
                        str(self.COUNT)
                    )
                )
            palette = json.loads(output)["palette"]

            if res and res[0]["colorpalette_ver"] != self.colorpalette_ver:
                self._update_color_scheme(image_hash, palette)
            else:
                self._save_color_scheme(image_hash, palette)
            
            return palette

    def _update_color_scheme(self, image_hash, palette):
        self.db.update({"colorpalette_ver": self.colorpalette_ver, "palette": palette}, Query().image_hash == image_hash)

    def _save_color_scheme(self, image_hash, palette):
        self.db.insert({"image_hash": image_hash, "palette": palette, "colorpalette_ver": self.colorpalette_ver})

