/**
 * Main Entry Point
 * Initializes the Korean word chain game application
 */

document.addEventListener('DOMContentLoaded', () => {
  const eventBus = new EventBus();
  const gameEngine = new GameEngine(eventBus);
  const wsClient = new WebSocketClient(CONFIG.WS_URL);
  const messageHandler = new MessageHandler(gameEngine, eventBus);
  const gameBoard = new GameBoard(eventBus);


  gameEngine.setWebSocketClient(wsClient);
  messageHandler.setupHandlers(wsClient);

  const startScreen = document.getElementById('startScreen');
  const gameScreen = document.getElementById('gameScreen');
  const startBtn = document.getElementById('startBtn');

  // Word submission from GameBoard
  eventBus.on('word_submitted', (data) => {
    gameEngine.submitWord(data.word);
  });

  // Timer expired → tell server
  eventBus.on('timer_expired', () => {
    wsClient.send('timer_expired', {});
  });

  // Start game button
  if (startBtn) {
    startBtn.addEventListener('click', () => {
      if (startScreen) startScreen.style.display = 'none';
      if (gameScreen) gameScreen.style.display = 'flex';
      gameEngine.startGame();
      // Emit game_started locally to activate UI immediately
      eventBus.emit('game_started', { difficulty: 'normal' });
    });
  }

  // Play again from modal
  gameBoard.gameOverModal.onPlayAgain(() => {
    gameEngine.startGame();
  });

  // Handle connection errors
  wsClient.onError((error) => {
    eventBus.emit('error', {
      message: '연결 오류가 발생했습니다.'
    });
  });

  wsClient.onClose(() => {
    eventBus.emit('error', {
      message: '서버와의 연결이 끊어졌습니다.'
    });
  });

  // Connect WebSocket
  wsClient.connect()
    .catch((err) => {
      console.error('WebSocket 연결 실패:', err);
    });
});
