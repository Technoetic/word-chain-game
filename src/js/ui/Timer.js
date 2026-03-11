/**
 * Timer UI Component
 * Manages countdown timer display with SVG circle progress indicator
 */
class Timer {
  constructor(elementSelector = '.timer') {
    this.element = document.querySelector(elementSelector);
    this.textEl = this.element.querySelector('.timer__text');
    this.duration = CONSTANTS.TIMER_DURATION || 15;
    this.remaining = this.duration;
    this._intervalId = null;
    this._onExpired = null;
  }

  start() {
    this.remaining = this.duration;
    this._updateDisplay();

    if (this._intervalId) {
      clearInterval(this._intervalId);
    }

    this._intervalId = setInterval(() => {
      this.remaining--;
      this._updateDisplay();

      if (this.remaining <= 0) {
        this.stop();
        if (this._onExpired) {
          this._onExpired();
        }
      }
    }, 1000);
  }

  stop() {
    if (this._intervalId) {
      clearInterval(this._intervalId);
      this._intervalId = null;
    }
  }

  reset(newDuration) {
    this.stop();
    if (newDuration !== undefined) {
      this.duration = newDuration;
    }
    this.remaining = this.duration;
    this.element.classList.remove('timer--danger', 'timer--warn');
    this._updateDisplay();
  }

  onExpired(callback) {
    this._onExpired = callback;
  }

  _updateDisplay() {
    this.textEl.textContent = this.remaining;

    // Apply color classes based on remaining time
    this.element.classList.remove('timer--danger', 'timer--warn', 'timer--safe');

    if (this.remaining < 3) {
      this.element.classList.add('timer--danger');
    } else if (this.remaining <= 5) {
      this.element.classList.add('timer--warn');
    } else {
      this.element.classList.add('timer--safe');
    }
  }
}
