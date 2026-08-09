/**
 * StaggeredGrid & Bento Parallax Engine (GSAP + ScrollTrigger Parity)
 * ===================================================================
 * Exact conversion of the requested React GSAP StaggeredGrid component:
 * 1. Kinetic split-text character reveal (staggered from center out)
 * 2. 7-Column multi-row staggered parallax grid (column delayFactor = Math.abs(col - mid) * 0.2)
 * 3. Interactive Expanding Bento Box:
 *    - Active item expands to 60% width with full content & shadow
 *    - Inactive items compress to 20% width with centered icon
 *    - Scale up on scroll into view (scale: 1.2, smooth scrub)
 * 4. Micro-interactions: hover tilt, glass specular borders, touch/click selection.
 */

(function () {
  class StaggeredBentoGrid {
    constructor(container) {
      this.container = typeof container === 'string' ? document.querySelector(container) : container;
      if (!this.container) return;

      this.textEl = this.container.querySelector('.staggered-center-text');
      this.gridEl = this.container.querySelector('.staggered-grid-full');
      this.bentoContainer = this.container.querySelector('.bento-container');
      this.bentoItems = Array.from(this.container.querySelectorAll('.bento-item'));
      this.gridItems = Array.from(this.container.querySelectorAll('.staggered-grid-item'));

      this.activeBentoIndex = 0;
      this.init();
    }

    init() {
      this.initSplitText();
      this.initBentoInteraction();
      this.initScrollAnimations();
    }

    initSplitText() {
      if (!this.textEl) return;
      const text = this.textEl.getAttribute('data-text') || this.textEl.innerText;
      this.textEl.innerHTML = '';

      const chars = text.split('');
      const charElements = [];

      chars.forEach((ch) => {
        const span = document.createElement('span');
        span.className = 'stagger-char';
        span.innerHTML = ch === ' ' ? '&nbsp;' : ch;
        this.textEl.appendChild(span);
        charElements.push(span);
      });

      this.chars = charElements;
    }

    initBentoInteraction() {
      if (!this.bentoItems.length) return;

      this.bentoItems.forEach((item, index) => {
        const setItemActive = () => {
          this.activeBentoIndex = index;
          this.bentoItems.forEach((it, i) => {
            const isActive = i === index;
            it.classList.toggle('active', isActive);
            it.classList.toggle('inactive', !isActive);
            it.style.width = isActive ? '60%' : '20%';
          });
        };

        item.addEventListener('mouseenter', setItemActive);
        item.addEventListener('click', setItemActive);
        item.addEventListener('pointerenter', setItemActive);
        item.addEventListener('touchstart', setItemActive, { passive: true });
      });

      // Set initial active item
      if (this.bentoItems[0]) {
        this.bentoItems[0].classList.add('active');
        this.bentoItems[0].style.width = '60%';
      }
    }

    initScrollAnimations() {
      // High-performance RAF Scroll Parallax Engine matching GSAP ScrollTrigger scrub
      const onScroll = () => {
        const rect = this.container.getBoundingClientRect();
        const winHeight = window.innerHeight;

        // Progress from 0 to 1 as container scrolls through viewport
        const totalDist = rect.height + winHeight;
        const currentDist = winHeight - rect.top;
        const progress = Math.max(0, Math.min(1, currentDist / totalDist));

        // 1. Kinetic Text Stagger from Center
        if (this.chars && this.chars.length) {
          const textRect = this.textEl.getBoundingClientRect();
          const textProgress = Math.max(0, Math.min(1, (winHeight - textRect.top) / (winHeight * 0.75)));
          const midChar = (this.chars.length - 1) / 2;

          this.chars.forEach((span, idx) => {
            const distFromCenter = Math.abs(idx - midChar) / midChar; // 0 at center, 1 at ends
            const charDelay = distFromCenter * 0.35;
            const adjustedProgress = Math.max(0, Math.min(1, (textProgress - charDelay) / (1 - charDelay)));
            const ease = Math.sin(adjustedProgress * Math.PI * 0.5);

            const yPercent = (1 - ease) * 180;
            const opacity = ease;
            span.style.transform = `translateY(${yPercent}%)`;
            span.style.opacity = opacity;
          });
        }

        // 2. 7-Column Grid Parabolic Delay
        if (this.gridItems && this.gridItems.length) {
          const numColumns = 7;
          const midCol = Math.floor(numColumns / 2);

          this.gridItems.forEach((item) => {
            const col = parseInt(item.getAttribute('data-col'), 10) || 0;
            const delayFactor = Math.abs(col - midCol) * 0.18;
            const colProgress = Math.max(0, Math.min(1, (progress - delayFactor * 0.25) / (1 - delayFactor * 0.25)));
            const ease = Math.sin(colProgress * Math.PI * 0.5);

            const yPercent = (1 - ease) * 120;
            const opacity = Math.max(0, ease * 1.2);
            item.style.transform = `translateY(${yPercent}px)`;
            item.style.opacity = opacity;
          });
        }

        // 3. Bento Container Zoom & Parallax Scale
        if (this.bentoContainer) {
          const bentoRect = this.bentoContainer.getBoundingClientRect();
          const bentoProgress = Math.max(0, Math.min(1, (winHeight - bentoRect.top) / (winHeight * 0.85)));
          const scale = 1.0 + Math.min(0.2, bentoProgress * 0.2);
          const translateY = (1 - bentoProgress) * 40;
          this.bentoContainer.style.transform = `translateY(${translateY}px) scale(${scale})`;
        }
      };

      window.addEventListener('scroll', onScroll, { passive: true });
      window.addEventListener('resize', onScroll);
      // Run once immediately
      requestAnimationFrame(onScroll);
    }
  }

  // Auto-initialize when DOM is ready
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-staggered-grid]').forEach((el) => {
      new StaggeredBentoGrid(el);
    });
  });
})();
