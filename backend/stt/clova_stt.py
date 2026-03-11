"""CLOVA Speech Recognition (CSR) STT proxy.

Receives PCM audio chunks via WebSocket from the frontend,
buffers them, and periodically sends to CLOVA CSR REST API.
Returns interim (buffered partial) and final results back to the client.
"""

import asyncio
import io
import struct
import wave
import httpx
from fastapi import WebSocket, WebSocketDisconnect

CLOVA_CSR_URL = "https://naveropenapi.apigw.ntruss.com/recog/v1/stt"
SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_WIDTH = 2  # 16-bit

# Send audio to CLOVA every N seconds of accumulated audio
CHUNK_INTERVAL_SEC = 1.5
# Minimum audio duration (seconds) to bother sending
MIN_AUDIO_SEC = 0.3


def _pcm_to_wav(pcm_data: bytes) -> bytes:
    """Wrap raw PCM bytes in a WAV header."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(SAMPLE_WIDTH)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm_data)
    return buf.getvalue()


async def _recognize(wav_data: bytes, client_id: str, client_secret: str) -> str | None:
    """Call CLOVA CSR REST API and return recognized text."""
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
        "Content-Type": "application/octet-stream",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            f"{CLOVA_CSR_URL}?lang=Kor",
            headers=headers,
            content=wav_data,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("text", "")
        else:
            print(f"[CLOVA STT] API error {resp.status_code}: {resp.text}")
            return None


async def handle_stt_session(websocket: WebSocket, client_id: str, client_secret: str):
    """Proxy audio between frontend WebSocket and CLOVA CSR REST API."""
    print(f"[CLOVA STT] session started, client_id={'SET' if client_id else 'EMPTY'}")
    await websocket.accept()

    audio_buffer = bytearray()
    lock = asyncio.Lock()
    running = True
    last_text = ""

    async def recognition_loop():
        """Periodically send buffered audio to CLOVA for recognition."""
        nonlocal audio_buffer, running, last_text

        while running:
            await asyncio.sleep(CHUNK_INTERVAL_SEC)
            if not running:
                break

            async with lock:
                if len(audio_buffer) < int(MIN_AUDIO_SEC * SAMPLE_RATE * SAMPLE_WIDTH):
                    continue
                pcm_snapshot = bytes(audio_buffer)

            wav_data = _pcm_to_wav(pcm_snapshot)
            text = await _recognize(wav_data, client_id, client_secret)

            if text is None:
                continue

            text = text.strip()
            if not text:
                continue

            if text != last_text:
                last_text = text
                try:
                    await websocket.send_json({
                        "type": "stt_result",
                        "transcript": text,
                        "is_final": False,
                    })
                except Exception:
                    break

    async def finalize():
        """Send final recognition for the complete audio buffer."""
        nonlocal audio_buffer, last_text

        async with lock:
            if len(audio_buffer) < int(MIN_AUDIO_SEC * SAMPLE_RATE * SAMPLE_WIDTH):
                return
            pcm_snapshot = bytes(audio_buffer)

        wav_data = _pcm_to_wav(pcm_snapshot)
        text = await _recognize(wav_data, client_id, client_secret)

        if text and text.strip():
            text = text.strip()
            try:
                await websocket.send_json({
                    "type": "stt_result",
                    "transcript": text,
                    "is_final": True,
                })
            except Exception:
                pass

    recognizer_task = asyncio.create_task(recognition_loop())

    try:
        while True:
            data = await websocket.receive()

            if "bytes" in data:
                async with lock:
                    audio_buffer.extend(data["bytes"])
            elif "text" in data:
                import json
                msg = json.loads(data["text"])
                if msg.get("type") == "stop":
                    break
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[CLOVA STT] WebSocket error: {e}")
    finally:
        running = False
        recognizer_task.cancel()
        try:
            await recognizer_task
        except asyncio.CancelledError:
            pass

        # Final recognition on complete buffer
        await finalize()

        # Send utterance end
        try:
            await websocket.send_json({"type": "stt_utterance_end"})
        except Exception:
            pass
