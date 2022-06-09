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

def min_max_luminosity(scheme):
        mini = maxi = (convert_color(sRGBColor(*hex_to_rgb(scheme[0]), is_upscaled=True), LabColor).lab_l, scheme[0])
        for c in scheme[1:]:
            l = convert_color(sRGBColor(*hex_to_rgb(c), is_upscaled=True), LabColor).lab_l
            if l > maxi[0]:
                maxi = (l,c)
            elif l < mini[0]:
                mini = (l,c)
        scheme.remove(mini[1])
        scheme.remove(maxi[1])
        return (scheme, mini[1], maxi[1])


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
    # Tangoish theme
    DEFAULT_COLOR = {
            # Derived "fg":       "2e3436",
            # Derived "bg":       "eeeeec",

            # Mini "nblack":   "2e3436",
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
            # Maxi "bwhite":   "eeeeec",
    }

    def _white_black_luminosity(self,scheme):
        (scheme, mini, maxi) = min_max_luminosity(scheme)
        return ({"nblack": maxi, "bwhite":mini}, scheme)
    
    def _generate_colors_from_scheme(self, scheme):
        if len(scheme) < len(self.DEFAULT_COLOR):
            raise ValueError("Not enought color in input")

        # Let's try to take the most luminescent color for white, opposite for black
        # Should be a better idea than distance (allow more diversity)
        (palette_default,scheme) = self._white_black_luminosity(scheme)

        mat_cs_dist = {}
        for dc in self.DEFAULT_COLOR:
            mat_cs_dist[dc] = {}
            for c in scheme:
               mat_cs_dist[dc][c] = color_distance(self.DEFAULT_COLOR[dc],c)
        
        palette_dark    = Gale_Shapley(mat_cs_dist)
        palette_light   = {"b" + k[1:]: rgb_to_hex(lighten_color(v)) for k,v in palette_dark.items() if k not in ("fg", "bg")}
        return {
                **palette_default, 
                **palette_dark, 
                **palette_light, 
                "bblack": rgb_to_hex(lighten_color(palette_default["nblack"])),
                "nwhite": rgb_to_hex(darken_color(palette_default["bwhite"])),
        }

    def _test_print(self, palette):
        chars   = "\x1b[48;2;{0};{1};{2}m" + "   " + "\x1b[0m"
        dark    = "\t\t"
        light   = "\t\t"
        for k in ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"):
            
            dark    += chars.format(*hex_to_rgb(palette["n" + k]))
            light   += chars.format(*hex_to_rgb(palette["b" + k]))
        print()
        print(dark)
        print(light)
        print()


        
# import random
# def GS_test():
#     M_MAX = 10
#     F_MAX = 20
#     mat = {}chars   = "\x1b[48;2;{0};{1};{2}" + u"\u2588"*3 + "A" + "\x1b[0m"
#     for i in range(M_MAX):
#         mat["M%i"%i] = {}
#         for j in range(F_MAX):
#             mat["M%d"% i]["M%d"%j] = random.randint(0,100)
#     print(mat)
#     print()
#     print(Gale_Shapley(mat))
# GS_test()

def print_test():
    scheme = ["2e3436", "cc0000", "73d216", "edd400", "3465a4", "75507b", "f57900", "eeeeec"]
    ala = Alacritty_colors()
    ala._test_print(ala._generate_colors_from_scheme(scheme))

print_test()
        


