"""Vakansiyani kanal shabloni bo'yicha post matniga aylantirish (Telegram HTML)."""
import html, re

CHANNEL_LINK = "https://t.me/karyerauznamangan"

def _sched(s):
    """'6/1, 08:00 - 17:00' -> 'haftasiga 6 kun ish, 1 kun dam, 08:00–17:00'"""
    m = re.match(r"\s*(\d)\s*/\s*(\d)\s*,?\s*(.*)", s or "")
    if not m:
        return s or "Kelishiladi"
    t = re.sub(r"\s*-\s*", "–", m.group(3).strip())
    return f"haftasiga {m.group(1)} kun ish, {m.group(2)} kun dam" + (f", {t}" if t else "")

def _edu(s):
    return re.sub(r"\s*\(", " (", s or "Ahamiyatsiz")

def _place(v):
    reg, dist = v.get("region") or "", v.get("district") or ""
    if reg and dist and reg.split()[0].lower() not in dist.lower():
        return f"{reg}, {dist}"
    return dist or reg or "O'zbekiston"

def build_text(v):
    e = lambda s: html.escape(str(s), quote=False)
    contact = ", ".join(x for x in [v.get("contact_name"), ", ".join(v.get("phones", [])[:2])] if x) or "osonish.uz orqali"
    lines = [
        f"🎓 <b>{e(v['title'].upper())}</b>",
        "",
        f"🏢 {e(v.get('org') or '—')}",
        f"📍 {e(_place(v))}",
        f"👥 Bo'sh o'rinlar: {v.get('slots', 1)} ta",
        f"🎓 Ma'lumot: {e(_edu(v.get('education')))}",
        f"⏳ Tajriba: {e((v.get('experience') or 'Talab etilmaydi').replace('-', '–'))}",
        f"💰 Maosh: {e(v.get('salary') or 'Kelishiladi')}",
        f"📋 Ish turi: {e((v.get('employment') or 'doimiy').lower())}",
        f"🕗 Ish tartibi: {e(_sched(v.get('schedule')))}",
        f"📞 Bog'lanish: {e(contact)}",
        f"🗓 E'lon sanasi: {e(v.get('date', ''))}",
        "",
        f"📝 Ariza topshirish: {e(v['url'])}",
        "",
        "",
        "👉 <b>KANALGA HOZIROQ OBUNA BO'LING:</b>",
        f"🔗 {CHANNEL_LINK}",
    ]
    return "\n".join(lines)
