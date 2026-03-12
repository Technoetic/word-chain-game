"""CLOVA Voice TTS — converts text to speech via NCP API."""

import httpx

CLOVA_TTS_URL = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"


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
        resp = await client.post(CLOVA_TTS_URL, headers=headers, data=data)
        resp.raise_for_status()
        return resp.content
