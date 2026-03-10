class GameEngine {
  constructor(eventBusInstance) {
    this.state = new GameState();
    this.wsClient = null;
    this.eventBus = eventBusInstance;
    this.setupEventListeners();
  }

  setupEventListeners() {
    this.eventBus.on(CONSTANTS.MSG_TYPES.WORD_RESULT, (data) => {
      this.handleWordResult(data);
    });

    this.eventBus.on(CONSTANTS.MSG_TYPES.LLM_TYPING, (data) => {
      this.handleLLMTyping(data);
    });

    this.eventBus.on(CONSTANTS.MSG_TYPES.LLM_COMPLETE, (data) => {
      this.handleLLMComplete(data);
    });

    this.eventBus.on(CONSTANTS.MSG_TYPES.GAME_OVER, (data) => {
      this.handleGameOver(data);
    });
  }

  setWebSocketClient(wsClient) {
    this.wsClient = wsClient;
  }

  startGame(difficulty) {
    this.state.reset();
    this.state.isGameActive = true;
    this.state.isUserTurn = true;

    if (this.wsClient) {
      this.wsClient.send(CONSTANTS.MSG_TYPES.GAME_START, {
        difficulty: difficulty || 'normal'
      });
    }
  }

  submitWord(word) {
    if (!word || word.length === 0) {
      this.eventBus.emit('word:invalid', {
        message: '빈 단어입니다.'
      });
      return;
    }

    if (this.state.hasWord(word)) {
      this.eventBus.emit('word:invalid', {
        message: '이미 사용한 단어입니다.'
      });
      return;
    }

    if (this.state.lastWord) {
      if (!KoreanUtils.isValidChain(this.state.lastWord, word)) {
        this.eventBus.emit('word:invalid', {
          message: '단어 연결이 올바르지 않습니다.'
        });
        return;
      }
    }

    this.state.addWord(word, true);
    this.state.isUserTurn = false;

    if (this.wsClient) {
      this.wsClient.send(CONSTANTS.MSG_TYPES.WORD_SUBMIT, {
        word: word,
        time_left: this.state.timeLeft || CONSTANTS.TIMER_DURATION
      });
    }
  }

  handleWordResult(data) {
    if (data.isCorrect) {
      this.eventBus.emit('word:accepted', {
        word: data.word,
        isUser: true
      });
    } else {
      this.eventBus.emit('word:rejected', {
        word: data.word,
        reason: data.reason
      });
    }
  }

  handleLLMTyping(data) {
    this.eventBus.emit('llm:typing', {
      partialWord: data.partialWord
    });
  }

  handleLLMComplete(data) {
    if (data.word) {
      this.state.addWord(data.word, false);
      this.eventBus.emit('llm:wordComplete', {
        word: data.word
      });
    }

    this.state.isUserTurn = true;
    this.eventBus.emit('game:userTurnStart', {
      lastWord: this.state.lastWord,
      timeLimit: CONSTANTS.TIMER_DURATION
    });
  }

  handleGameOver(data) {
    this.state.isGameActive = false;
    this.eventBus.emit('game:over', {
      winner: data.winner,
      totalTurns: this.state.turnCount
    });
  }

  endGame() {
    this.state.isGameActive = false;
    this.eventBus.emit('game:ended', {
      reason: 'user_quit'
    });
  }
}
