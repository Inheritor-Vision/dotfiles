from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

def hex_to_rgb(c):
    base = 1 if c[0] == "#" else 0
    return tuple(int(c[i:i+2], 16) for i in range(base,base+6,2))

def rgb_to_hex(c):
    return "#%02x%02x%02x" % c

def color_distance(c1, c2):
    c1 = convert_color(sRGBColor(*hex_to_rgb(c1), is_upscaled=True), LabColor)
    c2 = convert_color(sRGBColor(*hex_to_rgb(c2), is_upscaled=True), LabColor)
    return delta_e_cie2000(c1, c2)

def lighten_color(c):
    scale = 6   # Seems to be a good value. Room for improvment.
    res = None
    while scale:
        lab_c   = convert_color(sRGBColor(*hex_to_rgb(c), is_upscaled=True), LabColor)
        lab_c.lab_l = round(((100 - lab_c.lab_l)/scale)+lab_c.lab_l)
        res = convert_color(lab_c,sRGBColor).get_upscaled_value_tuple()
        scale = 0 if res[0] < 255 and res[1] < 255 and res[2] < 255 else scale + 1
    return res

def darken_color(c):
    lab_c   = convert_color(sRGBColor(*hex_to_rgb(c), is_upscaled=True), LabColor)
    lab_c.lab_l = round(lab_c.lab_l - (lab_c.lab_l/9))
    res = convert_color(lab_c,sRGBColor).get_upscaled_value_tuple()
    return res

# Mat is balanced. There is more man than woman.
def Gale_Shapley(mat):
    mat         = {k:{sk:sv for sk,sv in sorted(v.items(), key=lambda item: item[1])} for k,v in mat.items()}
    M_Free      = list(mat.keys())
    F           = dict.fromkeys(next(iter(mat.items()))[1].keys(), None)
    while M_Free:
        m = M_Free.pop(0)
        w,v = next(iter(mat[m].items()))
        del mat[m][w]
        if not F[w]:
            F[w] = (m,v)
        else:
            if F[w][1] > v:
                M_Free.append(F[w][0])
                F[w] = (m,v)
            else:
                M_Free.append(m)
    return {v[0]:k for k,v in F.items() if v}
    
# import random
# def GS_test():
#     M_MAX = 10
#     F_MAX = 20
#     mat = {}
#     for i in range(M_MAX):
#         mat["M%i"%i] = {}
#         for j in range(F_MAX):
#             mat["M%d"% i]["M%d"%j] = random.randint(0,100)
#     print(mat)
#     print()
#     print(Gale_Shapley(mat))
# GS_test()

class Alacritty_colors():

    TEMPLATE = """\
live_config_reload: true

schemes:
  automatic: &auto
    primary:
      background: '#{bg}'
      foreground: '#{fg}'

    # Normal colors
    normal:
      black:   '#{nblack}'
      red:     '#{nred}'
      green:   '#{ngreen}'
      yellow:  '#{nyellow}'
      blue:    '#{nblue}'
      magenta: '#{nmagenta}'
      cyan:    '#{ncyan}'
      white:   '#{nwhite}'

    # Bright colors
    bright:
      black:   '#{bblack}'
      red:     '#{bred}'
      green:   '#{bgreen}'
      yellow:  '#{byellow}'
      blue:    '#{bblue}'
      magenta: '#{bmagenta}'
      cyan:    '#{bcyan}'
      white:   '#{bwhite}'

colors: *auto
"""
    # Tangoish
    DEFAULT_COLOR = {
            # Derived "fg":       "2e3436",
            # Derived "bg":       "eeeeec",

            "nblack":   "2e3436",
            "nred":     "cc0000",
            "ngreen":   "73d216",
            "nyellow":  "edd400",
            "nblue":    "3465a4",
            "nmagenta": "75507b",
            "ncyan":    "f57900",
            # Derived "nwhite":   "d3d7cf",

            # Derived "bblack":   "2e3436",
            # Derived "bred":     "ef2929",
            # Derived "bgreen":   "8ae234",
            # Derived "byellow":  "fce94f",
            # Derived "bblue":    "729fcf",
            # Derived "bmagenta": "ad7fa8",
            # Derived "bcyan":    "fcaf3e",
            Derived "bwhite":   "eeeeec",
    }

    def _generate_colors_from_scheme(self, scheme):
        if len(scheme) < len(DEFAULT_COLOR):
            raise ValueError("Not enought color in input")
        
        list_cs_dist = []
        for dc in DEFAULT_COLOR:
            mat_c_dist[dc] = {}
            for c in scheme:
               mat_c_dist[dc][c] = color_distance(dc,c)
        
        palette_dark    = Gale_Shapley(mat_c_dist)
        palette_light   = {"b" + k[1:]: lighten_corlor(v) for k,v in palette_dark.items() if k not in ("fg", "bg")}
        return {**palette_dark, **palette_light}





        
        


