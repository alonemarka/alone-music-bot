from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.types import AudioPiped
import asyncio
import aiohttp

from config import API_ID, API_HASH, BOT_TOKEN, ADMIN_ID
from music import download_music, is_cached, get_cache_path
from database import log_play
from ai import ai_cevap

app = Client("AloneMusic", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call = PyTgCalls(app)

# Queue ve durum
queue = {}
is_playing = {}

# ====================== DUYURU SİSTEMİ ======================
last_announcement_id = 0
API_DUYURU_URL = "https://alonesocial.rf.gd//api/duyuru.php"

async def check_announcements():
    global last_announcement_id
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_DUYURU_URL}?last_id={last_announcement_id}") as resp:
                data = await resp.json()
                
                if data.get('success') and data.get('announcements'):
                    for duyuru in reversed(data['announcements']):
                        print(f"[DUYURU] {duyuru['message']}")
                        # İstersen tüm gruplara gönderebilirsin:
                        # await app.send_message(chat_id, f"📢 **AloneMusic Duyuru**\n\n{duyuru['message']}")
                    
                    if data['announcements']:
                        last_announcement_id = data['announcements'][0]['id']
    except:
        pass

async def announcement_checker():
    while True:
        await check_announcements()
        await asyncio.sleep(30)

# ====================== KOMUTLAR ======================

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply("**AloneMusic Bot**\n\n`/oynat <şarkı adı>` yazarak müzik çal.")

@app.on_message(filters.command("oynat"))
async def oynat(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("**Kullanım:** `/oynat <şarkı adı veya link>`")
    
    query = " ".join(message.command[1:])
    chat_id = message.chat.id

    await message.reply(f"**Aranıyor:** `{query}`")

    try:
        if not is_cached(query):
            await message.reply("**İndiriliyor...** Bekleyin.")
            file_path = await download_music(query)
            if not file_path:
                return await message.reply("İndirme başarısız.")
        else:
            file_path = get_cache_path(query)
            await message.reply("**Cache'den oynatılıyor** ✅")

        log_play(query, file_path)

        if chat_id not in is_playing or not is_playing[chat_id]:
            await call.join_group_call(
                chat_id,
                AudioPiped(file_path),
                stream_type=StreamType().local_stream
            )
            is_playing[chat_id] = True
            await message.reply(f"**Şimdi Çalıyor:** `{query}`")
        else:
            if chat_id not in queue:
                queue[chat_id] = []
            queue[chat_id].append(file_path)
            await message.reply(f"**Sıraya eklendi:** `{query}`")

    except Exception as e:
        await message.reply(f"**Hata:** {str(e)}")

@app.on_message(filters.command(["atla", "skip"]))
async def atla(client, message: Message):
    chat_id = message.chat.id
    try:
        await call.leave_group_call(chat_id)
        is_playing[chat_id] = False
        await message.reply("**Atlandı.**")
        
        if chat_id in queue and queue[chat_id]:
            next_file = queue[chat_id].pop(0)
            await call.join_group_call(chat_id, AudioPiped(next_file), stream_type=StreamType().local_stream)
            is_playing[chat_id] = True
    except:
        await message.reply("Şu anda çalan bir şey yok.")

@app.on_message(filters.command("durdur"))
async def durdur(client, message: Message):
    chat_id = message.chat.id
    try:
        await call.leave_group_call(chat_id)
        is_playing[chat_id] = False
        queue[chat_id] = []
        await message.reply("**Sesli sohbetten çıkıldı.**")
    except:
        await message.reply("Zaten sesli sohbette değilim.")

@app.on_message(filters.command("sor"))
async def sor(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("**Kullanım:** `/sor <soru>`")
    soru = " ".join(message.command[1:])
    cevap = await ai_cevap(soru)
    await message.reply(cevap)

@app.on_message(filters.text & ~filters.command)
async def ai_chat(client, message: Message):
    text = message.text.lower()
    if message.chat.type == "private" or text.startswith("alone") or text.startswith("bot"):
        cevap = await ai_cevap(message.text)
        await message.reply(cevap)

# ====================== BAŞLATMA ======================
async def main():
    await app.start()
    await call.start()
    print("✅ AloneMusic Bot Başarıyla Çalışıyor!")
    
    # Duyuru checker
    asyncio.create_task(announcement_checker())
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
