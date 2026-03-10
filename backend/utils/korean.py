import unicodedata
from typing import List

DUEUM_MAP = {
    "ㄴ": ["ㄴ", "ㅇ"],  # ㄴ → ㅇ conversion
    "ㄹ": ["ㄹ", "ㅇ", "ㄴ"],  # ㄹ → ㅇ/ㄴ conversion
}

# Mapping for specific characters under dueum rules
DUEUM_CHARS = {
    "녀": "여",
    "뇨": "요",
    "뉴": "유",
    "니": "이",
    "라": "나",
    "래": "내",
    "려": "여",
    "례": "예",
    "료": "요",
    "류": "유",
    "리": "이",
    "로": "노",
    "루": "누",
    "르": "느",
}


# 한방 글자: 이 글자로 시작하는 단어가 거의 없어서 이으기 매우 어려운 글자들
KILLER_ENDINGS = set("럽릎듐륨늄늅뀨쀼튐")


def is_killer_char(char: str) -> bool:
    """Check if a character is a 'killer' character (very hard to chain from)."""
    return char in KILLER_ENDINGS


def get_last_char(word: str) -> str:
    """Return the last character of the word."""
    if not word:
        return ""
    return word[-1]


def get_initial_jamo(char: str) -> str:
    """Extract initial consonant (초성) from a Korean character using Unicode decomposition."""
    if not char:
        return ""

    # Decompose the character into its jamo components
    decomposed = unicodedata.normalize("NFD", char)

    # The first character in NFD form is the initial consonant (초성)
    if decomposed:
        return decomposed[0]

    return ""


def apply_dueum(char: str) -> List[str]:
    """Apply dueum rules to a character and return list of possible characters."""
    if not char:
        return []

    result = [char]

    # Check if character has dueum rule mapping
    if char in DUEUM_CHARS:
        dueum_char = DUEUM_CHARS[char]
        if dueum_char not in result:
            result.append(dueum_char)

    return result


def is_valid_chain(prev_word: str, next_word: str) -> bool:
    """Validate word chain considering dueum rules.

    In Korean word chain, the last syllable of prev_word must match
    the first syllable of next_word (with dueum law variations).
    """
    if not prev_word or not next_word:
        return False

    last_char = get_last_char(prev_word)
    first_char = next_word[0]

    # Direct match: last char == first char
    if last_char == first_char:
        return True

    # Apply dueum rules: check if first_char matches any dueum variation
    dueum_variations = apply_dueum(last_char)
    if first_char in dueum_variations:
        return True

    return False
