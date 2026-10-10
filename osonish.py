"""osonish.uz'dan vakansiyalarni olish (faqat ochiq sahifalar; /api/ ishlatilmaydi — robots.txt)."""
import re, time, datetime as dt
import requests
from bs4 import BeautifulSoup

BASE = "https://osonish.uz"
UA = {"User-Agent": "KaryeraUzBot/1.0 (+https://t.me/karyerauznamangan)"}
DELAY = 1.2  # robots.txt: Crawl-delay 1

REGION_KEYS = ["namangan", "наманган"]
NAMANGAN_DISTRICTS = ["namangan", "chust", "chortoq", "kosonsoy", "mingbuloq", "norin", "pop tumani",
                      "to'raqo'rg'on", "uchqo'rg'on", "uychi", "yangiqo'rg'on", "davlatobod"]

def _get(url):
    r = requests.get(url, headers=UA, timeout=30)
    r.raise_for_status()
    time.sleep(DELAY)
    return r.text

def sitemap_ids():
    """sitemap/vacancies.xml dagi barcha vakansiya ID'lari (o'sish tartibida)."""
    xml = _get(f"{BASE}/sitemap/vacancies.xml")
    return sorted({int(m) for m in re.findall(r"/vacancies/(\d+)</loc>", xml)})

def _clean(s):
    return re.sub(r"\s+", " ", s or "").strip()

def _apos(s):
    return s.replace("`", "'").replace("ʻ", "'").replace("’", "'").replace("‘", "'").replace("ʼ", "'")

def _title_case(s):
    s = _apos(s).lower()
    return re.sub(r"(^|\s|-)([a-zа-яё'])", lambda m: m.group(1) + m.group(2).upper(), s, count=0) \
        .replace("-Umumiy", "-umumiy")

# osonish.uz call-markazi raqamlari — postga qo'shilmaydi
HOTLINES = {"+998 71 200 01 40", "+998 71 203 01 40", "+998 71 204 01 40"}

LABELS = {
    "kasb": "Kasb yoki lavozim nomi",
    "slots": "Vakansiyalar soni",
    "experience": "Ish tajribasi",
    "pay_form": "To'lov shakli",
    "employment": "Bandlik turi",
    "mode": "Ish usuli (rejimi)",
    "schedule": "Ish kunlari va vaqti",
    "education": "Ma'lumot darajasi",
    "gender": "Jinsi",
    "address": "Ish joy manzili",
}

def _rel_date(s, today=None):
    today = today or dt.date.today()
    s = _apos(s).lower()
    if "bugun" in s: return today.strftime("%d.%m.%Y")
    if "kecha" in s: return (today - dt.timedelta(days=1)).strftime("%d.%m.%Y")
    m = re.search(r"(\d+)\s*kun", s)
    if m: return (today - dt.timedelta(days=int(m.group(1)))).strftime("%d.%m.%Y")
    m = re.search(r"(\d{1,2})[./](\d{1,2})[./](\d{4})", s)
    if m: return f"{int(m.group(1)):02d}.{int(m.group(2)):02d}.{m.group(3)}"
    return today.strftime("%d.%m.%Y")

def parse_vacancy(html, vid, today=None):
    soup = BeautifulSoup(html, "html.parser")
    lines = [_clean(_apos(x)) for x in soup.get_text("\n").split("\n")]
    lines = [x for x in lines if x]
    v = {"id": vid, "url": f"{BASE}/vacancies/{vid}"}

    def after(label):
        for i, ln in enumerate(lines):
            if ln.lower().startswith(label.lower()):
                rest = ln[len(label):].lstrip(" :")
                if rest: return rest
                return lines[i + 1] if i + 1 < len(lines) else ""
        return ""

    for k, lab in LABELS.items():
        v[k] = after(lab)

    h1 = soup.find("h1")
    og = soup.find("meta", property="og:title")
    v["title"] = _clean(_apos(h1.get_text() if h1 else (og["content"] if og else v["kasb"])))

    comp = soup.find("a", href=re.compile(r"/companies/\d+"))
    v["org"] = _title_case(_clean(comp.get_text())) if comp else ""

    v["district"] = next((ln for ln in lines if re.search(r"(tumani|shahri)$", ln, re.I) and len(ln) < 40), "")
    sal = next((ln for ln in lines if re.search(r"\d[\d\s]*so'm", ln)), "")
    if not sal:
        sal = next((ln for ln in lines if "kelishil" in ln.lower()), "Kelishiladi")
    v["salary"] = sal.replace("so'mdan", "so'mdan boshlab") if sal else "Kelishiladi"

    phones = []
    for ln in lines:
        for p in re.findall(r"\+998[\s()\d-]{9,}", ln):
            p = re.sub(r"\D", "", p)
            if len(p) == 12:
                f = f"+{p[:3]} {p[3:5]} {p[5:8]} {p[8:10]} {p[10:]}"
                if f not in phones and f not in HOTLINES: phones.append(f)
    v["phones"] = phones
    v["contact_name"] = after("Mas'ul shaxs") or after("Aloqa uchun") or ""

    dl = next((ln for ln in lines if ln.lower().startswith("e'lon qilingan")), "")
    v["date"] = _rel_date(dl, today)

    try:
        v["slots"] = int(re.sub(r"\D", "", v["slots"]) or 1)
    except ValueError:
        v["slots"] = 1
    v["is_region"] = any(k in v["address"].lower() for k in REGION_KEYS) or \
        any(d in v["district"].lower() for d in NAMANGAN_DISTRICTS)
    return v

def fetch_vacancy(vid):
    return parse_vacancy(_get(f"{BASE}/vacancies/{vid}"), vid)
