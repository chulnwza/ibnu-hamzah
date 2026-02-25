"""
API Client for fetching Quran audio URLs.

This module provides asynchronous API calls to fetch audio URLs
from the Quran.com API (for full surahs) and the Aladhan API (for specific ayahs).
"""
import aiohttp

# Central mapping for reciters to their respective API IDs and Names
RECITER_MAPPING = {
    "alafasy": {"name": "Mishary Rashid Alafasy", "description": "Kuwait", "quran_com": 7, "aladhan": "ar.alafasy"},
    "husary": {"name": "Mahmoud Khalil Al-Husary", "description": "Egypt", "quran_com": 6, "aladhan": "ar.husary"},
    "abdulsamad": {"name": "AbdulBaset AbdulSamad", "description": "Egypt", "quran_com": 1, "aladhan": "ar.abdulsamad"},
    "sudais": {"name": "Abdur-Rahman as-Sudais", "description": "Mecca", "quran_com": 3, "aladhan": "ar.abdurrahmaansudais"},
    "shuraym": {"name": "Saud Al-Shuraim", "description": "Mecca", "quran_com": 12, "aladhan": "ar.saoodshuraym"},
    "maher": {"name": "Maher Al-Muaiqly", "description": "Mecca", "quran_com": 11, "aladhan": "ar.mahermuaiqly"},
    "shaatree": {"name": "Abu Bakr al-Shatri", "description": "Saudi Arabia", "quran_com": 4, "aladhan": "ar.shaatree"},
    "ajamy": {"name": "Ahmed ibn Ali al-Ajamy", "description": "Saudi Arabia", "quran_com": 2, "aladhan": "ar.ahmedajamy"},
    "rifai": {"name": "Hani ar-Rifai", "description": "Saudi Arabia", "quran_com": 5, "aladhan": "ar.hanirifai"},
    "hudhaify": {"name": "Ali Alhuthaifi", "description": "Medina", "quran_com": 8, "aladhan": "ar.hudhaify"},
    "minshawi": {"name": "Muhammad Siddiq al-Minshawi", "description": "Egypt", "quran_com": 11, "aladhan": "ar.minshawi"},
    "ayyoub": {"name": "Muhammad Ayyub", "description": "Medina", "quran_com": 9, "aladhan": "ar.muhammadayyoub"},
    "jibreel": {"name": "Muhammad Jibreel", "description": "Egypt", "quran_com": 10, "aladhan": "ar.muhammadjibreel"},
    "basfar": {"name": "Abdullah Basfar", "description": "Saudi Arabia", "quran_com": 7, "aladhan": "ar.abdullahbasfar"},
    "akhbar": {"name": "Ibrahim Al Akhdar", "description": "Saudi Arabia", "quran_com": 7, "aladhan": "ar.ibrahimakhbar"},
    "parhizgar": {"name": "Shahriar Parhizgar", "description": "Iran", "quran_com": 7, "aladhan": "ar.parhizgar"},
    "aymanswoaid": {"name": "Ayman Sowaid", "description": "Saudi Arabia", "quran_com": 7, "aladhan": "ar.aymanswoaid"},
    "husarymujawwad": {"name": "Al-Husary (Mujawwad)", "description": "Egypt", "quran_com": 6, "aladhan": "ar.husarymujawwad"},
    "minshawimujawwad": {"name": "Al-Minshawi (Mujawwad)", "description": "Egypt", "quran_com": 11, "aladhan": "ar.minshawimujawwad"},
    "abdulbasit": {"name": "AbdulBaset (Murattal)", "description": "Egypt", "quran_com": 2, "aladhan": "ar.abdulbasitmurattal"},
}

# Central mapping for text translations
TRANSLATION_MAPPING = {
    "none": {"name": "❌ ไม่แปล (No Translation)", "aladhan": None},
    "th.thai": {"name": "🇹🇭 ภาษาไทย (Thai)", "aladhan": "th.thai"},
    "en.sahih": {"name": "🇬🇧 English", "aladhan": "en.sahih"},
    "id.indonesian": {"name": "🇮🇩 Indonesian", "aladhan": "id.indonesian"},
    "ms.basmeih": {"name": "🇲🇾 Malay", "aladhan": "ms.basmeih"},
    "ur.jandali": {"name": "🇵🇰 Urdu", "aladhan": "ur.jandali"},
    "fr.hamidullah": {"name": "🇫🇷 French", "aladhan": "fr.hamidullah"},
    "es.cortes": {"name": "🇪🇸 Spanish", "aladhan": "es.cortes"},
    "ru.kuliev": {"name": "🇷🇺 Russian", "aladhan": "ru.kuliev"},
    "zh.jian": {"name": "🇨🇳 Chinese", "aladhan": "zh.jian"},
    "tr.diyanet": {"name": "🇹🇷 Turkish", "aladhan": "tr.diyanet"},
}

async def get_full_surah_audio(surah_number: int, reciter_id: int) -> str:
    """
    Fetches the full surah audio URL from the Quran.com API.
    """
    url = f"https://api.quran.com/api/v4/chapter_recitations/{reciter_id}/{surah_number}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                audio_file = data.get("audio_file", {})
                return audio_file.get("audio_url", "")
            else:
                raise Exception(f"Quran.com API returned status {response.status}")

async def get_ayah_audio(surah_number: int, ayah_number: int, reciter_string: str) -> str:
    """
    Fetches the audio URL for a specific Ayah from the Aladhan (AlQuran.cloud) API.
    """
    url = f"https://api.alquran.cloud/v1/ayah/{surah_number}:{ayah_number}/{reciter_string}"
    print(f"DEBUG: Requesting URL: {url}")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("data", {}).get("audio", "")
            else:
                error_text = await response.text()
                raise Exception(f"AlQuran.cloud API returned status {response.status}: {error_text}")

async def get_translation_text(surah_number: int, ayah_number: int, lang_code: str) -> str:
    """
    Fetches the translation text for a specific Ayah from the AlQuran.cloud API.
    """
    url = f"https://api.alquran.cloud/v1/ayah/{surah_number}:{ayah_number}/{lang_code}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("data", {}).get("text", "")
            else:
                error_text = await response.text()
                raise Exception(f"AlQuran.cloud Translation API returned status {response.status}: {error_text}")
