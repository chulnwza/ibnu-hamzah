"""
API Client for fetching Quran audio URLs.

This module provides asynchronous API calls to fetch audio URLs
from the Quran.com API (for full surahs) and the Aladhan API (for specific ayahs).
"""
import aiohttp

# Central mapping for reciters to their respective API IDs
# Central mapping for reciters to their respective API IDs
RECITER_MAPPING = {
    "husary": {"quran_com": 6, "aladhan": "ar.husary"},
    "mishary": {"quran_com": 7, "aladhan": "ar.alafasy"},
    "ghamidi": {"quran_com": 5, "aladhan": "ar.saadghamidi"},
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
