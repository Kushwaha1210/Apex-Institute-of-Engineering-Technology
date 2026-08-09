/**
 * FlipFadeText & FlipText - 3D Kinetic Character Flip & Word Cycler Engine
 * =======================================================================
 * Framer Motion Parity Specification:
 * - Word cycling with interval (default 2500ms)
 * - Initial: rotateX: 90deg, y: 20px, opacity: 0, filter: blur(8px)
 * - Animate: rotateX: 0deg, y: 0px, opacity: 1, filter: blur(0px), ease: [0.2, 0.65, 0.3, 0.9]
 * - Exit: rotateX: -90deg, y: -20px, opacity: 0, filter: blur(8px), ease: easeIn
 * - Enter staggerDelay: 0.08s, Exit staggerDelay: 0.04s
 * - Seamless question transition in Exam Proctoring
 */

class FlipFadeText {
  constructor(container, options = {}) {
    this.container = typeof container === 'string' ? document.querySelector(container) : container;
    if (!this.container) return;

    this.options = Object.assign({
      words: ["ONLINE ASSESSMENTS", "LIVE ANTI-CHEAT", "AUTO GRADING", "DIGITAL CERTIFICATION", "ACADEMIC SENTINEL"],
      interval: 2500,
      letterDuration: 0.6,
      staggerDelay: 0.08,
      exitStaggerDelay: 0.04,
      textClassName: ""
    }, options);

    // Read data attributes if present
    if (this.container.dataset.words) {
      try {
        this.options.words = JSON.parse(this.container.dataset.words);
      } catch (e) {
        this.options.words = this.container.dataset.words.split(",").map(w => w.trim());
      }
    }
    if (this.container.dataset.interval) {
      this.options.interval = parseInt(this.container.dataset.interval, 10);
    }

    this.currentIndex = 0;
    this.timer = null;
    this.isTransitioning = false;

    this.init();
  }

  init() {
    this.container.classList.add("flip-fade-wrapper");
    this.container.style.perspective = "1000px";
    this.container.style.display = "inline-block";

    this.renderWord(this.options.words[0], false);

    if (this.options.words.length > 1) {
      this.startCycle();
    }
  }

  renderWord(wordText, isAnimated = true) {
    const wordEl = document.createElement("div");
    wordEl.className = `flip-fade-word ${this.options.textClassName}`;
    wordEl.style.display = "inline-flex";
    wordEl.style.gap = "0.08em";
    wordEl.style.transformStyle = "preserve-3d";

    const chars = wordText.split("");
    chars.forEach((char, i) => {
      const letterSpan = document.createElement("span");
      letterSpan.className = "flip-fade-letter enter";
      letterSpan.style.display = "inline-block";
      letterSpan.style.transformStyle = "preserve-3d";
      letterSpan.style.willChange = "transform, opacity, filter";
      letterSpan.style.animationDuration = `${this.options.letterDuration}s`;
      letterSpan.style.animationDelay = `${i * this.options.staggerDelay}s`;
      letterSpan.style.animationTimingFunction = "cubic-bezier(0.2, 0.65, 0.3, 0.9)";
      letterSpan.style.animationFillMode = "both";
      letterSpan.innerHTML = char === " " ? "&nbsp;" : char;

      wordEl.appendChild(letterSpan);
    });

    this.container.innerHTML = "";
    this.container.appendChild(wordEl);
  }

  next() {
    if (this.isTransitioning) return;
    this.isTransitioning = true;

    const currentWordEl = this.container.querySelector(".flip-fade-word");
    const nextIndex = (this.currentIndex + 1) % this.options.words.length;
    const nextWordText = this.options.words[nextIndex];

    if (currentWordEl) {
      const letters = Array.from(currentWordEl.querySelectorAll(".flip-fade-letter"));
      
      // Trigger exit animation on each letter with exitStaggerDelay
      letters.forEach((letter, i) => {
        letter.classList.remove("enter");
        letter.classList.add("exit");
        letter.style.animationDuration = `${this.options.letterDuration * 0.67}s`;
        letter.style.animationDelay = `${i * this.options.exitStaggerDelay}s`;
        letter.style.animationTimingFunction = "ease-in";
      });

      const totalExitTime = (letters.length * this.options.exitStaggerDelay + this.options.letterDuration * 0.67) * 1000;

      setTimeout(() => {
        this.currentIndex = nextIndex;
        this.renderWord(nextWordText, true);
        this.isTransitioning = false;
      }, Math.max(300, totalExitTime * 0.85));
    } else {
      this.currentIndex = nextIndex;
      this.renderWord(nextWordText, true);
      this.isTransitioning = false;
    }
  }

  startCycle() {
    this.stopCycle();
    this.timer = setInterval(() => {
      this.next();
    }, this.options.interval);
  }

  stopCycle() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }
}

class FlipText {
  static createFlipHTML(text, options = {}) {
    const duration = options.duration || 0.6;
    const delay = options.delay || 0;
    const loop = options.loop || false;
    const separator = options.separator || " ";
    const together = options.together || false;

    const words = text.split(separator);
    const totalChars = text.length || 1;

    let globalIndex = 0;
    let html = `<div class="flip-text-wrapper" style="perspective: 1000px; display: inline-block; width: 100%; white-space: normal;">`;

    words.forEach((word, wordIndex) => {
      html += `<span class="word" style="display: inline-block; white-space: normal; transform-style: preserve-3d;">`;
      const chars = word.split("");

      chars.forEach((char) => {
        let calculatedDelay = delay;
        if (!together) {
          const normalizedIndex = globalIndex / totalChars;
          const sineValue = Math.sin(normalizedIndex * (Math.PI / 2));
          calculatedDelay = sineValue * (duration * 0.35) + delay;
        }

        const isSpace = char === " ";
        html += `<span class="flip-char" data-char="${char}" style="--flip-duration: ${duration}s; --flip-delay: ${calculatedDelay.toFixed(3)}s; --flip-iteration: ${loop ? 'infinite' : '1'}; display: inline-block; transform-style: preserve-3d;">${isSpace ? '&nbsp;' : char}</span>`;
        globalIndex++;
      });

      if (separator === " " && wordIndex < words.length - 1) {
        html += `<span class="whitespace" style="display: inline-block;">&nbsp;</span>`;
        globalIndex++;
      } else if (separator !== " " && wordIndex < words.length - 1) {
        html += `<span class="separator" style="display: inline-block;">${separator}</span>`;
        globalIndex += separator.length;
      }

      html += `</span>`;
    });

    html += `</div>`;
    return html;
  }

  static applyToElement(el, options = {}) {
    if (!el || el.getAttribute("data-flip-applied") === "true") return;
    const rawText = el.getAttribute("data-flip-text") || el.innerText.trim();
    if (!rawText) return;

    el.setAttribute("data-flip-applied", "true");
    el.setAttribute("data-original-text", rawText);
    el.innerHTML = FlipText.createFlipHTML(rawText, options);
  }

  static animateCard(cardEl) {
    if (!cardEl) return;
    
    // 1. Flip question text with letter-by-letter kinetic stagger
    const qTextEl = cardEl.querySelector(".question-text");
    if (qTextEl) {
      const text = qTextEl.getAttribute("data-original-text") || qTextEl.innerText.trim();
      qTextEl.setAttribute("data-original-text", text);
      qTextEl.innerHTML = FlipText.createFlipHTML(text, { duration: 0.55, delay: 0.04 });
    }

    // 2. Flip all option labels with staggered wave
    const optionLabels = cardEl.querySelectorAll(".option-label");
    optionLabels.forEach((labelEl, idx) => {
      const optText = labelEl.getAttribute("data-original-text") || labelEl.innerText.trim();
      labelEl.setAttribute("data-original-text", optText);
      labelEl.innerHTML = FlipText.createFlipHTML(optText, {
        duration: 0.45,
        delay: 0.1 + idx * 0.05
      });
    });

    // 3. Subtle 3D lift pop on the card container
    cardEl.style.animation = "none";
    cardEl.offsetHeight; // trigger reflow
    cardEl.style.animation = "cardPopIn 0.5s cubic-bezier(0.2, 0.65, 0.3, 0.9) both";
  }

  static init() {
    // Auto-init single flip text elements
    document.querySelectorAll("[data-flip-text]").forEach((el) => {
      const duration = parseFloat(el.getAttribute("data-flip-duration")) || 0.75;
      const delay = parseFloat(el.getAttribute("data-flip-delay")) || 0;
      FlipText.applyToElement(el, { duration, delay });
    });

    // Auto-init FlipFadeText word cyclers
    document.querySelectorAll("[data-flip-fade]").forEach((el) => {
      new FlipFadeText(el);
    });
  }
}

// Global auto initialization on DOM ready
document.addEventListener("DOMContentLoaded", () => {
  FlipText.init();
});

window.FlipText = FlipText;
window.FlipFadeText = FlipFadeText;

