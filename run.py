"""Bitta ishga tushirish sikli (GitHub Actions har ~10 daqiqada chaqiradi):
1) admin tugmalari va tahrirlarni qayta ishlash;
2) osonish.uz'dan yangi Namangan vakansiyalarini olib, admin chatga tekshiruvga yuborish.

Ishlatish:
  python run.py                 # oddiy sikl
  python run.py --test 116052   # bitta vakansiyani tahlil qilib, matnini chiqarish (Telegramsiz)
"""
import json, os, sys, tempfile, traceback
import osonish, post, card, tg

STATE_FILE = os.environ.get("STATE_FILE", "state.json")
ADMIN_CHAT = os.environ.get("ADMIN_CHAT_ID", "")
CHANNEL = os.environ.get("CHANNEL_ID", "@karyerauznamangan")
MAX_FETCH = int(os.environ.get("MAX_FETCH", "350"))        # bir siklda ko'riladigan max sahifa
INITIAL_SCAN = int(os.environ.get("INITIAL_SCAN", "300"))  # birinchi ishga tushishda oxirgi N ta e'lon
CAPTION_LIMIT = 1024

def load():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {"last_id": None, "offset": 0, "posts": {}, "awaiting": {}}

def save(st):
    # eski yakunlangan postlarni tozalash (fayl o'sib ketmasin)
    done = [k for k, p in st["posts"].items() if p["status"] != "pending"]
    for k in sorted(done, key=int)[:-500]:
        st["posts"].pop(k)
    with open(STATE_FILE, "w") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)

def _img(v, variant):
    path = os.path.join(tempfile.gettempdir(), f"v{v['id']}_{variant}.jpg")
    return card.make_card(v, path, variant=variant)

def _safe(fn, *a, **k):
    try:
        return fn(*a, **k)
    except Exception as e:
        print("XATO:", e)

# ---------- 1. Admin harakatlari ----------
def handle_updates(st):
    ups = tg.call("getUpdates", offset=st["offset"], timeout=0,
                  allowed_updates=["callback_query", "message"])
    for u in ups:
        st["offset"] = u["update_id"] + 1
        try:
            if "callback_query" in u:
                on_button(st, u["callback_query"])
            elif "message" in u:
                on_message(st, u["message"])
        except Exception:
            traceback.print_exc()

def on_button(st, q):
    msg = q.get("message", {})
    if str(msg.get("chat", {}).get("id")) != str(ADMIN_CHAT):
        return
    act, _, vid = q.get("data", "").partition(":")
    p = st["posts"].get(vid)
    _safe(tg.call, "answerCallbackQuery", callback_query_id=q["id"])
    if not p or p["status"] != "pending":
        return
    who = q["from"].get("first_name", "admin")
    if act == "ok":
        tg.call("copyMessage", chat_id=CHANNEL, from_chat_id=ADMIN_CHAT, message_id=p["msg_id"])
        p["status"] = "posted"
        tg.call("editMessageReplyMarkup", chat_id=ADMIN_CHAT, message_id=p["msg_id"],
                reply_markup=tg.status_kb(f"✅ Kanalga joylandi ({who})"))
    elif act == "no":
        p["status"] = "rejected"
        tg.call("editMessageReplyMarkup", chat_id=ADMIN_CHAT, message_id=p["msg_id"],
                reply_markup=tg.status_kb(f"❌ Rad etildi ({who})"))
    elif act == "ed":
        m = tg.call("sendMessage", chat_id=ADMIN_CHAT, reply_to_message_id=p["msg_id"],
                    text=f"✏️ ID {vid}: postning yangi matnini shu xabarga JAVOB (reply) qilib yuboring.\n"
                         "Maslahat: post matnini nusxalab, tahrirlab yuboring — formatlash saqlanadi.",
                    reply_markup={"force_reply": True, "selective": True})
        st["awaiting"][str(m["message_id"])] = vid
    elif act == "im":
        p["variant"] = p.get("variant", 0) + 1
        path = _img(p["v"], p["variant"])
        with open(path, "rb") as f:
            media = {"type": "photo", "media": "attach://p", "caption": p["caption"]}
            if p.get("entities"):
                media["caption_entities"] = p["entities"]
            else:
                media["parse_mode"] = "HTML"
            tg.call("editMessageMedia", files={"p": f}, chat_id=ADMIN_CHAT, message_id=p["msg_id"],
                    media=media, reply_markup=tg.review_kb(vid))

def on_message(st, m):
    if str(m.get("chat", {}).get("id")) != str(ADMIN_CHAT):
        return
    rep = m.get("reply_to_message")
    if not rep or str(rep["message_id"]) not in st["awaiting"]:
        return
    vid = st["awaiting"].pop(str(rep["message_id"]))
    p = st["posts"].get(vid)
    text = m.get("text") or m.get("caption")
    if not p or p["status"] != "pending" or not text:
        return
    if len(text) > CAPTION_LIMIT:
        tg.call("sendMessage", chat_id=ADMIN_CHAT, reply_to_message_id=m["message_id"],
                text=f"⚠️ Matn juda uzun ({len(text)} belgi, ruxsat {CAPTION_LIMIT}). Qisqartirib qayta yuboring.")
        st["awaiting"][str(rep["message_id"])] = vid
        return
    ents = m.get("entities") or m.get("caption_entities") or []
    tg.call("editMessageCaption", chat_id=ADMIN_CHAT, message_id=p["msg_id"], caption=text,
            caption_entities=ents, reply_markup=tg.review_kb(vid))
    p["caption"], p["entities"] = text, ents
    _safe(tg.call, "deleteMessage", chat_id=ADMIN_CHAT, message_id=rep["message_id"])
    _safe(tg.call, "setMessageReaction", chat_id=ADMIN_CHAT, message_id=m["message_id"],
          reaction=[{"type": "emoji", "emoji": "👍"}])

# ---------- 2. Yangi vakansiyalar ----------
def scrape(st):
    ids = osonish.sitemap_ids()
    if not ids:
        return
    if st["last_id"] is None:
        todo = ids[-INITIAL_SCAN:]
    else:
        todo = [i for i in ids if i > st["last_id"]]
    todo = todo[:MAX_FETCH]
    print(f"Ko'rib chiqiladi: {len(todo)} ta e'lon")
    for vid in todo:
        try:
            v = osonish.fetch_vacancy(vid)
        except Exception as e:
            print(f"{vid}: o'tkazildi ({e})")
            st["last_id"] = vid
            continue
        st["last_id"] = vid
        if not v["is_region"] or str(vid) in st["posts"]:
            continue
        caption = post.build_text(v)
        m = tg.send_photo(ADMIN_CHAT, _img(v, 0), caption, tg.review_kb(vid))
        st["posts"][str(vid)] = {"msg_id": m["message_id"], "status": "pending", "variant": 0,
                                 "caption": m.get("caption", caption), "entities": m.get("caption_entities"),
                                 "v": v}
        save(st)  # har postdan keyin saqlash — uzilib qolsa ham takrorlanmaydi
        print(f"{vid}: tekshiruvga yuborildi — {v['title']}")

def main():
    if "--test" in sys.argv:
        vid = int(sys.argv[sys.argv.index("--test") + 1])
        html_ = osonish._get(f"{osonish.BASE}/vacancies/{vid}")
        open(f"test_{vid}.html", "w").write(html_)
        v = osonish.parse_vacancy(html_, vid)
        print(json.dumps(v, ensure_ascii=False, indent=1))
        print("\n" + post.build_text(v))
        print("\nRasm:", card.make_card(v, f"test_{vid}.jpg"))
        return
    assert tg.TOKEN and ADMIN_CHAT, "BOT_TOKEN va ADMIN_CHAT_ID sozlanmagan"
    st = load()
    try:
        handle_updates(st)
        save(st)
        scrape(st)
        handle_updates(st)  # skrayping vaqtida bosilgan tugmalar ham ishlansin
    finally:
        save(st)

if __name__ == "__main__":
    main()
