/**
 * GameBoard UI Component
 * Main container that orchestrates all UI sub-components
 */
class GameBoard {
  constructor(eventBus) {
    this.eventBus = eventBus;

    // Initialize sub-components
    this.timer = new Timer('.timer');
    this.wordHistory = new WordHistory('.word-history');
    this.wordInput = new WordInput('.input-area');
    this.gameOverModal = new GameOverModal('.modal-overlay');

    // Initialize STT controller
    this.sttController = new STTController();

    // Connect STT to WordInput
    this.sttController.onInterimText((text) => {
      this.wordInput.setInterimText(text);
    });

    this.sttController.onFinalText((text) => {
      this.wordInput.setFinalText(text);
    });

    this.sttController.onListeningChange((isListening) => {
      this.wordInput.updateMicState(isListening);
    });

    // Volume gauge
    this._micRing = document.getElementById('micRing');
    this.sttController.onVolume((level) => {
      if (this._micRing) {
        if (level > 0.01) {
          const size = 72 + level * 28;
          this._micRing.style.width = size + 'px';
          this._micRing.style.height = size + 'px';
          this._micRing.classList.add('mic-ring--active');
        } else {
          this._micRing.classList.remove('mic-ring--active');
          this._micRing.style.width = '72px';
          this._micRing.style.height = '72px';
        }
      }
    });

    this._setupEventListeners();
  }

  _setupEventListeners() {
    // Mic button click → toggle STT
    const micBtn = document.getElementById('micBtn');
    if (micBtn) {
      micBtn.addEventListener('click', () => {
        this.sttController.toggleListening();
      });
    }

    // Voice result auto-submit
    this.wordInput.onSubmit((word) => {
      if (word) {
        this.eventBus.emit('word_submitted', { word });
        this.wordInput.clear();
      }
    });

    // Game events from event bus
    this.eventBus.on('game_started', (data) => {
      this.resetUI();
      this.timer.start();
    });

    // Timer expired — send regardless of whose turn
    this.timer.onExpired(() => {
      this.eventBus.emit('timer_expired', {});
    });

    this.eventBus.on('word_result', (data) => {
      const { word, isCorrect, killerWord } = data;

      if (isCorrect) {
        this.timer.stop();
        this.wordHistory.addUserWord(word);
        ParticleEffect.success();

        // killer_word reaction is now streamed via ai_reaction events
      } else {
        this.wordInput.shake();
        ParticleEffect.fail();
        this.wordHistory.addRejectedWord(word, data.message);
      }
    });

    this.eventBus.on('ai_reaction', (data) => {
      const { char } = data;
      if (char === 'START') {
        this.wordHistory.startAIReaction();
      } else if (char === 'END') {
        this.wordHistory.finalizeAIReaction();
      } else {
        this.wordHistory.addAIReactionChar(char);
      }
    });

    this._llmTyping = false;
    this.eventBus.on('llm_typing', (data) => {
      const { char } = data;
      if (char === 'START') {
        if (this._llmTyping) {
          // Retry: remove previous failed typing item
          this.wordHistory.removeLastTyping();
        } else {
          // First attempt: start timer
          this.timer.reset();
          this.timer.start();
        }
        this._llmTyping = true;
        this.wordHistory.startLLMTyping();
      } else {
        this.wordHistory.addLLMTypingChar(char);
      }
    });

    this.eventBus.on('llm_complete', (data) => {
      const { word } = data;
      this._llmTyping = false;
      this.wordHistory.finalizeLLMWord(word);
      this._speakWord(word);
      this.timer.reset();
      this.timer.start();
    });

    this.eventBus.on('game_over', (data) => {
      this._llmTyping = false;
      this.timer.stop();
      this.gameOverModal.show(data);
    });

    this.eventBus.on('error', (data) => {
      const { message } = data;
      this.showError(message);
    });
  }

  _speakWord(word) {
    fetch(`/api/tts?text=${encodeURIComponent(word)}`)
      .then(res => {
        if (!res.ok) throw new Error('TTS failed');
        return res.blob();
      })
      .then(blob => {
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        audio.onended = () => URL.revokeObjectURL(url);
        audio.play().catch(() => {});
      })
      .catch(() => {});
  }

  resetUI() {
    this.wordHistory.clear();
    this.wordInput.clear();
    this.wordInput.setEnabled(true);
    this.wordInput.focus();
    this.gameOverModal.hide();
    this.timer.reset();
  }

  showError(message) {
    const notification = document.createElement('div');
    notification.className = 'error-notification';
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
      notification.remove();
    }, 3000);
  }
}
