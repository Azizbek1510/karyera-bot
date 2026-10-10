"""Telegram Bot API uchun minimal mijoz (kutubxonasiz)."""
import json, os, requests

TOKEN = os.environ.get("BOT_TOKEN", "")
API = f"https://api.telegram.org/bot{TOKEN}/"

def call(method, files=None, **params):
    data = {k: (json.dumps(v) if isinstance(v, (dict, list)) else v) for k, v in params.items() if v is not None}
    r = requests.post(API + method, data=data, files=files, timeout=60)
    res = r.json()
    if not res.get("ok"):
        raise RuntimeError(f"{method}: {res}")
    return res["result"]

def review_kb(vid):
    return {"inline_keyboard": [
        [{"text": "✅ Tasdiqlash", "callback_data": f"ok:{vid}"},
         {"text": "❌ Rad etish", "callback_data": f"no:{vid}"}],
        [{"text": "✏️ Tahrirlash", "callback_data": f"ed:{vid}"},
         {"text": "🔄 Boshqa rasm", "callback_data": f"im:{vid}"}],
    ]}

def status_kb(text):
    return {"inline_keyboard": [[{"text": text, "callback_data": "noop"}]]}

def send_photo(chat_id, path, caption, kb=None):
    with open(path, "rb") as f:
        return call("sendPhoto", files={"photo": f}, chat_id=chat_id, caption=caption,
                    parse_mode="HTML", reply_markup=kb)

def replace_photo(chat_id, msg_id, path, caption, kb):
    with open(path, "rb") as f:
        media = {"type": "photo", "media": "attach://p", "caption": caption, "parse_mode": "HTML"}
        return call("editMessageMedia", files={"p": f}, chat_id=chat_id, message_id=msg_id,
                    media=media, reply_markup=kb)
