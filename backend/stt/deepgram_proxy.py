"""Deepgram STT WebSocket proxy."""

import asyncio
import json
import websockets
from fastapi import WebSocket, WebSocketDisconnect


DEEPGRAM_WS_URL = "wss://api.deepgram.com/v1/listen"


async def handle_stt_session(websocket: WebSocket, api_key: str):
    """Proxy audio between frontend WebSocket and Deepgram."""
    print(f"[STT] handle_stt_session called, api_key={'SET' if api_key else 'EMPTY'}")
    await websocket.accept()
    print(f"[STT] WebSocket accepted, connecting to Deepgram...")

    params = (
        "?language=ko"
        "&model=nova-2"
        "&encoding=linear16"
        "&sample_rate=16000"
        "&channels=1"
        "&interim_results=true"
        "&endpointing=400"
        "&utterance_end_ms=1000"
        "&punctuate=false"
        "&smart_format=false"
    )

    dg_ws = None
    try:
        dg_ws = await websockets.connect(
            DEEPGRAM_WS_URL + params,
            additional_headers={"Authorization": f"Token {api_key}"},
        )

        print(f"[STT] Deepgram connected successfully")

        async def forward_deepgram_to_client():
            try:
                async for msg in dg_ws:
                    data = json.loads(msg)
                    msg_type = data.get("type", "unknown")

                    if msg_type == "UtteranceEnd":
                        print("[STT] UtteranceEnd received")
                        await websocket.send_json({
                            "type": "stt_utterance_end",
                        })
                        continue

                    channel = data.get("channel", {})
                    alternatives = channel.get("alternatives", [])
                    if not alternatives:
                        continue

                    transcript = alternatives[0].get("transcript", "")
                    if not transcript:
                        continue

                    is_final = data.get("is_final", False)
                    speech_final = data.get("speech_final", False)
                    resolved_final = is_final or speech_final
                    print(f"[STT] transcript: '{transcript}' (is_final={is_final}, speech_final={speech_final})")
                    await websocket.send_json({
                        "type": "stt_result",
                        "transcript": transcript,
                        "is_final": resolved_final,
                    })
            except websockets.exceptions.ConnectionClosed as e:
                print(f"[STT] Deepgram connection closed: {e}")
            except Exception as e:
                print(f"[STT] Forward error: {e}")

        reader_task = asyncio.create_task(forward_deepgram_to_client())

        try:
            while True:
                audio_data = await websocket.receive_bytes()
                await dg_ws.send(audio_data)
        except WebSocketDisconnect:
            pass

        reader_task.cancel()
        try:
            await reader_task
        except asyncio.CancelledError:
            pass

    except Exception as e:
        print(f"[STT] Connection error: {e}")
        try:
            await websocket.send_json({
                "type": "stt_error",
                "message": str(e),
            })
        except Exception:
            pass
    finally:
        if dg_ws:
            try:
                await dg_ws.close()
            except Exception:
                pass
