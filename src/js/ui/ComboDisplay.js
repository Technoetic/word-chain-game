/**
 * ComboDisplay UI Component
 * Shows combo count with flash animation
 */
class ComboDisplay {
  constructor(elementSelector = '.combo-display') {
    this.element = document.querySelector(elementSelector);
    this.textEl = this.element.querySelector('.combo-display__text');
    this.comboCount = 0;
  }

  setCombo(count) {
    this.comboCount = count;

    if (count > 0) {
      this.textEl.textContent = `COMBO x${count}!`;
      this.element.style.display = 'block';
    } else {
      this.element.style.display = 'none';
    }
  }

  animate() {
    this.element.classList.remove('combo-flash');
    // Trigger reflow to restart animation
    void this.element.offsetWidth;
    this.element.classList.add('combo-flash');
  }
}
