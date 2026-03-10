class KoreanUtils {
  static getLastChar(word) {
    if (!word || word.length === 0) {
      return '';
    }
    return word[word.length - 1];
  }

  static applyDueum(char) {
    const dueum = {
      '녀': '여', '뇨': '요', '뉴': '유', '니': '이',
      '라': '나', '래': '내', '려': '여', '례': '예',
      '료': '요', '류': '유', '리': '이', '로': '노',
      '루': '누', '르': '느'
    };

    const result = [char];
    if (dueum[char] && !result.includes(dueum[char])) {
      result.push(dueum[char]);
    }
    return result;
  }

  static isValidChain(prevWord, nextWord) {
    if (!prevWord || !nextWord) {
      return false;
    }

    const lastChar = this.getLastChar(prevWord);
    const firstChar = nextWord[0];

    // Direct match
    if (lastChar === firstChar) {
      return true;
    }

    // Dueum law match
    const validChars = this.applyDueum(lastChar);
    return validChars.includes(firstChar);
  }

  static getInitial(char) {
    if (!char || char.length === 0) {
      return '';
    }

    const code = char.charCodeAt(0);
    if (code < 0xAC00 || code > 0xD7A3) {
      return char;
    }

    const index = code - 0xAC00;
    const initial = Math.floor(index / (21 * 28));
    const initials = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'];

    return initials[initial];
  }
}
