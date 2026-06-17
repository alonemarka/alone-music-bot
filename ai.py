from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

async def ai_cevap(soru):
    if not client:
        return "AI şu anda kullanılamıyor."
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": soru}],
            temperature=0.8,
            max_tokens=600
        )
        return completion.choices[0].message.content
    except:
        return "AI ile ilgili bir hata oluştu."
