/**
 * GameOverModal UI Component
 * Displays game result modal with winner info
 */
class GameOverModal {
  constructor(containerSelector = '.modal-overlay') {
    this.overlay = document.querySelector(containerSelector);
    this.modal = this.overlay ? this.overlay.querySelector('.modal') : null;
    this.titleEl = document.getElementById('modalTitle');
    this.messageEl = document.getElementById('modalMessage');
    this.playAgainBtn = document.getElementById('playAgainBtn');
    this._onPlayAgain = null;

    this._setupEventListeners();
  }

  _setupEventListeners() {
    this.playAgainBtn.addEventListener('click', () => {
      this.hide();
      if (this._onPlayAgain) {
        this._onPlayAgain();
      }
    });

    this.overlay.addEventListener('click', (e) => {
      if (e.target === this.overlay) {
        this.hide();
      }
    });
  }

  show(result) {
    const { winner } = result;

    if (winner === 'user') {
      this.titleEl.textContent = '승리!';
      this.messageEl.textContent = 'AI가 단어를 잇지 못했습니다!';
    } else {
      this.titleEl.textContent = '패배...';
      this.messageEl.textContent = '시간 초과! 단어를 잇지 못했습니다.';
    }

    this.overlay.style.display = 'flex';
  }

  hide() {
    this.overlay.style.display = 'none';
  }

  onPlayAgain(callback) {
    this._onPlayAgain = callback;
  }
}
