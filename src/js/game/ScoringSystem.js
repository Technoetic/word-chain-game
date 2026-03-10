class ScoringSystem {
  static calculate(word, combo, timeLeft) {
    const baseScore = word.length * 100;
    const comboMultiplier = this.getComboMultiplier(combo);
    const speedBonus = Math.max(0, timeLeft * 10);

    return Math.floor(baseScore * comboMultiplier + speedBonus);
  }

  static getComboMultiplier(combo) {
    if (combo === 0) {
      return 1;
    } else if (combo === 1) {
      return 1.5;
    } else if (combo === 2) {
      return 2;
    } else if (combo === 3) {
      return 2.5;
    } else if (combo >= 4) {
      return 3;
    }
    return 1;
  }
}
