import os
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from backend.websocket.manager import ConnectionManager
from backend.websocket.handlers import handle_message
from backend.dictionary.korean_api_client import KoreanAPIClient
from backend.dictionary.cache import WordCache
from backend.dictionary.validator import WordValidator
from backend.llm.service import LLMService
from backend.stt.deepgram_proxy import handle_stt_session as handle_deepgram_session
from backend.stt.clova_stt import handle_stt_session as handle_clova_session
from backend.stt.vito_proxy import handle_stt_session as handle_vito_session
from backend.tts.clova_tts import synthesize as clova_synthesize
from backend.utils.config import Settings

app = FastAPI(title="Korean Word Chain Game API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = ConnectionManager()

settings = Settings()

word_cache = WordCache()
korean_api_client = KoreanAPIClient(settings.korean_dict_api_key)
word_validator = WordValidator(korean_api_client, word_cache)

llm_service = LLMService(settings.anthropic_api_key, base_url=settings.anthropic_base_url)

manager.word_validator = word_validator
manager.llm_service = llm_service


@app.websocket("/ws/stt")
async def stt_endpoint(websocket: WebSocket):
    if settings.vito_client_id and settings.vito_client_secret:
        await handle_vito_session(websocket, settings.vito_client_id, settings.vito_client_secret)
    elif settings.ncp_client_id and settings.ncp_client_secret:
        await handle_clova_session(websocket, settings.ncp_client_id, settings.ncp_client_secret)
    else:
        await handle_deepgram_session(websocket, settings.deepgram_api_key)


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_json()
            await handle_message(websocket, data, manager, session_id)
    except WebSocketDisconnect:
        await manager.disconnect(session_id)
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        await manager.disconnect(session_id)


@app.get("/api/tts")
async def tts_endpoint(text: str = Query(..., max_length=200)):
    if not settings.ncp_client_id or not settings.ncp_client_secret:
        return Response(status_code=503, content="TTS not configured")
    try:
        audio = await clova_synthesize(
            text, settings.ncp_client_id, settings.ncp_client_secret
        )
        return Response(content=audio, media_type="audio/mpeg")
    except Exception as e:
        print(f"[TTS] error: {e}")
        return Response(status_code=500, content=str(e))


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


DIST_DIR = Path(__file__).parent.parent / "dist"


@app.get("/")
async def serve_index():
    return FileResponse(DIST_DIR / "index.html")


@app.on_event("shutdown")
async def shutdown_event():
    for session_id in list(manager.connections.keys()):
        await manager.disconnect(session_id)
