"""Comprehensive tests for WordValidator class."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.dictionary.validator import WordValidator, ValidationReason
from backend.dictionary.cache import WordCache


class TestWordValidatorWithCache:
    """Tests for validate() with cached results."""

    @pytest.mark.asyncio
    async def test_validate_returns_cached_result(self):
        """Test that validate() returns cached result without API call."""
        # Setup
        api_client = AsyncMock()
        cache = WordCache()
        validator = WordValidator(api_client, cache)

        # Pre-populate cache
        cached_result = {
            "valid": True,
            "is_noun": True,
            "reason": ValidationReason.VALID.value,
            "message": "'책'은(는) 유효한 명사입니다.",
        }
        cache.set("책", cached_result)

        # Execute
        result = await validator.validate("책")

        # Assert
        assert result == cached_result
        api_client.search.assert_not_called()  # API should NOT be called

    @pytest.mark.asyncio
    async def test_validate_uses_cache_for_multiple_calls(self):
        """Test that cache is used for repeated validations."""
        # Setup
        api_client = AsyncMock()
        cache = WordCache()
        validator = WordValidator(api_client, cache)

        api_response = {
            "result": {
                "word": [{"pos": "명사", "definition": "paper made from pulped wood"}]
            }
        }
        api_client.search.return_value = api_response

        # Execute - first call
        result1 = await validator.validate("종이")

        # Execute - second call (should use cache)
        result2 = await validator.validate("종이")

        # Assert
        assert result1 == result2
        assert result1["valid"] is True
        assert result1["is_noun"] is True
        api_client.search.assert_called_once()  # API called only once

    @pytest.mark.asyncio
    async def test_validate_cache_stores_result(self):
        """Test that validate() stores result in cache."""
        # Setup
        api_client = AsyncMock()
        cache = WordCache()
        validator = WordValidator(api_client, cache)

        api_response = {
            "result": {
                "word": [{"pos": "명사"}]
            }
        }
        api_client.search.return_value = api_response

        # Execute
        result = await validator.validate("나무")

        # Assert
        cached = cache.get("나무")
        assert cached is not None
        assert cached == result

    @pytest.mark.asyncio
    async def test_validate_distinguishes_cached_valid_from_invalid(self):
        """Test that cache correctly stores both valid and invalid results."""
        # Setup
        api_client = AsyncMock()
        cache = WordCache()
        validator = WordValidator(api_client, cache)

        # Pre-populate cache with invalid result
        invalid_result = {
            "valid": False,
            "is_noun": False,
            "reason": ValidationReason.NOT_IN_DICT.value,
            "message": "'xyzabc'은(는) 사전에 없는 단어입니다.",
        }
        cache.set("xyzabc", invalid_result)

        # Execute
        result = await validator.validate("xyzabc")

        # Assert
        assert result["valid"] is False
        api_client.search.assert_not_called()


class TestWordValidatorAPICall:
    """Tests for validate() calling API when cache miss."""

    @pytest.mark.asyncio
    async def test_validate_calls_api_on_cache_miss(self):
        """Test that validate() calls API when cache is empty."""
        # Setup
        api_client = AsyncMock()
        cache = WordCache()
        validator = WordValidator(api_client, cache)

        api_response = {
            "result": {
                "word": [{"pos": "명사"}]
            }
        }
        api_client.search.return_value = api_response

        # Execute
        await validator.validate("flower")

        # Assert
        api_client.search.assert_called_once_with("flower")

    @pytest.mark.asyncio
    async def test_validate_passes_word_to_api(self):
        """Test that validate() passes the correct word to API."""
        # Setup
        api_client = AsyncMock()
        cache = WordCache()
        validator = WordValidator(api_client, cache)

        api_client.search.return_value = {"result": {"word": []}}

        # Execute
        await validator.validate("테스트단어")

        # Assert
        api_client.search.assert_called_once_with("테스트단어")

    @pytest.mark.asyncio
    async def test_validate_handles_empty_api_response(self):
        """Test validate() with API returning empty result."""
        # Setup
        api_client = AsyncMock()
        cache = WordCache()
        validator = WordValidator(api_client, cache)

        api_client.search.return_value = {"result": {}}

        # Execute
        result = await validator.validate("notaword")

        # Assert
        assert result["valid"] is False
        assert result["reason"] == ValidationReason.NOT_IN_DICT.value


class TestParsingValidNounResponse:
    """Tests for parsing valid noun responses from API."""

    @pytest.mark.asyncio
    async def test_parse_response_valid_noun(self):
        """Test parsing response with valid noun."""
        # Setup
        api_client = AsyncMock()
        cache = WordCache()
        validator = WordValidator(api_client, cache)

        api_response = {
            "result": {
                "word": [
                    {"pos": "명사", "definition": "tree"}
                ]
            }
        }
        api_client.search.return_value = api_response

        # Execute
        result = await validator.validate("나무")

        # Assert
        assert result["valid"] is True
        assert result["is_noun"] is True
        assert result["reason"] == ValidationReason.VALID.value
        assert "유효한 명사" in result["message"]

    @pytest.mark.asyncio
    async def test_parse_response_noun_in_multiple_entries(self):
        """Test parsing when noun appears in list with other parts of speech."""
        # Setup
        api_client = AsyncMock()
        cache = WordCache()
        validator = WordValidator(api_client, cache)

        api_response = {
            "result": {
                "word": [
                    {"pos": "동사", "definition": "to run"},
                    {"pos": "명사", "definition": "run as a noun"},
                    {"pos": "형용사", "definition": "running as adjective"}
                ]
            }
        }
        api_client.search.return_value = api_response

        # Execute
        result = await validator.validate("달리다")

        # Assert
        assert result["valid"] is True
        assert result["is_noun"] is True
        assert result["reason"] == ValidationReason.VALID.value

    @pytest.mark.asyncio
    async def test_parse_response_noun_with_embedded_text(self):
        """Test parsing when 명사 is embedded in pos field."""
        # Setup
        api_client = AsyncMock()
        cache = WordCache()
        validator = WordValidator(api_client, cache)

        api_response = {
            "result": {
                "word": [
                    {"pos": "명사 (n)"}
                ]
            }
        }
        api_client.search.return_value = api_response

        # Execute
        result = await validator.validate("단어")

        # Assert
        assert result["valid"] is True
        assert result["is_noun"] is True

    @pytest.mark.asyncio
    async def test_parse_response_word_as_single_item(self):
        """Test parsing when word field is single dict not list."""
        # Setup
        api_client = AsyncMock()
        cache = WordCache()
        validator = WordValidator(api_client, cache)

        api_response = {
            "result": {
                "word": {"pos": "명사", "definition": "book"}
            }
        }
        api_client.search.return_value = api_response

        # Execute
        result = await validator.validate("책")

        # Assert
        assert result["valid"] is True
        assert result["is_noun"] is True

    @pytest.mark.asyncio
    async def test_parse_response_multiple_valid_nouns(self):
        """Test parsing with multiple valid noun entries."""
        # Setup
        api_client = AsyncMock()
        cache = WordCache()
        validator = WordValidator(api_client, cache)

        api_response = {
            "result": {
                "word": [
                    {"pos": "명사", "definition": "definition 1"},
                    {"pos": "명사", "definition": "definition 2"},
                    {"pos": "명사", "definition": "definition 3"}
                ]
            }
        }
        api_client.search.return_value = api_response

        # Execute
        result = await validator.validate("다의어")

        # Assert
        assert result["valid"] is True
        assert result["is_noun"] is True


class TestParsingNonNounResponse:
    """Tests for parsing non-noun responses from API."""

    @pytest.mark.asyncio
    async def test_parse_response_non_noun_verb(self):
        """Test parsing response with verb (not noun)."""
        # Setup
        api_client = AsyncMock()
        cache = WordCache()
        validator = WordValidator(api_client, cache)

        api_response = {
            "result": {
                "word": [
                    {"pos": "동사", "definition": "to walk"}
                ]
            }
        }
        api_client.search.return_value = api_response

        # Execute
        result = await validator.validate("걷다")

        # Assert
        assert result["valid"] is False
        assert result["is_noun"] is False
        assert result["reason"] == ValidationReason.NOT_A_NOUN.value
        assert "명사가 아닙니다" in result["message"]

    @pytest.mark.asyncio
    async def test_parse_response_non_noun_adjective(self):
        """Test parsing response with adjective."""
        # Setup
        api_client = AsyncMock()
        cache = WordCache()
        validator = WordValidator(api_client, cache)

        api_response = {
            "result": {
                "word": [
                    {"pos": "형용사", "definition": "big"}
                ]
            }
        }
        api_client.search.return_value = api_response

        # Execute
        result = await validator.validate("크다")

        # Assert
        assert result["valid"] is False
        assert result["is_noun"] is False

    @pytest.mark.asyncio
    async def test_parse_response_mixed_pos_no_noun(self):
        """Test parsing with multiple POS but no noun."""
        # Setup
        api_client = AsyncMock()
        cache = WordCache()
        validator = WordValidator(api_client, cache)

        api_response = {
            "result": {
                "word": [
                    {"pos": "동사"},
                    {"pos": "형용사"},
                    {"pos": "부사"}
                ]
            }
        }
        api_client.search.return_value = api_response

        # Execute
        result = await validator.validate("빨리")

        # Assert
        assert result["valid"] is False
        assert result["is_noun"] is False
        assert result["reason"] == ValidationReason.NOT_A_NOUN.value

    @pytest.mark.asyncio
    async def test_parse_response_empty_word_list(self):
        """Test parsing when word list is empty."""
        # Setup
        api_client = AsyncMock()
        cache = WordCache()
        validator = WordValidator(api_client, cache)

        api_response = {
            "result": {
                "word": []
            }
        }
        api_client.search.return_value = api_response

        # Execute
        result = await validator.validate("fakword")

        # Assert
        assert result["valid"] is False
        assert result["reason"] == ValidationReason.NOT_IN_DICT.value

    @pytest.mark.asyncio
    async def test_parse_response_missing_pos_field(self):
        """Test parsing when word entry lacks pos field."""
        # Setup
        api_client = AsyncMock()
        cache = WordCache()
        validator = WordValidator(api_client, cache)

        api_response = {
            "result": {
                "word": [
                    {"definition": "some definition"}
                ]
            }
        }
        api_client.search.return_value = api_response

        # Execute
        result = await validator.validate("incomplete")

        # Assert
        assert result["valid"] is False
        assert result["reason"] == ValidationReason.NOT_A_NOUN.value


class TestAPIErrorHandling:
    """Tests for API error handling."""

    @pytest.mark.asyncio
    async def test_handle_api_error_in_response(self):
        """Test handling API error field in response."""
        # Setup
        api_client = AsyncMock()
        cache = WordCache()
        validator = WordValidator(api_client, cache)

        api_response = {
            "error": "API request limit exceeded"
        }
        api_client.search.return_value = api_response

        # Execute
        result = await validator.validate("someword")

        # Assert
        assert result["valid"] is False
        assert result["is_noun"] is False
        assert result["reason"] == ValidationReason.API_ERROR.value
        assert "API 오류" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_malformed_response_missing_result(self):
        """Test handling response missing 'result' key."""
        # Setup
        api_client = AsyncMock()
        cache = WordCache()
        validator = WordValidator(api_client, cache)

        api_response = {"data": {}}
        api_client.search.return_value = api_response

        # Execute
        result = await validator.validate("word")

        # Assert
        assert result["valid"] is False
        assert result["reason"] == ValidationReason.NOT_IN_DICT.value

    @pytest.mark.asyncio
    async def test_handle_null_result(self):
        """Test handling when result is None."""
        # Setup
        api_client = AsyncMock()
        cache = WordCache()
        validator = WordValidator(api_client, cache)

        api_response = {"result": None}
        api_client.search.return_value = api_response

        # Execute
        result = await validator.validate("word")

        # Assert
        assert result["valid"] is False
        assert result["reason"] == ValidationReason.NOT_IN_DICT.value

    @pytest.mark.asyncio
    async def test_handle_missing_word_field(self):
        """Test handling when result lacks 'word' field."""
        # Setup
        api_client = AsyncMock()
        cache = WordCache()
        validator = WordValidator(api_client, cache)

        api_response = {"result": {"definition": "some data"}}
        api_client.search.return_value = api_response

        # Execute
        result = await validator.validate("word")

        # Assert
        assert result["valid"] is False
        assert result["reason"] == ValidationReason.NOT_IN_DICT.value

    @pytest.mark.asyncio
    async def test_handle_invalid_word_type(self):
        """Test handling when word field is not list or dict."""
        # Setup
        api_client = AsyncMock()
        cache = WordCache()
        validator = WordValidator(api_client, cache)

        api_response = {"result": {"word": "string_not_list"}}
        api_client.search.return_value = api_response

        # Execute
        result = await validator.validate("word")

        # Assert
        assert result["valid"] is False

    @pytest.mark.asyncio
    async def test_handle_non_dict_word_entry(self):
        """Test handling when word list contains non-dict entries."""
        # Setup
        api_client = AsyncMock()
        cache = WordCache()
        validator = WordValidator(api_client, cache)

        api_response = {
            "result": {
                "word": ["string_entry", 123, None]
            }
        }
        api_client.search.return_value = api_response

        # Execute
        result = await validator.validate("word")

        # Assert
        assert result["valid"] is False
        assert result["reason"] == ValidationReason.NOT_A_NOUN.value

    @pytest.mark.asyncio
    async def test_handle_parsing_exception(self):
        """Test that parsing exceptions are caught and handled."""
        # Setup
        api_client = AsyncMock()
        cache = WordCache()
        validator = WordValidator(api_client, cache)

        # Return response that will cause exception in parsing
        api_response = {"result": {"word": [{"pos": None}]}}
        api_client.search.return_value = api_response

        # Execute (should not raise exception)
        result = await validator.validate("word")

        # Assert
        assert result["valid"] is False
        assert result["reason"] == ValidationReason.NOT_A_NOUN.value

    @pytest.mark.asyncio
    async def test_api_error_is_not_cached(self):
        """Test that API error results can be cached but not retried."""
        # Setup
        api_client = AsyncMock()
        cache = WordCache()
        validator = WordValidator(api_client, cache)

        api_response = {"error": "Service unavailable"}
        api_client.search.return_value = api_response

        # Execute - first call
        result1 = await validator.validate("word")

        # Execute - second call (should use cache)
        result2 = await validator.validate("word")

        # Assert
        assert result1 == result2
        assert result1["reason"] == ValidationReason.API_ERROR.value
        api_client.search.assert_called_once()  # API called only once


class TestValidatorIntegration:
    """Integration tests for complete validation flow."""

    @pytest.mark.asyncio
    async def test_full_validation_flow_valid_noun(self):
        """Test complete flow for valid noun."""
        # Setup
        api_client = AsyncMock()
        cache = WordCache()
        validator = WordValidator(api_client, cache)

        api_response = {
            "result": {
                "word": [{"pos": "명사", "definition": "mountain"}]
            }
        }
        api_client.search.return_value = api_response

        # Execute
        result = await validator.validate("산")

        # Assert - complete result
        assert result["valid"] is True
        assert result["is_noun"] is True
        assert result["reason"] == ValidationReason.VALID.value
        assert "유효한 명사" in result["message"]
        assert "산" in result["message"]

    @pytest.mark.asyncio
    async def test_full_validation_flow_invalid_word(self):
        """Test complete flow for word not in dictionary."""
        # Setup
        api_client = AsyncMock()
        cache = WordCache()
        validator = WordValidator(api_client, cache)

        api_response = {"result": {"word": []}}
        api_client.search.return_value = api_response

        # Execute
        result = await validator.validate("xyz123")

        # Assert - complete result
        assert result["valid"] is False
        assert result["is_noun"] is False
        assert result["reason"] == ValidationReason.NOT_IN_DICT.value

    @pytest.mark.asyncio
    async def test_sequential_validations_mixed(self):
        """Test sequential validations with both cache hits and misses."""
        # Setup
        api_client = AsyncMock()
        cache = WordCache()
        validator = WordValidator(api_client, cache)

        api_responses = {
            "책": {"result": {"word": [{"pos": "명사"}]}},
            "책을": {"result": {"word": []}},
        }
        api_client.search.side_effect = lambda word: api_responses.get(word, {})

        # Execute
        result1 = await validator.validate("책")  # API call
        result2 = await validator.validate("책")  # Cache hit
        result3 = await validator.validate("책을")  # API call

        # Assert
        assert result1["valid"] is True
        assert result1 == result2
        assert result3["valid"] is False
        assert api_client.search.call_count == 2  # Only called for unique words
