/**
 * WordInput UI Component (Voice-only)
 * Handles voice input from user - no text field
 */
class WordInput {
  constructor(containerSelector = '.input-area') {
    this.container = document.querySelector(containerSelector);
    this.micBtn = this.container.querySelector('.mic-btn');
    this.transcriptEl = document.getElementById('sttTranscript');
    this.hintEl = document.getElementById('sttHint');
    this._onSubmit = null;
    this._currentWord = '';
  }

  setInterimText(text) {
    this._currentWord = text;
    this.transcriptEl.textContent = text;
    this.transcriptEl.classList.add('stt-transcript--interim');
    this.hintEl.classList.add('stt-hint--hidden');
  }

  setFinalText(text) {
    this._currentWord = text;
    this.transcriptEl.textContent = text;
    this.transcriptEl.classList.remove('stt-transcript--interim');

    if (text && this._onSubmit) {
      this._onSubmit(text.trim());
    }
  }

  onSubmit(callback) {
    this._onSubmit = callback;
  }

  setEnabled(enabled) {
    if (this.micBtn) {
      this.micBtn.disabled = !enabled;
    }
  }

  clear() {
    this._currentWord = '';
    this.transcriptEl.textContent = '';
    this.transcriptEl.classList.remove('stt-transcript--interim');
    this.hintEl.classList.remove('stt-hint--hidden');
  }

  shake() {
    this.container.classList.remove('input-area--shake');
    void this.container.offsetWidth;
    this.container.classList.add('input-area--shake');
  }

  updateMicState(isListening) {
    if (!this.micBtn) return;

    if (isListening) {
      this.micBtn.classList.add('mic-btn--active');
      this.hintEl.textContent = '듣고 있어요...';
    } else {
      this.micBtn.classList.remove('mic-btn--active');
      this.hintEl.textContent = '마이크를 눌러 말하세요';
    }
  }

  focus() {
    // no-op for voice mode
  }

  getValue() {
    return this._currentWord.trim();
  }
}
