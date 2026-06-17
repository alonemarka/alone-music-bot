from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.types import AudioPiped
from yt_dlp import YoutubeDL
import asyncio
import os
from config import API_ID, API_HASH, BOT_TOKEN, ADMIN_ID, DOWNLOAD_DIR
from cache import get_cache_path, is_cached
from database import log_play
from ai import ai_cevap

app = Client("AloneMusic", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call = PyTgCalls(app)

queue = {}
is_playing = {}

# ====================== KOMUTLAR ======================

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply("**AloneMusic Bot**\n\nMüzik çalmak için `/oynat şarkı adı` yaz.")

@app.on_message(filters.command("oynat"))
async def oynat(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Kullanım: `/oynat <şarkı adı>`")
    
    query = " ".join(message.command[1:])
    chat_id = message.chat.id
    
    await message.reply(f"**Aranıyor:** `{query}`")
    
    try:
        file_path = get_cache_path(query)
        
        if not is_cached(query):
            await message.reply("İndiriliyor, lütfen bekle...")
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': file_path,
                'quiet': True,
            }
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{query}", download=True)
                title = info.get('title', query)
        else:
            title = query
        
        log_play(query, file_path)
        
        # Sesli sohbete katıl
        if chat_id not in is_playing or not is_playing[chat_id]:
            await call.join_group_call(
                chat_id,
                AudioPiped(file_path),
                stream_type=StreamType().local_stream
            )
            is_playing[chat_id] = True
            await message.reply(f"**Şimdi Çalıyor:** `{title}`")
        else:
            # Queue'ya ekle (basit queue)
            if chat_id not in queue:
                queue[chat_id] = []
            queue[chat_id].append(file_path)
            await message.reply(f"**Sıraya eklendi:** `{title}`")
            
    except Exception as e:
        await message.reply(f"Hata: {str(e)}")

@app.on_message(filters.command("atla"))
async def atla(client, message: Message):
    chat_id = message.chat.id
    try:
        await call.change_stream(chat_id, AudioPiped("next"))  # Basit atlama
        await message.reply("Şarkı atlandı.")
    except:
        await message.reply("Şu anda bir şey çalmıyor.")

@app.on_message(filters.command("durdur"))
async def durdur(client, message: Message):
    chat_id = message.chat.id
    try:
        await call.leave_group_call(chat_id)
        is_playing[chat_id] = False
        await message.reply("Sesli sohbetten çıkıldı.")
    except:
        await message.reply("Zaten sesli sohbette değilim.")

@app.on_message(filters.command("sor"))
async def sor(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Kullanım: `/sor Merhaba nasılsın?`")
    soru = " ".join(message.command[1:])
    cevap = await ai_cevap(soru)
    await message.reply(cevap)

# ====================== AI SOHBET ======================
@app.on_message(filters.text & ~filters.command)
async def ai_chat(client, message: Message):
    if message.chat.type == "private" or message.text.lower().startswith("alone"):
        cevap = await ai_cevap(message.text)
        await message.reply(cevap)

# ====================== BAŞLAT ======================
async def main():
    await app.start()
    await call.start()
    print("✅ AloneMusic Bot Çalışıyor...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
