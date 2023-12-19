from config import Config 
try:
    import pyrogram, kvsqlite
except:
    import os; os.system("pip install pyrogram kvsqlite")
from pyrogram import Client, filters
from pyrogram.types import *
import re, kvsqlite, random, pyrogram
db = kvsqlite.sync.Client("u.sqlite")

def search_name(name, data):
    best_results = []
    best_score = 0

    for item in data:
        item_name = item["name"]
        score = similarity_score(name, item_name)
        if score > best_score:
            best_score = score
            best_results = [item]
        elif score == best_score:
            best_results.append(item)

    return best_results

def similarity_score(name1, name2):
    
    pattern = re.escape(name1)
    match = re.search(pattern, name2, re.IGNORECASE)
    if match:
        return match.end() - match.start()
    return 0

api_hash = Config.API_HASH #ايبي هاش 
api_id = Config.APP_ID #ايبي ايدي
token = Config.TG_BOT_TOKEN #البوت

def create_voice_results(file_ids):
    results = []
    for file_id in file_ids:
        result = InlineQueryResultCachedVoice(
            voice_file_id=file_id["id"],
            title=file_id["name"],
            caption=file_id["name"],
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Dev", url="trprogram.t.me")]])
        )
        results.append(result)
    return results
@app.on_message(filters.voice)
def rvoice(app, m):
    if m:
        f = m.voice.file_id
        for i in db.get("audios"):
            if str(i["id"]) == str(f): return m.reply("الفويس مرفوع من قبل !!")
        db.set(f"temp_{m.from_user.id}_g", f)
        m.reply("ارسل العنوان لفويسك، لايتخطى 40 حرف")
        return
@app.on_message(filters.text)
def rtext(app, m):
    if m.text  == "/start":
        if not db.exists("audios"):
            db.set("audios", [])
        db.delete(f"temp_{m.from_user.id}_g")
        m.reply("اهلا بك،\n- ارسل لي فويس واتبع الخطوات!\n⎯ ⎯ ⎯ ⎯")
        return
    if m:
        if db.exists(f"temp_{m.from_user.id}_g"):
            id = db.get(f"temp_{m.from_user.id}_g")
            d = db.get("audios")
            d.append({"id":id, "name":m.text[:40]})
            db.set("audios",d)
            db.delete(f"temp_{m.from_user.id}_g")
            username = None
            try:
                t = app.get_me()
                username = t.username
            except:
                return
            m.reply(f"تمت بنجاح ..\n<code>@{username} {m.text[:40]}</code>")
            return
@app.on_inline_query()
def inline_query_handler(client: Client, query: InlineQuery):
    
    query_string = query.query.lower().strip()
    d = db.get("audios")
    if not d: return
    if not query_string:
        e = create_voice_results(d[:20])
        client.answer_inline_query(query.id, e)
    s = search_name(query_string, d)[:10]
    if not s: return
    e = create_voice_results(s)
    if not e: return
    client.answer_inline_query(query.id, e)
app.run()
