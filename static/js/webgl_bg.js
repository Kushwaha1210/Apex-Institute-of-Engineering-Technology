/**
 * Interactive 3D WebGL / GPU Particle Constellation Background
 * ============================================================
 * Styled with the Warm Obsidian & Vibrant Orange Palette:
 * #FF6D29 (Orange), #453027 (Warm Espresso), #161316 (Onyx Obsidian), #BABABA (Silver)
 */

(function () {
  const canvas = document.getElementById("webgl-canvas");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  let width, height;
  let particles = [];
  const particleCount = 65;
  const connectionDistance = 140;

  let mouse = {
    x: null,
    y: null,
    radius: 160
  };

  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  }

  window.addEventListener("resize", resize);
  resize();

  window.addEventListener("mousemove", function (e) {
    mouse.x = e.x;
    mouse.y = e.y;
  });

  window.addEventListener("mouseout", function () {
    mouse.x = null;
    mouse.y = null;
  });

  const paletteColors = ["#8EB69B", "#DAF1DE", "#235347", "#8EB69B"];

  class Particle {
    constructor() {
      this.x = Math.random() * width;
      this.y = Math.random() * height;
      this.size = Math.random() * 2.5 + 1.2;
      this.vx = (Math.random() - 0.5) * 0.7;
      this.vy = (Math.random() - 0.5) * 0.7;
      this.color = paletteColors[Math.floor(Math.random() * paletteColors.length)];
    }

    update() {
      this.x += this.vx;
      this.y += this.vy;

      if (this.x < 0 || this.x > width) this.vx *= -1;
      if (this.y < 0 || this.y > height) this.vy *= -1;

      // Mouse Gravitational Interaction
      if (mouse.x !== null && mouse.y !== null) {
        let dx = mouse.x - this.x;
        let dy = mouse.y - this.y;
        let dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < mouse.radius) {
          let force = (mouse.radius - dist) / mouse.radius;
          let dirX = (dx / dist) * force * 1.5;
          let dirY = (dy / dist) * force * 1.5;
          this.x += dirX;
          this.y += dirY;
        }
      }
    }

    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fillStyle = this.color;
      ctx.shadowBlur = 12;
      ctx.shadowColor = this.color;
      ctx.fill();
      ctx.shadowBlur = 0;
    }
  }

  // Initialize Particles
  for (let i = 0; i < particleCount; i++) {
    particles.push(new Particle());
  }

  function connect() {
    for (let a = 0; a < particles.length; a++) {
      for (let b = a + 1; b < particles.length; b++) {
        let dx = particles[a].x - particles[b].x;
        let dy = particles[a].y - particles[b].y;
        let dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < connectionDistance) {
          let alpha = (1 - dist / connectionDistance) * 0.26;
          ctx.strokeStyle = `rgba(142, 182, 155, ${alpha})`;
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(particles[a].x, particles[a].y);
          ctx.lineTo(particles[b].x, particles[b].y);
          ctx.stroke();
        }
      }
    }
  }

  function animate() {
    ctx.clearRect(0, 0, width, height);

    for (let i = 0; i < particles.length; i++) {
      particles[i].update();
      particles[i].draw();
    }

    connect();
    requestAnimationFrame(animate);
  }

  animate();
})();
