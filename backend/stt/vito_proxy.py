"""리턴제로 VITO STT WebSocket proxy.

Proxies audio between the frontend WebSocket and VITO streaming STT API.
Drop-in replacement for the Deepgram proxy with the same interface.
"""

import asyncio
import json
import httpx
import websockets
from fastapi import WebSocket, WebSocketDisconnect

VITO_AUTH_URL = "https://openapi.vito.ai/v1/authenticate"
VITO_WS_URL = "wss://openapi.vito.ai/v1/transcribe:streaming"


async def _get_access_token(client_id: str, client_secret: str) -> str:
    """Authenticate with VITO API and return access token."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            VITO_AUTH_URL,
            data={"client_id": client_id, "client_secret": client_secret},
        )
        resp.raise_for_status()
        return resp.json()["access_token"]


async def handle_stt_session(websocket: WebSocket, client_id: str, client_secret: str):
    """Proxy audio between frontend WebSocket and VITO streaming STT."""
    print(f"[VITO STT] session started, client_id={'SET' if client_id else 'EMPTY'}")
    await websocket.accept()

    try:
        token = await _get_access_token(client_id, client_secret)
        print("[VITO STT] authenticated successfully")
    except Exception as e:
        print(f"[VITO STT] auth error: {e}")
        await websocket.send_json({"type": "stt_error", "message": f"VITO 인증 실패: {e}"})
        return

    params = (
        "?sample_rate=16000"
        "&encoding=LINEAR16"
        "&use_itn=true"
        "&use_disfluency_filter=true"
        "&use_profanity_filter=false"
    )

    vito_ws = None
    try:
        vito_ws = await websockets.connect(
            VITO_WS_URL + params,
            additional_headers={"Authorization": f"Bearer {token}"},
        )
        print("[VITO STT] WebSocket connected")

        async def forward_vito_to_client():
            """Read VITO responses and forward to frontend."""
            try:
                async for msg in vito_ws:
                    data = json.loads(msg)

                    alternatives = data.get("alternatives", [])
                    if not alternatives:
                        continue

                    transcript = alternatives[0].get("text", "")
                    if not transcript:
                        continue

                    is_final = data.get("final", False)
                    print(f"[VITO STT] transcript: '{transcript}' (final={is_final})")

                    await websocket.send_json({
                        "type": "stt_result",
                        "transcript": transcript,
                        "is_final": is_final,
                    })

                    # VITO final == utterance boundary
                    if is_final:
                        await websocket.send_json({"type": "stt_utterance_end"})

            except websockets.exceptions.ConnectionClosed as e:
                print(f"[VITO STT] connection closed: {e}")
            except Exception as e:
                print(f"[VITO STT] forward error: {e}")

        reader_task = asyncio.create_task(forward_vito_to_client())

        try:
            while True:
                audio_data = await websocket.receive_bytes()
                try:
                    await vito_ws.send(audio_data)
                except websockets.exceptions.ConnectionClosed:
                    break
        except WebSocketDisconnect:
            pass
        finally:
            # Send EOS to VITO to signal end of stream
            try:
                await vito_ws.send("EOS")
            except Exception:
                pass

            reader_task.cancel()
            try:
                await reader_task
            except asyncio.CancelledError:
                pass

    except Exception as e:
        print(f"[VITO STT] connection error: {e}")
        try:
            await websocket.send_json({"type": "stt_error", "message": str(e)})
        except Exception:
            pass
    finally:
        if vito_ws:
            try:
                await vito_ws.close()
            except Exception:
                pass
