/**
 * Live Examination Engine with Robust Step-by-Step Question Navigation
 * ====================================================================
 * 1. Synchronized single-question step view (strictly sequential index + 1 / - 1)
 * 2. Instant palette synchronization (exact button index matches question index)
 * 3. Live countdown timer & auto-submission
 * 4. Anti-cheating proctoring (tab-switch & focus loss logging)
 * 5. Fullscreen toggle
 */

document.addEventListener("DOMContentLoaded", function () {
  const examForm = document.getElementById("exam-form");
  if (!examForm) return;

  // ==========================================
  // 1. Step-by-Step Question Navigation Engine
  // ==========================================
  const questionCards = Array.from(document.querySelectorAll(".question-step-card"));
  const totalQuestions = questionCards.length;
  let currentQuestionIndex = 0;

  const currentQIndexDisplay = document.getElementById("current-q-index");
  const examProgressFill = document.getElementById("exam-progress-fill");
  const paletteButtons = Array.from(document.querySelectorAll(".palette-btn"));

  function showQuestion(index) {
    if (index < 0 || index >= totalQuestions) return;
    currentQuestionIndex = index;

    // Show only the current active question card
    questionCards.forEach((card, idx) => {
      if (idx === index) {
        card.style.display = "block";
        card.style.opacity = "1";
        card.classList.add("active-question");
      } else {
        card.style.display = "none";
        card.classList.remove("active-question");
      }
    });

    // Update Question Counter (e.g. Question 1 of 10)
    if (currentQIndexDisplay) {
      currentQIndexDisplay.innerText = index + 1;
    }

    // Update Progress Bar Fill
    if (examProgressFill && totalQuestions > 0) {
      const progressPercent = Math.round(((index + 1) / totalQuestions) * 100);
      examProgressFill.style.width = `${progressPercent}%`;
    }

    // Highlight current active question in Palette strictly by index matching
    paletteButtons.forEach((btn, idx) => {
      const btnIndex = parseInt(btn.getAttribute("data-index"));
      if (btnIndex === index) {
        btn.classList.add("current-active");
      } else {
        btn.classList.remove("current-active");
      }
    });

    // Scroll to top of exam container and trigger 3D FlipText animation
    const activeCard = questionCards[index];
    if (activeCard) {
      if (window.FlipText && typeof window.FlipText.animateCard === 'function') {
        window.FlipText.animateCard(activeCard);
      }

      window.scrollTo({
        top: activeCard.offsetTop - 120,
        behavior: "smooth"
      });
    }
  }

  // Bind Next Question Buttons -> Always advance by exactly +1
  document.querySelectorAll(".btn-next-question").forEach((btn) => {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      showQuestion(currentQuestionIndex + 1);
    });
  });

  // Bind Previous Question Buttons -> Always retreat by exactly -1
  document.querySelectorAll(".btn-prev-question").forEach((btn) => {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      showQuestion(currentQuestionIndex - 1);
    });
  });

  // Bind Question Palette Buttons to jump directly to target index
  paletteButtons.forEach((btn) => {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      const targetIndex = parseInt(this.getAttribute("data-index"));
      if (!isNaN(targetIndex)) {
        showQuestion(targetIndex);
      }
    });
  });

  // Show Question 1 initially
  showQuestion(0);

  // ==========================================
  // 2. Question Palette State Management
  // ==========================================
  const optionsInputs = document.querySelectorAll(".option-radio");
  const flaggedQuestions = new Set();

  function updateQuestionState(questionId) {
    const btn = document.getElementById(`palette-btn-${questionId}`);
    if (!btn) return;

    const isAnswered = document.querySelector(`input[name="question_${questionId}"]:checked`);
    const isFlagged = flaggedQuestions.has(questionId);

    btn.classList.remove("answered", "unanswered", "flagged", "not-visited");

    if (isFlagged) {
      btn.classList.add("flagged");
    } else if (isAnswered) {
      btn.classList.add("answered");
    } else {
      btn.classList.add("unanswered");
    }
  }

  optionsInputs.forEach((input) => {
    input.addEventListener("change", function () {
      const qId = this.getAttribute("data-qid");
      updateQuestionState(qId);
    });
  });

  // Flag / Mark for Review button
  const flagButtons = document.querySelectorAll(".btn-flag-review");
  flagButtons.forEach((btn) => {
    btn.addEventListener("click", function () {
      const qId = this.getAttribute("data-qid");
      if (flaggedQuestions.has(qId)) {
        flaggedQuestions.delete(qId);
        this.innerHTML = "⭐ Mark for Review";
      } else {
        flaggedQuestions.add(qId);
        this.innerHTML = "🌟 Flagged (Review)";
      }
      updateQuestionState(qId);
    });
  });

  // Clear Selection button
  const clearButtons = document.querySelectorAll(".btn-clear-selection");
  clearButtons.forEach((btn) => {
    btn.addEventListener("click", function () {
      const qId = this.getAttribute("data-qid");
      const radios = document.querySelectorAll(`input[name="question_${qId}"]`);
      radios.forEach((r) => (r.checked = false));
      flaggedQuestions.delete(qId);
      updateQuestionState(qId);
    });
  });

  // ==========================================
  // 3. Live Countdown Timer
  // ==========================================
  const timerElement = document.getElementById("exam-timer-display");
  let remainingSeconds = parseInt(timerElement.getAttribute("data-seconds")) || 1800;

  function updateTimer() {
    if (remainingSeconds <= 0) {
      clearInterval(timerInterval);
      timerElement.innerText = "00:00";
      alert("⏳ Time limit reached! Your examination is being automatically submitted.");
      examForm.submit();
      return;
    }

    remainingSeconds--;
    const minutes = Math.floor(remainingSeconds / 60);
    const seconds = remainingSeconds % 60;
    timerElement.innerText = `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;

    if (remainingSeconds < 300) {
      timerElement.classList.add("timer-warning");
    }
  }

  const timerInterval = setInterval(updateTimer, 1000);

  // ==========================================
  // 4. Anti-Cheating: Tab-Switch Detection
  // ==========================================
  let violationsCount = 0;
  const violationsInput = document.getElementById("violations_count");
  const warningModal = document.getElementById("tab-warning-modal");
  const warningCountSpan = document.getElementById("warning-count-display");

  window.addEventListener("blur", function () {
    violationsCount++;
    if (violationsInput) violationsInput.value = violationsCount;

    if (warningCountSpan) warningCountSpan.innerText = violationsCount;
    if (warningModal) warningModal.style.display = "flex";

    if (violationsCount >= 3) {
      alert("⚠️ Multiple tab-switching violations detected! Your examination is being terminated and submitted.");
      examForm.submit();
    }
  });

  const dismissWarningBtn = document.getElementById("dismiss-warning-btn");
  if (dismissWarningBtn) {
    dismissWarningBtn.addEventListener("click", function () {
      if (warningModal) warningModal.style.display = "none";
    });
  }

  // Prevent Right-Click & Copy-Paste
  document.addEventListener("contextmenu", (e) => e.preventDefault());
  document.addEventListener("copy", (e) => e.preventDefault());
  document.addEventListener("cut", (e) => e.preventDefault());

  // ==========================================
  // 5. Fullscreen Toggle
  // ==========================================
  const fullscreenBtn = document.getElementById("toggle-fullscreen-btn");
  if (fullscreenBtn) {
    fullscreenBtn.addEventListener("click", function () {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch((err) => {
          console.warn("Fullscreen request error:", err);
        });
      } else {
        document.exitFullscreen();
      }
    });
  }
});
