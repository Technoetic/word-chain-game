/**
 * ScoreBoard UI Component
 * Displays and animates score updates for user and LLM
 */
class ScoreBoard {
  constructor(containerSelector = '.score-board') {
    this.container = document.querySelector(containerSelector);
    this.userScoreEl = document.getElementById('userScore');
    this.llmScoreEl = document.getElementById('aiScore');
    this.userScore = 0;
    this.llmScore = 0;
  }

  update(userScore, llmScore) {
    const userDiff = userScore - this.userScore;
    const llmDiff = llmScore - this.llmScore;

    if (userDiff !== 0) {
      this._animateValue(
        this.userScoreEl,
        this.userScore,
        userScore,
        500
      );
    }

    if (llmDiff !== 0) {
      this._animateValue(
        this.llmScoreEl,
        this.llmScore,
        llmScore,
        500
      );
    }

    this.userScore = userScore;
    this.llmScore = llmScore;
  }

  _animateValue(element, start, end, duration = 500) {
    const startTime = Date.now();
    const difference = end - start;

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const current = Math.floor(start + difference * progress);

      element.textContent = current;

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    animate();
  }
}
