class GameState {
  constructor() {
    this.usedWords = new Set();
    this.lastWord = '';
    this.turnCount = 0;
    this.isGameActive = false;
    this.isUserTurn = true;
  }

  reset() {
    this.usedWords.clear();
    this.lastWord = '';
    this.turnCount = 0;
    this.isGameActive = false;
    this.isUserTurn = true;
  }

  addWord(word, isUser) {
    const lowerWord = word.toLowerCase();
    this.usedWords.add(lowerWord);
    this.lastWord = lowerWord;
    this.turnCount += 1;
  }

  removeWord(word) {
    this.usedWords.delete(word.toLowerCase());
    this.turnCount = Math.max(0, this.turnCount - 1);
  }

  hasWord(word) {
    return this.usedWords.has(word.toLowerCase());
  }
}
