import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.game.engine import GameEngine
from backend.game.state import GameState
from backend.game.rules import GameRules
from backend.game.scoring import ScoringSystem


@pytest.fixture
def mock_word_validator():
    """Create a mock word validator."""
    validator = AsyncMock()
    # Default valid response
    validator.validate = AsyncMock(
        return_value={"valid": True, "is_noun": True, "reason": "VALID", "message": "ok"}
    )
    return validator


@pytest.fixture
def mock_llm_service():
    """Create a mock LLM service with async generator."""
    service = MagicMock()

    async def stream_word_generator(char, used_words, difficulty):
        """Async generator that yields characters."""
        word = "테스트"
        for c in word:
            yield c

    # Set stream_word as an async generator
    service.stream_word = stream_word_generator
    return service


@pytest.fixture
def game_engine(mock_word_validator, mock_llm_service):
    """Create a GameEngine instance with mocked dependencies."""
    return GameEngine(
        word_validator=mock_word_validator,
        llm_service=mock_llm_service
    )


class TestGameEngineStartGame:
    """Tests for start_game method."""

    def test_start_game_default_difficulty(self, game_engine):
        """Test starting game with default difficulty."""
        result = game_engine.start_game()

        assert result["type"] == "game_started"
        assert result["difficulty"] == "normal"
        assert result["session_id"] is not None
        assert game_engine.state.is_active is True
        assert game_engine.state.current_turn == "user"
        assert game_engine.state.difficulty == "normal"

    def test_start_game_hard_difficulty(self, game_engine):
        """Test starting game with hard difficulty."""
        result = game_engine.start_game(difficulty="hard")

        assert result["type"] == "game_started"
        assert result["difficulty"] == "hard"
        assert game_engine.state.difficulty == "hard"

    def test_start_game_easy_difficulty(self, game_engine):
        """Test starting game with easy difficulty."""
        result = game_engine.start_game(difficulty="easy")

        assert result["type"] == "game_started"
        assert result["difficulty"] == "easy"
        assert game_engine.state.difficulty == "easy"


class TestProcessUserWord:
    """Tests for process_user_word method."""

    @pytest.mark.asyncio
    async def test_process_user_word_valid(self, game_engine, mock_word_validator):
        """Test processing a valid user word."""
        game_engine.start_game()
        mock_word_validator.validate.return_value = {
            "valid": True,
            "is_noun": True,
            "reason": "VALID",
            "message": "ok"
        }

        result = await game_engine.process_user_word("테스트")

        assert result["type"] == "word_result"
        assert result["valid"] is True
        assert result["word"] == "테스트"
        assert result["score"] > 0
        assert "테스트" in game_engine.state.used_words
        assert game_engine.state.user_score > 0
        assert game_engine.state.current_turn == "llm"

    @pytest.mark.asyncio
    async def test_process_user_word_invalid_dict_response(self, game_engine, mock_word_validator):
        """Test processing an invalid word (dict response)."""
        game_engine.start_game()
        mock_word_validator.validate.return_value = {
            "valid": False,
            "reason": "NOT_FOUND",
            "message": "word not in dictionary"
        }

        result = await game_engine.process_user_word("zzzzzzz")

        assert result["type"] == "word_result"
        assert result["valid"] is False
        assert result["word"] == "zzzzzzz"
        assert "not found in dictionary" in result["message"]

    @pytest.mark.asyncio
    async def test_process_user_word_invalid_bool_response(self, game_engine, mock_word_validator):
        """Test processing an invalid word (bool response)."""
        game_engine.start_game()
        mock_word_validator.validate.return_value = False

        result = await game_engine.process_user_word("invalid")

        assert result["type"] == "word_result"
        assert result["valid"] is False
        assert result["word"] == "invalid"

    @pytest.mark.asyncio
    async def test_process_user_word_game_not_active(self, game_engine):
        """Test processing word when game is not active."""
        game_engine.state.is_active = False

        result = await game_engine.process_user_word("테스트")

        assert result["type"] == "word_result"
        assert result["valid"] is False
        assert "not active" in result["message"]

    @pytest.mark.asyncio
    async def test_process_user_word_wrong_turn(self, game_engine):
        """Test processing word when it's not user's turn."""
        game_engine.start_game()
        game_engine.state.current_turn = "llm"

        result = await game_engine.process_user_word("테스트")

        assert result["type"] == "word_result"
        assert result["valid"] is False
        assert "Not your turn" in result["message"]

    @pytest.mark.asyncio
    async def test_process_user_word_too_short(self, game_engine):
        """Test processing word that is too short."""
        game_engine.start_game()

        result = await game_engine.process_user_word("a")

        assert result["type"] == "word_result"
        assert result["valid"] is False
        assert "at least 2 characters" in result["message"]

    @pytest.mark.asyncio
    async def test_process_user_word_already_used(self, game_engine, mock_word_validator):
        """Test processing a word that was already used."""
        game_engine.start_game()
        game_engine.state.used_words.append("테스트")

        result = await game_engine.process_user_word("테스트")

        assert result["type"] == "word_result"
        assert result["valid"] is False
        assert "already used" in result["message"]

    @pytest.mark.asyncio
    async def test_process_user_word_chain_violation(self, game_engine, mock_word_validator):
        """Test processing word that violates chain rules."""
        game_engine.start_game()
        game_engine.state.last_word = "테스트"
        mock_word_validator.validate.return_value = {
            "valid": True,
            "is_noun": True,
            "reason": "VALID",
            "message": "ok"
        }

        with patch("backend.game.engine.is_valid_chain", return_value=False):
            result = await game_engine.process_user_word("다른")

            assert result["type"] == "word_result"
            assert result["valid"] is False
            assert "follow chain rules" in result["message"]

    @pytest.mark.asyncio
    async def test_process_user_word_updates_combo(self, game_engine, mock_word_validator):
        """Test that combo increases with valid words."""
        game_engine.start_game()
        mock_word_validator.validate.return_value = {
            "valid": True,
            "is_noun": True,
            "reason": "VALID",
            "message": "ok"
        }

        assert game_engine.state.combo == 0

        # Mock is_valid_chain to always return True for testing combo
        with patch("backend.game.engine.is_valid_chain", return_value=True):
            await game_engine.process_user_word("테스트")
            assert game_engine.state.combo == 1

            game_engine.state.current_turn = "user"  # Reset for next turn
            await game_engine.process_user_word("테스트2")
            assert game_engine.state.combo == 2


class TestGenerateLLMResponse:
    """Tests for generate_llm_response method."""

    @pytest.mark.asyncio
    async def test_generate_llm_response_success(self, game_engine, mock_word_validator, mock_llm_service):
        """Test successful LLM response generation."""
        game_engine.start_game()
        mock_word_validator.validate.return_value = {
            "valid": True,
            "is_noun": True,
            "reason": "VALID",
            "message": "ok"
        }

        with patch("backend.game.engine.apply_dueum", return_value=["ㄷ"]):
            events = []
            async for event in game_engine.generate_llm_response("트"):
                events.append(event)

            # Should have typing events and completion event
            assert any(e["type"] == "llm_complete" for e in events)
            assert any(e["type"] == "llm_typing" for e in events)

    @pytest.mark.asyncio
    async def test_generate_llm_response_invalid_word(self, game_engine, mock_word_validator, mock_llm_service):
        """Test LLM response with invalid word."""
        game_engine.start_game()
        mock_word_validator.validate.return_value = {
            "valid": False,
            "reason": "NOT_FOUND",
            "message": "word not in dictionary"
        }

        with patch("backend.game.engine.apply_dueum", return_value=["ㄷ"]):
            events = []
            async for event in game_engine.generate_llm_response("트"):
                events.append(event)

            # Should have game_over event
            assert any(e["type"] == "game_over" for e in events)
            game_over = next(e for e in events if e["type"] == "game_over")
            assert "invalid word" in game_over["reason"]
            assert game_engine.state.is_active is False

    @pytest.mark.asyncio
    async def test_generate_llm_response_llm_service_error(self, game_engine, mock_llm_service):
        """Test LLM response when stream_word raises exception."""
        game_engine.start_game()

        async def stream_error(char, used_words, difficulty):
            raise Exception("LLM service error")
            # Make it a valid generator (never reached)
            yield ""

        mock_llm_service.stream_word = stream_error

        with patch("backend.game.engine.apply_dueum", return_value=["ㄷ"]):
            events = []
            async for event in game_engine.generate_llm_response("트"):
                events.append(event)

            # Should have game_over event
            assert any(e["type"] == "game_over" for e in events)
            game_over = next(e for e in events if e["type"] == "game_over")
            assert "AI error" in game_over["reason"]
            assert game_engine.state.is_active is False

    @pytest.mark.asyncio
    async def test_generate_llm_response_duplicate_word(self, game_engine, mock_llm_service):
        """Test LLM response with duplicate word."""
        game_engine.start_game()
        game_engine.state.used_words.append("테스트")

        # Mock stream_word to return a word that's already used
        async def stream_duplicate(char, used_words, difficulty):
            for c in "테스트":
                yield c

        mock_llm_service.stream_word = stream_duplicate

        with patch("backend.game.engine.apply_dueum", return_value=["ㄷ"]):
            events = []
            async for event in game_engine.generate_llm_response("트"):
                events.append(event)

            # Should have game_over event for duplicate
            assert any(e["type"] == "game_over" for e in events)
            game_over = next(e for e in events if e["type"] == "game_over")
            assert "could not find a word" in game_over["reason"]


class TestEndGame:
    """Tests for end_game method."""

    def test_end_game_user_wins(self, game_engine):
        """Test ending game with user winning."""
        game_engine.start_game()
        game_engine.state.user_score = 100
        game_engine.state.llm_score = 50

        result = game_engine.end_game("User gave up")

        assert result["type"] == "game_over"
        assert result["winner"] == "user"
        assert result["user_score"] == 100
        assert result["llm_score"] == 50
        assert result["reason"] == "User gave up"
        assert game_engine.state.is_active is False

    def test_end_game_llm_wins(self, game_engine):
        """Test ending game with LLM winning."""
        game_engine.start_game()
        game_engine.state.user_score = 30
        game_engine.state.llm_score = 80

        result = game_engine.end_game("Time's up")

        assert result["type"] == "game_over"
        assert result["winner"] == "llm"
        assert result["user_score"] == 30
        assert result["llm_score"] == 80

    def test_end_game_draw(self, game_engine):
        """Test ending game with draw."""
        game_engine.start_game()
        game_engine.state.user_score = 50
        game_engine.state.llm_score = 50

        result = game_engine.end_game("Draw")

        assert result["type"] == "game_over"
        assert result["winner"] == "draw"
        assert result["user_score"] == 50
        assert result["llm_score"] == 50


class TestGameEngineState:
    """Tests for game state management."""

    def test_engine_initializes_with_unique_sessions(self, mock_word_validator, mock_llm_service):
        """Test that each engine gets a unique session ID."""
        engine1 = GameEngine(mock_word_validator, mock_llm_service)
        engine2 = GameEngine(mock_word_validator, mock_llm_service)

        assert engine1.state.session_id != engine2.state.session_id

    def test_engine_uses_custom_rules_and_scoring(self, mock_word_validator, mock_llm_service):
        """Test that engine accepts custom rules and scoring."""
        custom_rules = GameRules()
        custom_scoring = ScoringSystem()

        engine = GameEngine(
            word_validator=mock_word_validator,
            llm_service=mock_llm_service,
            rules=custom_rules,
            scoring=custom_scoring
        )

        assert engine.rules is custom_rules
        assert engine.scoring is custom_scoring
