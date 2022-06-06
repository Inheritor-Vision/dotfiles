import json
import subprocess

from tinydb import TinyDB, Query
from hashlib import sha256

class ColorSchemeUnifier():

    PATH_COLORPALETTE   = "ColorPalette/colorPalette.js"
    MODE_COLORPALETTE   = "deep"

    COUNT               = 5
    
    DB_NAME             = "db.json"
    DB_DEFAULT_TABLE    = "image_palette"
 
    db                  = None


    def __init__(self):
        self.db                     = TinyDB(self.DB_NAME)
        self.db.default_table_name  = self.DB_DEFAULT_TABLE


    def change_theme(self, image):
        image_hash = sha256(open(image, "rb").read()).hexdigest()

        palette = self._get_color_scheme(image, image_hash)



    def _get_color_scheme(self, image, image_hash):
        res = self.db.search(Query().image_hash == image_hash)

        if res:
            print("Already in!")
            return res[0]["palette"] 
        else:
            print("New !!!")
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
            self._save_color_scheme(image_hash, palette)
            return palette

    def _save_color_scheme(self, image_hash, palette):
        self.db.insert({"image_hash": image_hash, "palette": palette})

        

test = ColorSchemeUnifier();
test.change_theme("/mnt/data/Display System/Real WP/pZF4Q6L.jpg")
test.change_theme("/mnt/data/Display System/Real WP/giTlCNT.jpg")
print(test.db.all())
