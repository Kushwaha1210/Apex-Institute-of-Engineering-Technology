/**
 * Scroll-Triggered Reveal & 3D Interactive Motion Engine
 * ====================================================
 * Automatically adds smooth scroll entrance animations,
 * and enables subtle 3D hover tilt strictly on compact cards
 * (Excludes wide data tables, search filters, and exam question forms).
 */

document.addEventListener("DOMContentLoaded", function () {
  // 1. Target all interactive cards, plates, and storytelling panels
  const targetSelectors = [
    ".glass-card",
    ".glass-plate",
    ".exam-card-v2",
    ".featured-glow-card",
    ".widget-today-note",
    ".widget-my-files",
    ".widget-activity",
    ".auth-card",
    ".data-table",
    ".stat-card",
    ".story-step",
    ".cert-paper"
  ];

  const panels = document.querySelectorAll(targetSelectors.join(", "));

  // Add scroll-reveal class initially
  panels.forEach((panel) => {
    panel.classList.add("scroll-reveal");
  });

  // 2. IntersectionObserver to trigger smooth entrance when scrolling down
  if ("IntersectionObserver" in window) {
    const observerOptions = {
      root: null,
      threshold: 0.05,
      rootMargin: "0px 0px -20px 0px"
    };

    const scrollObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          entry.target.classList.add("visible");
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);

    panels.forEach((panel) => {
      const rect = panel.getBoundingClientRect();
      if (rect.top < window.innerHeight && rect.bottom > 0) {
        panel.classList.add("is-visible", "visible");
      } else {
        scrollObserver.observe(panel);
      }
    });
  } else {
    panels.forEach((panel) => panel.classList.add("is-visible", "visible"));
  }

  // 3. 3D Card Hover Tilt ONLY on compact cards (Excluding Data Tables, Forms & Exam Cards)
  const tiltableCards = document.querySelectorAll(
    ".exam-card-v2, .auth-card, .featured-glow-card, .widget-today-note, .widget-my-files, .widget-activity, .story-step .glass-card"
  );

  tiltableCards.forEach((card) => {
    // Exclude if contains table, form, or is wide container
    if (
      card.querySelector("table") ||
      card.querySelector("form") ||
      card.closest("#exam-form") ||
      card.classList.contains("question-card") ||
      card.classList.contains("question-step-card")
    ) {
      return;
    }

    card.style.transformStyle = "preserve-3d";
    card.style.transition = "transform 0.12s ease-out, box-shadow 0.25s ease, border-color 0.25s ease";

    card.addEventListener("mousemove", (e) => {
      // Don't tilt if card is wider than 650px (e.g. full-width data tables)
      const rect = card.getBoundingClientRect();
      if (rect.width > 650) return;

      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      // Subtle 3D Tilt
      const rotX = -((y - centerY) / centerY) * 8;
      const rotY = ((x - centerX) / centerX) * 8;

      card.style.setProperty(
        "transform",
        `perspective(1000px) rotateX(${rotX.toFixed(2)}deg) rotateY(${rotY.toFixed(2)}deg) translateY(-6px) scale3d(1.01, 1.01, 1.01)`,
        "important"
      );
    });

    card.addEventListener("mouseleave", () => {
      card.style.setProperty(
        "transform",
        "perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0) scale3d(1, 1, 1)",
        "important"
      );
    });
  });
});
