import pytest
from pydantic import ValidationError
from backend.game.state import GameState, WordResult


class TestGameStateDefaults:
    """Test GameState default values and initialization."""

    def test_gamestate_default_values(self):
        """Test that GameState initializes with correct default values."""
        game_state = GameState(session_id="test_session_1")

        assert game_state.session_id == "test_session_1"
        assert game_state.user_score == 0
        assert game_state.llm_score == 0
        assert game_state.combo == 0
        assert game_state.last_word == ""
        assert game_state.turn_count == 0
        assert game_state.is_active is False
        assert game_state.difficulty == "normal"
        assert game_state.current_turn == "user"

    def test_gamestate_used_words_default_factory(self):
        """Test that used_words uses default_factory=list for independence."""
        game_state = GameState(session_id="test_session_2")

        # used_words should be an empty list by default
        assert game_state.used_words == []
        assert isinstance(game_state.used_words, list)

    def test_gamestate_used_words_is_mutable_list(self):
        """Test that used_words is a mutable list that can be modified."""
        game_state = GameState(session_id="test_session_3")
        game_state.used_words.append("단어")

        assert game_state.used_words == ["단어"]
        assert len(game_state.used_words) == 1

    def test_gamestate_field_types(self):
        """Test that all GameState fields have correct types."""
        game_state = GameState(session_id="test_session_4")

        assert isinstance(game_state.session_id, str)
        assert isinstance(game_state.user_score, int)
        assert isinstance(game_state.llm_score, int)
        assert isinstance(game_state.used_words, list)
        assert isinstance(game_state.combo, int)
        assert isinstance(game_state.last_word, str)
        assert isinstance(game_state.turn_count, int)
        assert isinstance(game_state.is_active, bool)
        assert isinstance(game_state.difficulty, str)
        assert isinstance(game_state.current_turn, str)


class TestGameStateMultipleInstances:
    """Test edge case: multiple GameState instances have independent used_words."""

    def test_multiple_instances_independent_used_words(self):
        """Test that multiple GameState instances have independent used_words lists."""
        game_state_1 = GameState(session_id="session_1")
        game_state_2 = GameState(session_id="session_2")

        # Modify used_words in game_state_1
        game_state_1.used_words.append("첫번째")
        game_state_1.used_words.append("단어")

        # game_state_2 should not be affected
        assert game_state_2.used_words == []
        assert game_state_1.used_words == ["첫번째", "단어"]

    def test_multiple_instances_independent_scores(self):
        """Test that multiple GameState instances have independent score values."""
        game_state_1 = GameState(session_id="session_1")
        game_state_2 = GameState(session_id="session_2")

        # Modify scores in game_state_1
        game_state_1.user_score = 100
        game_state_1.llm_score = 50

        # game_state_2 should have default values
        assert game_state_2.user_score == 0
        assert game_state_2.llm_score == 0
        assert game_state_1.user_score == 100
        assert game_state_1.llm_score == 50

    def test_three_instances_used_words_independence(self):
        """Test independence of used_words across three GameState instances."""
        instances = [GameState(session_id=f"session_{i}") for i in range(3)]

        # Add different words to each instance
        instances[0].used_words.append("첫번째_단어")
        instances[1].used_words.extend(["두번째_단어1", "두번째_단어2"])
        instances[2].used_words.append("세번째_단어")

        # Verify independence
        assert instances[0].used_words == ["첫번째_단어"]
        assert instances[1].used_words == ["두번째_단어1", "두번째_단어2"]
        assert instances[2].used_words == ["세번째_단어"]

    def test_multiple_instances_can_be_modified_independently(self):
        """Test that modifying one instance doesn't affect others."""
        game_state_a = GameState(session_id="a")
        game_state_b = GameState(session_id="b")
        game_state_c = GameState(session_id="c")

        # Modify each instance independently
        game_state_a.combo = 5
        game_state_b.is_active = True
        game_state_c.difficulty = "hard"

        # Verify each has its own state
        assert game_state_a.combo == 5 and game_state_b.combo == 0 and game_state_c.combo == 0
        assert game_state_a.is_active is False and game_state_b.is_active is True and game_state_c.is_active is False
        assert game_state_a.difficulty == "normal" and game_state_b.difficulty == "normal" and game_state_c.difficulty == "hard"


class TestWordResultCreation:
    """Test WordResult model creation and field types."""

    def test_wordresult_creation_valid_true(self):
        """Test creating a WordResult with valid=True."""
        result = WordResult(
            valid=True,
            word="사과",
            score=10,
            reason="정상 단어",
            message="올바른 단어입니다"
        )

        assert result.valid is True
        assert result.word == "사과"
        assert result.score == 10
        assert result.reason == "정상 단어"
        assert result.message == "올바른 단어입니다"

    def test_wordresult_creation_valid_false(self):
        """Test creating a WordResult with valid=False."""
        result = WordResult(
            valid=False,
            word="xxx",
            score=0,
            reason="존재하지 않는 단어",
            message="올바르지 않은 단어입니다"
        )

        assert result.valid is False
        assert result.word == "xxx"
        assert result.score == 0
        assert result.reason == "존재하지 않는 단어"
        assert result.message == "올바르지 않은 단어입니다"

    def test_wordresult_field_types(self):
        """Test that all WordResult fields have correct types."""
        result = WordResult(
            valid=True,
            word="테스트",
            score=5,
            reason="테스트 이유",
            message="테스트 메시지"
        )

        assert isinstance(result.valid, bool)
        assert isinstance(result.word, str)
        assert isinstance(result.score, int)
        assert isinstance(result.reason, str)
        assert isinstance(result.message, str)

    def test_wordresult_with_zero_score(self):
        """Test WordResult with zero score."""
        result = WordResult(
            valid=False,
            word="invalid",
            score=0,
            reason="점수 없음",
            message="점수를 받지 못했습니다"
        )

        assert result.score == 0

    def test_wordresult_with_negative_score(self):
        """Test WordResult can have negative score."""
        result = WordResult(
            valid=False,
            word="bad_word",
            score=-5,
            reason="부정적 단어",
            message="감점되었습니다"
        )

        assert result.score == -5

    def test_wordresult_with_large_score(self):
        """Test WordResult with large score value."""
        result = WordResult(
            valid=True,
            word="사전단어",
            score=1000,
            reason="큰 점수",
            message="큰 점수를 받았습니다"
        )

        assert result.score == 1000


class TestGameStateCustomValues:
    """Test GameState with custom non-default values."""

    def test_gamestate_custom_initialization(self):
        """Test GameState initialization with custom values."""
        game_state = GameState(
            session_id="custom_session",
            user_score=50,
            llm_score=40,
            used_words=["apple", "elephant"],
            combo=3,
            last_word="turtle",
            turn_count=5,
            is_active=True,
            difficulty="hard",
            current_turn="llm"
        )

        assert game_state.session_id == "custom_session"
        assert game_state.user_score == 50
        assert game_state.llm_score == 40
        assert game_state.used_words == ["apple", "elephant"]
        assert game_state.combo == 3
        assert game_state.last_word == "turtle"
        assert game_state.turn_count == 5
        assert game_state.is_active is True
        assert game_state.difficulty == "hard"
        assert game_state.current_turn == "llm"

    def test_gamestate_partial_custom_values(self):
        """Test GameState with some custom and some default values."""
        game_state = GameState(
            session_id="partial_session",
            user_score=25,
            difficulty="easy"
        )

        assert game_state.session_id == "partial_session"
        assert game_state.user_score == 25
        assert game_state.difficulty == "easy"
        # Check defaults are still applied
        assert game_state.llm_score == 0
        assert game_state.combo == 0
        assert game_state.used_words == []
        assert game_state.is_active is False


class TestGameStateValidation:
    """Test GameState validation and type checking."""

    def test_gamestate_requires_session_id(self):
        """Test that session_id is required for GameState."""
        with pytest.raises(ValidationError):
            GameState()

    def test_gamestate_accepts_empty_used_words(self):
        """Test that GameState accepts empty used_words list."""
        game_state = GameState(session_id="test", used_words=[])
        assert game_state.used_words == []

    def test_gamestate_accepts_populated_used_words(self):
        """Test that GameState accepts pre-populated used_words."""
        words = ["word1", "word2", "word3"]
        game_state = GameState(session_id="test", used_words=words)
        assert game_state.used_words == words
        assert len(game_state.used_words) == 3


class TestGameStateDefaultFactoryBehavior:
    """Test default_factory behavior specifically for used_words."""

    def test_default_factory_creates_new_list_each_time(self):
        """Test that default_factory creates new list instances."""
        game_state_1 = GameState(session_id="s1")
        game_state_2 = GameState(session_id="s2")

        # Ensure they are different list objects
        assert game_state_1.used_words is not game_state_2.used_words

        # Modify one and ensure the other is unaffected
        game_state_1.used_words.append("word")
        assert len(game_state_2.used_words) == 0

    def test_default_factory_with_class_instantiation(self):
        """Test default_factory across multiple class instantiations."""
        instances = [GameState(session_id=f"s{i}") for i in range(5)]

        # All should have empty used_words
        for instance in instances:
            assert instance.used_words == []

        # Modify each one
        for i, instance in enumerate(instances):
            instance.used_words.append(f"word_{i}")

        # Verify all have their own words
        for i, instance in enumerate(instances):
            assert instance.used_words == [f"word_{i}"]
