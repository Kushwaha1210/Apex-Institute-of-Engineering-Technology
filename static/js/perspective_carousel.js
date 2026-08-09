/**
 * PerspectiveCarousel - 3D Perspective Coverflow Carousel Engine
 * Vanilla JS conversion matching the Framer Motion 3D Rotation specification:
 * - 3D Stage with perspective: 1200px
 * - Interactive Y-Axis Rotation step (rotationStep)
 * - Inactive Scale damping (inactiveScale)
 * - Spring-damped smooth transitions
 * - Left/Right Chevron controls + Expandable Indicator Dots
 * - Touch Swipe & Drag gestures + Keyboard Arrow navigation
 * - Auto-rotation / Infinite loop support
 */

class PerspectiveCarousel {
  constructor(container, options = {}) {
    this.container = typeof container === 'string' ? document.querySelector(container) : container;
    if (!this.container) return;

    this.options = Object.assign({
      slideWidth: 320,
      rotationStep: 36, // degrees rotation per offset index
      inactiveScale: 0.84,
      loop: true,
      autoPlay: true,
      autoPlayInterval: 4500,
      showControls: true,
      showDots: true,
      onActiveChange: null
    }, options);

    this.viewport = this.container.querySelector('.perspective-viewport') || this.container;
    this.track = this.container.querySelector('.perspective-track');
    this.slides = Array.from(this.container.querySelectorAll('.perspective-slide'));
    
    if (!this.slides.length) return;

    this.currentIndex = 0;
    this.maxIndex = this.slides.length - 1;
    this.isDragging = false;
    this.startX = 0;
    this.currentX = 0;
    this.timer = null;

    // Pre-calculated rotation angles for organic physical 3D card stacking (matching TestimonialsCard specification)
    this.rotations = [4, -2, -9, 7, -5, 6, -3];

    this.init();
  }

  init() {
    this.container.classList.add('perspective-carousel-initialized');
    this.container.setAttribute('tabindex', '0');
    this.container.setAttribute('role', 'region');
    this.container.setAttribute('aria-roledescription', '3D perspective card stack');

    // Build top counter indicator
    this.buildCounter();

    // Build controls if not already in markup
    this.buildControls();

    // Attach Event Listeners
    this.bindEvents();

    // Initial render
    this.update();

    // Start Autoplay if enabled
    if (this.options.autoPlay) {
      this.startAutoPlay();
    }
  }

  buildCounter() {
    if (this.options.showCounter === false) return;
    let counter = this.container.querySelector('.perspective-counter');
    if (!counter) {
      counter = document.createElement('div');
      counter.className = 'perspective-counter';
      this.container.appendChild(counter);
    }
    this.counterEl = counter;
  }

  buildControls() {
    if (!this.options.showControls) return;

    let controlsBar = this.container.querySelector('.perspective-controls');
    if (!controlsBar) {
      controlsBar = document.createElement('div');
      controlsBar.className = 'perspective-controls';

      // Left Chevron
      const prevBtn = document.createElement('button');
      prevBtn.type = 'button';
      prevBtn.className = 'perspective-btn perspective-prev';
      prevBtn.setAttribute('aria-label', 'Previous slide');
      prevBtn.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="15 18 9 12 15 6"></polyline>
        </svg>
      `;
      prevBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.prev();
      });
      controlsBar.appendChild(prevBtn);

      // Dots Indicator Container
      if (this.options.showDots) {
        const dotsContainer = document.createElement('div');
        dotsContainer.className = 'perspective-dots';
        
        this.slides.forEach((_, idx) => {
          const dot = document.createElement('button');
          dot.type = 'button';
          dot.className = `perspective-dot ${idx === 0 ? 'active' : ''}`;
          dot.setAttribute('aria-label', `Go to slide ${idx + 1}`);
          dot.addEventListener('click', (e) => {
            e.stopPropagation();
            this.goTo(idx);
          });
          dotsContainer.appendChild(dot);
        });
        controlsBar.appendChild(dotsContainer);
      }

      // Right Chevron
      const nextBtn = document.createElement('button');
      nextBtn.type = 'button';
      nextBtn.className = 'perspective-btn perspective-next';
      nextBtn.setAttribute('aria-label', 'Next slide');
      nextBtn.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="9 18 15 12 9 6"></polyline>
        </svg>
      `;
      nextBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.next();
      });
      controlsBar.appendChild(nextBtn);

      this.container.appendChild(controlsBar);
    }
  }

  bindEvents() {
    // Keyboard navigation
    this.container.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft') {
        e.preventDefault();
        this.prev();
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        this.next();
      }
    });

    // Slide Click to Focus
    this.slides.forEach((slide, idx) => {
      slide.addEventListener('click', () => {
        if (this.currentIndex !== idx) {
          this.goTo(idx);
        }
      });
    });

    // Touch & Pointer Drag Gestures
    this.viewport.addEventListener('pointerdown', (e) => this.onDragStart(e));
    window.addEventListener('pointermove', (e) => this.onDragMove(e));
    window.addEventListener('pointerup', () => this.onDragEnd());
    window.addEventListener('pointercancel', () => this.onDragEnd());

    // Pause on Hover
    this.container.addEventListener('mouseenter', () => this.stopAutoPlay());
    this.container.addEventListener('mouseleave', () => {
      if (this.options.autoPlay) this.startAutoPlay();
    });
  }

  onDragStart(e) {
    if (e.button !== 0 && e.pointerType === 'mouse') return;
    this.isDragging = true;
    this.startX = e.clientX;
    this.currentX = e.clientX;
    this.stopAutoPlay();
  }

  onDragMove(e) {
    if (!this.isDragging) return;
    this.currentX = e.clientX;
  }

  onDragEnd() {
    if (!this.isDragging) return;
    this.isDragging = false;
    const diffX = this.currentX - this.startX;
    
    if (Math.abs(diffX) > 40) {
      if (diffX > 0) {
        this.prev();
      } else {
        this.next();
      }
    }

    if (this.options.autoPlay) {
      this.startAutoPlay();
    }
  }

  goTo(index) {
    if (this.options.loop) {
      this.currentIndex = (index + this.slides.length) % this.slides.length;
    } else {
      this.currentIndex = Math.max(0, Math.min(index, this.maxIndex));
    }
    this.update();
  }

  next() {
    this.goTo(this.currentIndex + 1);
  }

  prev() {
    this.goTo(this.currentIndex - 1);
  }

  update() {
    const total = this.slides.length;
    const centerIndex = this.currentIndex;

    this.slides.forEach((slide, idx) => {
      let offset = idx - centerIndex;

      // Handle shortest wrapping offset if loop is true
      if (this.options.loop) {
        if (offset > total / 2) offset -= total;
        if (offset < -total / 2) offset += total;
      }

      const absOffset = Math.abs(offset);
      const isActive = offset === 0;

      slide.classList.toggle('active', isActive);
      slide.classList.toggle('inactive', !isActive);
      slide.setAttribute('aria-current', isActive ? 'true' : 'false');

      // 3D Testimonials Stack Depth + Rotations Physics
      const rotZ = isActive ? 0 : this.rotations[Math.abs(idx) % this.rotations.length];
      const rotateY = offset * -this.options.rotationStep * 0.6;
      const scale = isActive ? 1.0 : Math.max(0.76, this.options.inactiveScale - (absOffset - 1) * 0.05);
      const translateX = offset * (this.options.slideWidth * 0.72);
      const translateY = isActive ? 0 : Math.abs(offset) * 6;
      const translateZ = isActive ? 0 : -90 * absOffset;
      const opacity = isActive ? 1 : Math.max(0.24, 0.76 - (absOffset - 1) * 0.22);
      const zIndex = isActive ? 100 : 50 - absOffset;

      slide.style.transform = `translate3d(${translateX}px, ${translateY}px, ${translateZ}px) rotateY(${rotateY}deg) rotateZ(${rotZ}deg) scale(${scale})`;
      slide.style.zIndex = zIndex;
      slide.style.opacity = opacity;
      slide.style.filter = 'none';
      slide.style.pointerEvents = absOffset > 3 ? 'none' : 'auto';
    });

    // Update Counter (e.g. "02 / 07")
    if (this.counterEl) {
      const currentFormatted = String(centerIndex + 1).padStart(2, '0');
      const totalFormatted = String(total).padStart(2, '0');
      this.counterEl.innerText = `${currentFormatted} / ${totalFormatted}`;
    }

    // Update Dots indicator
    const dots = this.container.querySelectorAll('.perspective-dot');
    dots.forEach((dot, idx) => {
      dot.classList.toggle('active', idx === centerIndex);
    });

    // Update Disabled state on buttons if non-looping
    if (!this.options.loop) {
      const prevBtn = this.container.querySelector('.perspective-prev');
      const nextBtn = this.container.querySelector('.perspective-next');
      if (prevBtn) prevBtn.disabled = this.currentIndex === 0;
      if (nextBtn) nextBtn.disabled = this.currentIndex === this.maxIndex;
    }

    if (typeof this.options.onActiveChange === 'function') {
      this.options.onActiveChange(centerIndex, this.slides[centerIndex]);
    }
  }

  startAutoPlay() {
    this.stopAutoPlay();
    this.timer = setInterval(() => {
      this.next();
    }, this.options.autoPlayInterval);
  }

  stopAutoPlay() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }
}

// Global auto-initializer for any element with data-perspective-carousel
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-perspective-carousel]').forEach((el) => {
    new PerspectiveCarousel(el, {
      slideWidth: parseInt(el.dataset.slideWidth, 10) || 340,
      rotationStep: parseInt(el.dataset.rotationStep, 10) || 38,
      inactiveScale: parseFloat(el.dataset.inactiveScale) || 0.82,
      loop: el.dataset.loop !== 'false',
      autoPlay: el.dataset.autoplay !== 'false'
    });
  });
});
