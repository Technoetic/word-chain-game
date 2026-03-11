from fastapi import WebSocket
from typing import Dict, Optional


class ConnectionManager:
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}
        self.game_sessions: Dict[str, object] = {}
        self.word_validator: Optional[object] = None
        self.llm_service: Optional[object] = None

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.connections[session_id] = websocket

    async def disconnect(self, session_id: str):
        if session_id in self.connections:
            del self.connections[session_id]
        if session_id in self.game_sessions:
            del self.game_sessions[session_id]

    async def send(self, session_id: str, message: dict):
        if session_id in self.connections:
            try:
                await self.connections[session_id].send_json(message)
            except Exception:
                await self.disconnect(session_id)

    def create_game(self, session_id: str, word_validator, llm_service):
        from backend.game.engine import GameEngine

        game = GameEngine(word_validator, llm_service)
        self.game_sessions[session_id] = game
        return game

    def get_game(self, session_id: str) -> Optional[object]:
        return self.game_sessions.get(session_id)
