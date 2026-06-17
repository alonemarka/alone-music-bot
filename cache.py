import os
import hashlib
from yt_dlp import YoutubeDL

from config import DOWNLOAD_DIR

def get_cache_path(query):
    safe_name = hashlib.md5(query.lower().encode()).hexdigest()
    return os.path.join(DOWNLOAD_DIR, f"{safe_name}.mp3")

def is_cached(query):
    return os.path.exists(get_cache_path(query))
