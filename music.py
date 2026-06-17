import os
import hashlib
from yt_dlp import YoutubeDL
from config import DOWNLOAD_DIR

def get_cache_path(query: str) -> str:
    """Şarkı adına göre cache dosya yolu oluştur"""
    safe_name = hashlib.md5(query.lower().strip().encode()).hexdigest()
    return os.path.join(DOWNLOAD_DIR, f"{safe_name}.mp3")

def is_cached(query: str) -> bool:
    """Şarkı cache'de var mı kontrol et"""
    return os.path.exists(get_cache_path(query))

async def download_music(query: str) -> str:
    """Müzik indir veya cache'den al"""
    file_path = get_cache_path(query)
    
    if is_cached(query):
        print(f"[CACHE] {query} cache'den oynatılıyor.")
        return file_path
    
    print(f"[DOWNLOAD] {query} indiriliyor...")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': file_path,
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'default_search': 'ytsearch',
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([query])
        print(f"[SUCCESS] {query} indirildi.")
        return file_path
    except Exception as e:
        print(f"[ERROR] İndirme hatası: {e}")
        return None
