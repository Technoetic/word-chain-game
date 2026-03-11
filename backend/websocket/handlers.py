import asyncio
from fastapi import WebSocket
from typing import Dict
from backend.websocket.messages import (
    ErrorMsg,
)

LLM_TIMEOUT = 30  # seconds


async def handle_message(websocket: WebSocket, data: Dict, manager, session_id: str):
    msg_type = data.get("type")

    if msg_type == "game_start":
        await handle_game_start(websocket, data, manager, session_id)
    elif msg_type == "word_submit":
        await handle_word_submit(websocket, data, manager, session_id)
    elif msg_type == "timer_expired":
        await handle_timer_expired(websocket, data, manager, session_id)
    else:
        error_msg = ErrorMsg(message=f"Unknown message type: {msg_type}")
        await manager.send(session_id, error_msg.model_dump())


async def handle_game_start(websocket: WebSocket, data: Dict, manager, session_id: str):
    try:
        difficulty = data.get("difficulty", "normal")

        game = manager.create_game(
            session_id, manager.word_validator, manager.llm_service
        )
        result = game.start_game(difficulty)

        await manager.send(session_id, result)
    except Exception as e:
        error_msg = ErrorMsg(message=f"Failed to start game: {str(e)}")
        await manager.send(session_id, error_msg.model_dump())


async def handle_word_submit(
    websocket: WebSocket, data: Dict, manager, session_id: str
):
    try:
        word = data.get("word", "").strip()
        time_left = data.get("time_left", 15)

        game = manager.get_game(session_id)
        if not game:
            error_msg = ErrorMsg(message="Game not found")
            await manager.send(session_id, error_msg.model_dump())
            return

        result = await game.process_user_word(word, time_left)
        await manager.send(session_id, result)

        if result.get("valid"):
            target_char = game.state.last_word[-1]

            if result.get("killer_word"):
                try:
                    await manager.send(session_id, {"type": "ai_reaction", "char": "START"})
                    async for chunk in manager.llm_service.stream_reaction(
                        result["word"], target_char
                    ):
                        await manager.send(session_id, {"type": "ai_reaction", "char": chunk})
                except Exception as e:
                    print(f"[Reaction] stream error: {e}")
                finally:
                    await manager.send(session_id, {"type": "ai_reaction", "char": "END"})

            try:
                async def _stream_llm():
                    async for response in game.generate_llm_response(target_char):
                        await manager.send(session_id, response)

                await asyncio.wait_for(_stream_llm(), timeout=LLM_TIMEOUT)
            except asyncio.TimeoutError:
                game.state.is_active = False
                game.state.current_turn = "llm"
                await manager.send(session_id, game.end_game("AI 시간 초과"))
    except Exception as e:
        error_msg = ErrorMsg(message=f"Error processing word: {str(e)}")
        await manager.send(session_id, error_msg.model_dump())


async def handle_timer_expired(
    websocket: WebSocket, data: Dict, manager, session_id: str
):
    try:
        game = manager.get_game(session_id)
        if not game:
            error_msg = ErrorMsg(message="Game not found")
            await manager.send(session_id, error_msg.model_dump())
            return

        result = game.end_game("Timer expired")
        await manager.send(session_id, result)
    except Exception as e:
        error_msg = ErrorMsg(message=f"Error ending game: {str(e)}")
        await manager.send(session_id, error_msg.model_dump())
