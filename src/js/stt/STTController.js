class STTController {
  constructor() {
    this.sttManager = new SpeechRecognitionManager('ko-KR');
    this.isEnabled = this.sttManager.isSupported;
    this.wordInput = null;
    this._onInterimCallback = null;
    this._onFinalCallback = null;
    this._onListeningChangeCallback = null;
    this._onVolumeCallback = null;
    this._lastInterim = '';
    this._interimTimer = null;

    if (this.isEnabled) {
      this.sttManager.onInterim((text) => this._onInterimResult(text));
      this.sttManager.onFinal((text) => this._onFinalResult(text));
      this.sttManager.onError((error) => this._onError(error));
      this.sttManager.onStateChange((isListening) => this._onStateChange(isListening));
      this.sttManager.onVolume((level) => this._onVolume(level));
      this.sttManager.onUtteranceEnd(() => this._submitPendingInterim());
    }
  }

  setWordInput(wordInput) {
    this.wordInput = wordInput;
  }

  async toggleListening() {
    if (!this.isEnabled) {
      return;
    }

    if (this.sttManager.isListening) {
      this._submitPendingInterim();
      this.sttManager.stop();
    } else {
      this._lastInterim = '';
      await this.sttManager.start();
    }
  }

  _submitPendingInterim() {
    if (this._interimTimer) {
      clearTimeout(this._interimTimer);
      this._interimTimer = null;
    }
    if (this._lastInterim) {
      const text = this._lastInterim;
      this._lastInterim = '';
      this._onFinalResult(text);
    }
  }

  onInterimText(callback) {
    this._onInterimCallback = callback;
  }

  onFinalText(callback) {
    this._onFinalCallback = callback;
  }

  onListeningChange(callback) {
    this._onListeningChangeCallback = callback;
  }

  onVolume(callback) {
    this._onVolumeCallback = callback;
  }

  _onVolume(level) {
    if (this._onVolumeCallback) {
      this._onVolumeCallback(level);
    }
  }

  _onInterimResult(text) {
    const changed = text !== this._lastInterim;
    this._lastInterim = text;

    if (changed && text) {
      if (this._interimTimer) {
        clearTimeout(this._interimTimer);
      }
      this._interimTimer = setTimeout(() => {
        this._submitPendingInterim();
      }, 1200);
    }

    if (this._onInterimCallback) {
      this._onInterimCallback(text);
    }
    if (this.wordInput) {
      this.wordInput.setInterimText(text);
    }
  }

  _onFinalResult(text) {
    this._lastInterim = '';
    if (this._interimTimer) {
      clearTimeout(this._interimTimer);
      this._interimTimer = null;
    }

    if (this._onFinalCallback) {
      this._onFinalCallback(text);
    }
    if (this.wordInput) {
      this.wordInput.setFinalText(text);
    }
  }

  _onError(error) {
    console.error('STT error:', error);

    if (error === 'not-allowed') {
      alert('마이크 접근 권한이 없습니다. 브라우저 설정에서 허용해주세요.');
    }
  }

  _onStateChange(isListening) {
    if (this._onListeningChangeCallback) {
      this._onListeningChangeCallback(isListening);
    }
    if (this.wordInput) {
      this.wordInput.updateMicState(isListening);
    }
  }

  isListening() {
    return this.sttManager.isListening;
  }

  isSupported() {
    return this.isEnabled;
  }
}
