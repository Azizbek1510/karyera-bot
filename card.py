"""Vakansiya uchun brendlangan kreativ rasm (kartochka) yasash.

Soha (kategoriya) bo'yicha rang va illyustratsiya o'zgaradi.
AI fon ulansa, `background` parametri orqali beriladi.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, random, textwrap

W, H = 1280, 720
import os
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts") + "/"
def font(style, size):
    return ImageFont.truetype(F + f"Inter-{style}.otf", size)

THEMES = {
    "talim":    {"c1": (30, 58, 138),  "c2": (59, 130, 246), "acc": (250, 204, 21),  "kw": ["maktab", "o'qituvchi", "direktor", "ta'lim", "bog'cha", "tarbiyachi", "pedagog"]},
    "tibbiyot": {"c1": (6, 95, 70),    "c2": (16, 185, 129), "acc": (255, 255, 255), "kw": ["shifokor", "hamshira", "tibbiy", "poliklinika", "kasalxona", "farmatsevt", "vrach"]},
    "transport":{"c1": (124, 45, 18),  "c2": (234, 88, 12),  "acc": (254, 215, 170), "kw": ["haydovchi", "transport", "avto", "logist"]},
    "it":       {"c1": (49, 46, 129),  "c2": (139, 92, 246), "acc": (165, 243, 252), "kw": ["dasturchi", "it", "operator", "kompyuter", "texnik"]},
    "moliya":   {"c1": (20, 83, 45),   "c2": (101, 163, 13), "acc": (254, 240, 138), "kw": ["buxgalter", "kassir", "iqtisodchi", "moliya", "bank"]},
    "umumiy":   {"c1": (15, 23, 42),   "c2": (71, 85, 105),  "acc": (56, 189, 248),  "kw": []},
}

def detect_theme(title, org=""):
    t = f"{title} {org}".lower()
    for name, th in THEMES.items():
        if any(k in t for k in th["kw"]):
            return name
    return "umumiy"

def _gradient(c1, c2):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for x in range(W):
        k = x / W
        d.line([(x, 0), (x, H)], fill=tuple(int(c1[i] + (c2[i] - c1[i]) * k) for i in range(3)))
    return img

def _illustration(layer, theme, acc):
    """O'ng tomonda sohaga mos oddiy vektor illyustratsiya."""
    d = ImageDraw.Draw(layer)
    cx, cy = 1010, 330
    white = (255, 255, 255, 235)
    a = acc + (255,)
    d.ellipse([cx-210, cy-210, cx+210, cy+210], fill=(255, 255, 255, 28))
    d.ellipse([cx-160, cy-160, cx+160, cy+160], fill=(255, 255, 255, 30))
    if theme == "talim":  # bitiruvchi qalpoqchasi + kitob
        d.polygon([(cx-150, cy-40), (cx, cy-110), (cx+150, cy-40), (cx, cy+30)], fill=white)
        d.rectangle([cx-85, cy-10, cx+85, cy+60], fill=white)
        d.line([(cx+120, cy-50), (cx+120, cy+60)], fill=a, width=8)
        d.ellipse([cx+106, cy+55, cx+134, cy+85], fill=a)
        d.rectangle([cx-120, cy+105, cx-5, cy+125], fill=a)
        d.rectangle([cx+5, cy+105, cx+120, cy+125], fill=a)
    elif theme == "tibbiyot":  # xoch belgisi
        d.rounded_rectangle([cx-45, cy-130, cx+45, cy+130], 18, fill=white)
        d.rounded_rectangle([cx-130, cy-45, cx+130, cy+45], 18, fill=white)
    elif theme == "transport":  # avtomobil
        d.rounded_rectangle([cx-170, cy-10, cx+170, cy+80], 30, fill=white)
        d.polygon([(cx-100, cy-10), (cx-60, cy-90), (cx+70, cy-90), (cx+120, cy-10)], fill=white)
        for x in (cx-95, cx+95):
            d.ellipse([x-42, cy+45, x+42, cy+129], fill=a)
    elif theme == "it":  # monitor + </>
        d.rounded_rectangle([cx-160, cy-110, cx+160, cy+90], 16, fill=white)
        d.rectangle([cx-30, cy+90, cx+30, cy+130], fill=white)
        d.text((cx, cy-10), "</>", font=font("Bold", 110), fill=a, anchor="mm")
    elif theme == "moliya":  # tangalar ustuni
        for i in range(4):
            y = cy + 90 - i * 50
            d.ellipse([cx-110, y-28, cx+110, y+28], fill=white if i % 2 == 0 else a)
    else:  # portfel
        d.rounded_rectangle([cx-150, cy-60, cx+150, cy+120], 24, fill=white)
        d.rounded_rectangle([cx-55, cy-110, cx+55, cy-50], 14, outline=white, width=18)
        d.rectangle([cx-150, cy+10, cx+150, cy+22], fill=a)

def _logo(d, x, y, s):
    """KaryeraUz belgisi: 3 ta ustun + yashil strelka (s — o'lcham px)."""
    k = s / 100
    bars = [((147, 197, 253), 18, 62, 40), ((59, 130, 246), 44, 44, 40), ((29, 78, 216), 70, 26, 40)]
    for col, bx, top, bw in bars:
        d.rounded_rectangle([x + bx*k, y + top*k, x + (bx+20)*k, y + 100*k], max(2, int(4*k)), fill=col)
    g = (16, 185, 129)
    d.line([(x + 10*k, y + 50*k), (x + 78*k, y + 6*k)], fill=g, width=max(3, int(7*k)))
    d.polygon([(x + 86*k, y + 0*k), (x + 66*k, y + 2*k), (x + 82*k, y + 18*k)], fill=g)

def make_card(v, out_path, background=None, variant=0):
    theme = detect_theme(v["title"], v.get("org", ""))
    th = THEMES[theme]
    c1, c2 = (th["c1"], th["c2"]) if variant % 2 == 0 else (th["c2"], th["c1"])
    if variant % 3 == 2:
        c2 = tuple(min(255, int(c * 0.6 + 60)) for c in c2)
    img = background.resize((W, H)).convert("RGB") if background else _gradient(c1, c2)
    # dekor: tasodifiy nuqtalar (har rasm biroz farq qiladi)
    rnd = random.Random(f"{v.get('id', v['title'])}-{variant}")
    deco = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(deco)
    for _ in range(18):
        r = rnd.randint(4, 16); x = rnd.randint(0, W); y = rnd.randint(0, H)
        dd.ellipse([x-r, y-r, x+r, y+r], fill=(255, 255, 255, rnd.randint(20, 60)))
    _illustration(deco, theme, th["acc"])
    img = Image.alpha_composite(img.convert("RGBA"), deco)
    # chap tomonda matn uchun yarim shaffof panel
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shade).rectangle([0, 0, 760, H], fill=(0, 0, 0, 70))
    img = Image.alpha_composite(img, shade.filter(ImageFilter.GaussianBlur(40)))
    d = ImageDraw.Draw(img)

    # yuqori yorliq
    d.rounded_rectangle([60, 56, 330, 104], 24, fill=th["acc"])
    d.text((195, 80), "BO'SH ISH O'RNI", font=font("Bold", 24), fill=th["c1"], anchor="mm")

    # sarlavha (avtomatik o'lcham)
    title = v["title"].upper()
    size = 76
    while size > 40:
        lines = textwrap.wrap(title, width=int(640 / (size * 0.62)))
        if len(lines) <= 3: break
        size -= 4
    y = 140
    for ln in lines:
        d.text((60, y), ln, font=font("ExtraBold", size), fill="white")
        y += int(size * 1.12)
    d.text((60, y + 10), v.get("org", ""), font=font("SemiBold", 32), fill=(226, 232, 240))
    y += 80

    # chiplar: tuman, o'rinlar, maosh
    x = 60
    chips = [(v.get("district", ""), (255, 255, 255), th["c1"]),
             (f"{v.get('slots', 1)} ta bo'sh o'rin", th["acc"], th["c1"])]
    for text, bg, fg in chips:
        if not text: continue
        fnt = font("Bold", 28)
        tw = d.textlength(text, font=fnt)
        d.rounded_rectangle([x, y, x + tw + 48, y + 56], 28, fill=bg)
        d.text((x + 24, y + 28), text, font=fnt, fill=fg, anchor="lm")
        x += tw + 64
    if v.get("salary"):
        d.text((60, y + 90), f"Maosh: {v['salary']}", font=font("SemiBold", 30), fill="white")

    # pastki oq chiziq — KaryeraUz brendi (logotip vektorda)
    d.rectangle([0, H - 84, W, H], fill=(255, 255, 255))
    d.rectangle([0, H - 88, W, H - 84], fill=(16, 185, 129))
    _logo(d, 60, H - 74, 64)
    fb = font("ExtraBold", 36)
    d.text((140, H - 42), "Karyera", font=fb, fill=(30, 41, 59), anchor="lm")
    d.text((140 + d.textlength("Karyera", font=fb), H - 42), "Uz", font=fb, fill=(16, 185, 129), anchor="lm")
    d.text((W - 60, H - 42), "t.me/karyerauznamangan", font=font("SemiBold", 26), fill=(71, 85, 105), anchor="rm")
    img.convert("RGB").save(out_path, quality=92)
    return out_path


if __name__ == "__main__":
    samples = [
        {"id": 116052, "title": "Direktor o'rinbosari", "org": "4-umumiy o'rta ta'lim maktabi",
         "district": "Yangiqo'rg'on tumani", "slots": 1, "salary": "Kelishiladi"},
        {"id": 2, "title": "Hamshira", "org": "Chust tuman tibbiyot birlashmasi",
         "district": "Chust tumani", "slots": 3, "salary": "4 500 000 so'm"},
        {"id": 3, "title": "Haydovchi", "org": "Namangan avtotransport korxonasi",
         "district": "Namangan shahri", "slots": 2, "salary": "5 000 000 so'm"},
        {"id": 4, "title": "Buxgalter", "org": "Uychi tuman moliya bo'limi",
         "district": "Uychi tumani", "slots": 1, "salary": "Kelishiladi"},
    ]
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    for s in samples:
        print(make_card(s, f"{out}/namuna_{s['id']}.jpg"))
