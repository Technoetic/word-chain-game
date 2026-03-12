"""CLOVA Voice TTS — converts text to speech via NCP API.

Tries Premium endpoint first, falls back to standard CSS endpoint.
"""

import httpx

CLOVA_TTS_PREMIUM_URL = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"
CLOVA_TTS_CSS_URL = "https://naveropenapi.apigw.ntruss.com/voice/v1/tts"

PREMIUM_SPEAKERS = {"nara", "nara_call", "nminsang", "nhajun", "ndain", "njiyun", "nsujin", "jinho", "clara"}
CSS_SPEAKERS = {"mijin", "jinho"}


async def synthesize(
    text: str,
    client_id: str,
    client_secret: str,
    speaker: str = "nara",
    speed: int = 0,
    volume: int = 0,
    pitch: int = 0,
) -> bytes:
    """Return mp3 audio bytes for the given text."""
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "speaker": speaker,
        "text": text,
        "speed": str(speed),
        "volume": str(volume),
        "pitch": str(pitch),
        "format": "mp3",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        # Try Premium first
        resp = await client.post(CLOVA_TTS_PREMIUM_URL, headers=headers, data=data)
        if resp.status_code == 200:
            return resp.content

        # Fallback to CSS with mijin speaker
        print(f"[TTS] Premium failed ({resp.status_code}), trying CSS endpoint")
        data["speaker"] = "mijin"
        resp = await client.post(CLOVA_TTS_CSS_URL, headers=headers, data=data)
        resp.raise_for_status()
        return resp.content
