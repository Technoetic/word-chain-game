/**
 * ParticleEffect UI Component
 * Creates various particle and visual effects
 */
class ParticleEffect {
  static burst(x, y, color = '#66bb6a', count = 15) {
    const container = document.body;

    for (let i = 0; i < count; i++) {
      const particle = document.createElement('div');
      particle.className = 'particle';
      particle.style.left = x + 'px';
      particle.style.top = y + 'px';
      particle.style.backgroundColor = color;

      // Random velocity and direction
      const angle = (Math.PI * 2 * i) / count;
      const velocity = 5 + Math.random() * 5;
      const vx = Math.cos(angle) * velocity;
      const vy = Math.sin(angle) * velocity;

      container.appendChild(particle);

      // Animate particle
      let posX = x;
      let posY = y;
      const startTime = Date.now();
      const duration = 600;

      const animate = () => {
        const elapsed = Date.now() - startTime;
        const progress = elapsed / duration;

        if (progress >= 1) {
          particle.remove();
          return;
        }

        posX += vx;
        posY += vy;

        particle.style.left = posX + 'px';
        particle.style.top = posY + 'px';
        particle.style.opacity = 1 - progress;

        requestAnimationFrame(animate);
      };

      animate();
    }
  }

  static success() {
    const centerX = window.innerWidth / 2;
    const centerY = window.innerHeight / 2;
    this.burst(centerX, centerY, '#66bb6a', 20);
  }

  static fail() {
    const overlay = document.createElement('div');
    overlay.className = 'flash-overlay flash-overlay--fail';
    document.body.appendChild(overlay);

    setTimeout(() => {
      overlay.remove();
    }, 300);
  }

  static combo() {
    const comboEl = document.querySelector('.combo-display');
    if (comboEl) {
      const rect = comboEl.getBoundingClientRect();
      const x = rect.left + rect.width / 2;
      const y = rect.top + rect.height / 2;
      this.burst(x, y, '#ffd700', 15);
    }
  }

  static screenShake(duration = 300) {
    const gameBoard = document.querySelector('.game-board');
    if (!gameBoard) return;

    const startTime = Date.now();
    const shake = () => {
      const elapsed = Date.now() - startTime;

      if (elapsed >= duration) {
        gameBoard.style.transform = 'translate(0, 0)';
        return;
      }

      const intensity = (1 - elapsed / duration) * 5;
      const x = (Math.random() - 0.5) * intensity;
      const y = (Math.random() - 0.5) * intensity;

      gameBoard.style.transform = `translate(${x}px, ${y}px)`;
      requestAnimationFrame(shake);
    };

    shake();
  }
}
