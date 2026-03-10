class MessageHandler {
  constructor(gameEngine, eventBus) {
    this.gameEngine = gameEngine;
    this.eventBus = eventBus;
    this.handlers = {
      game_started: (data) => this._handleGameStarted(data),
      word_result: (data) => this._handleWordResult(data),
      ai_reaction: (data) => this._handleAIReaction(data),
      llm_typing: (data) => this._handleLLMTyping(data),
      llm_complete: (data) => this._handleLLMComplete(data),
      game_over: (data) => this._handleGameOver(data),
      error: (data) => this._handleError(data)
    };
  }

  setupHandlers(wsClient) {
    Object.keys(this.handlers).forEach((type) => {
      wsClient.on(type, this.handlers[type]);
    });
  }

  _handleGameStarted(data) {
    this.eventBus.emit('game_started', data);
  }

  _handleWordResult(data) {
    this.eventBus.emit('word_result', {
      word: data.word,
      isCorrect: data.valid,
      message: data.message,
      killerWord: data.killer_word || false
    });
  }

  _handleAIReaction(data) {
    this.eventBus.emit('ai_reaction', data);
  }

  _handleLLMTyping(data) {
    this.eventBus.emit('llm_typing', data);
  }

  _handleLLMComplete(data) {
    this.eventBus.emit('llm_complete', data);
  }

  _handleGameOver(data) {
    this.eventBus.emit('game_over', data);
  }

  _handleError(data) {
    this.eventBus.emit('error', data);
  }
}
