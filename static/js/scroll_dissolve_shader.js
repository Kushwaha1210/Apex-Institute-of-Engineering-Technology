/**
 * ScrollDissolveShader - WebGL GPU Shader Engine
 * ===============================================
 * Exact implementation of the Sobel Edge Detection + FBM Noise Dissolve + Sparkle Shader:
 * - Sobel Convolution Kernel for high-frequency edge luminescence
 * - 5-Octave Fractal Brownian Motion (FBM) procedural domain warping
 * - Pixelated Edge Sparkle & Holographic Emission
 * - Dynamic scroll-driven progress (uDissolve, uGrayscale, uEdgeIntensity)
 * - Mouse cursor focal warp (uCenter)
 * - Palette: Electric Green (#33BC65), Neon Cyan (#12DCEF), Aqua Mint (#5DFFD9), Obsidian (#070707)
 */

(function () {
  class ScrollDissolveShader {
    constructor(canvasId) {
      this.canvas = typeof canvasId === 'string' ? document.getElementById(canvasId) : canvasId;
      if (!this.canvas) return;

      this.gl = this.canvas.getContext('webgl', { alpha: true, antialias: true, premultipliedAlpha: false }) ||
                this.canvas.getContext('experimental-webgl');
      if (!this.gl) return;

      this.width = window.innerWidth;
      this.height = window.innerHeight;
      this.scrollProgress = 0;
      this.mouse = { x: 0.5, y: 0.5, targetX: 0.5, targetY: 0.5 };
      this.startTime = performance.now();

      this.init();
    }

    init() {
      const gl = this.gl;

      const vertexShaderSource = `
        attribute vec2 a_position;
        varying vec2 vUv;
        void main() {
          vUv = (a_position + 1.0) * 0.5;
          gl_Position = vec4(a_position, 0.0, 1.0);
        }
      `;

      const fragmentShaderSource = `
        precision highp float;
        uniform vec2 uResolution;
        uniform float uDissolve;
        uniform vec2 uCenter;
        uniform float uTime;
        uniform float uGrayscale;
        uniform float uEdgeIntensity;
        uniform float uEdgeBrightness;
        varying vec2 vUv;

        mat3 sobelX = mat3(
          -1.0, 0.0, 1.0,
          -2.0, 0.0, 2.0,
          -1.0, 0.0, 1.0
        );

        mat3 sobelY = mat3(
          -1.0, -2.0, -1.0,
           0.0,  0.0,  0.0,
           1.0,  2.0,  1.0
        );

        float getLuminance(vec3 color) {
          return dot(color, vec3(0.299, 0.587, 0.114));
        }

        float hash(vec2 p) {
          return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
        }

        float noise(vec2 p) {
          vec2 i = floor(p);
          vec2 f = fract(p);
          f = f * f * (3.0 - 2.0 * f);
          
          float a = hash(i);
          float b = hash(i + vec2(1.0, 0.0));
          float c = hash(i + vec2(0.0, 1.0));
          float d = hash(i + vec2(1.0, 1.0));
          
          return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
        }

        float fbm(vec2 p) {
          float value = 0.0;
          float amplitude = 0.5;
          float frequency = 1.0;
          
          for (int i = 0; i < 5; i++) {
            value += amplitude * noise(p * frequency);
            amplitude *= 0.5;
            frequency *= 2.0;
          }
          
          return value;
        }

        vec3 getSceneColor(vec2 uv) {
          // Procedural cybernetic grid & constellation nebula in our exact palette:
          // #33BC65 (Green), #12DCEF (Cyan), #5DFFD9 (Mint), #070707 (Obsidian)
          vec2 grid = abs(fract(uv * 18.0 - 0.5) - 0.5) / fwidth(uv * 18.0);
          float line = 1.0 - min(min(grid.x, grid.y), 1.0);

          float n1 = fbm(uv * 3.5 + vec2(uTime * 0.04, -uTime * 0.03));
          float n2 = fbm(uv * 6.0 - vec2(-uTime * 0.02, uTime * 0.05) + n1);

          vec3 colGreen = vec3(0.20, 0.74, 0.40); // #33BC65
          vec3 colCyan  = vec3(0.07, 0.86, 0.94); // #12DCEF
          vec3 colMint  = vec3(0.36, 1.00, 0.85); // #5DFFD9
          vec3 colVoid  = vec3(0.03, 0.05, 0.04); // #070707

          vec3 baseNebula = mix(colVoid, colGreen, smoothstep(0.3, 0.8, n1) * 0.45);
          baseNebula = mix(baseNebula, colCyan, smoothstep(0.4, 0.9, n2) * 0.55);
          baseNebula += colMint * (line * 0.22);

          return baseNebula;
        }

        float getSceneEdge(vec2 uv, vec2 texelSize) {
          float gx = 0.0;
          float gy = 0.0;

          for (int i = -1; i <= 1; i++) {
            for (int j = -1; j <= 1; j++) {
              vec2 offset = vec2(float(i), float(j)) * texelSize * 2.0;
              float lum = getLuminance(getSceneColor(uv + offset));
              gx += lum * sobelX[i + 1][j + 1];
              gy += lum * sobelY[i + 1][j + 1];
            }
          }

          return sqrt(gx * gx + gy * gy);
        }

        void main() {
          vec2 uv = vUv;
          vec3 texColor = getSceneColor(uv);

          float gray = getLuminance(texColor.rgb);
          vec3 grayscaleColor = vec3(gray);
          texColor = mix(texColor, grayscaleColor, uGrayscale);

          vec2 centeredUv = vUv - uCenter;
          float aspect = uResolution.x / uResolution.y;
          centeredUv.x *= aspect;
          float dist = length(centeredUv);

          float angle = atan(centeredUv.y, centeredUv.x);

          float noiseScale = 6.0;
          vec2 pixelatedUv = floor(vUv * uResolution / noiseScale) * noiseScale / uResolution;
          float blockNoise = fbm(pixelatedUv * 20.0 + vec2(uTime * 0.08, 0.0)) * 0.15;
          float angularNoise = fbm(vec2(angle * 5.0, uTime * 0.05)) * 0.15;

          float totalNoise = blockNoise + angularNoise;
          float noisyDist = dist + totalNoise;

          float maxDist = length(vec2(aspect * 0.5, 0.5));
          float normalizedDist = noisyDist / maxDist;

          float dissolveThreshold = uDissolve * 1.5;

          vec2 texelSize = 1.0 / uResolution;
          float edge = getSceneEdge(uv, texelSize);

          edge = pow(edge, 0.7) * 2.0;
          edge = clamp(edge, 0.0, 1.0);

          float dissolveMask = smoothstep(dissolveThreshold - 0.03, dissolveThreshold, normalizedDist);

          vec3 edgeColor = vec3(0.36, 1.00, 0.85); // Luminous Aqua Mint (#5DFFD9)

          vec3 baseColor = mix(texColor, vec3(0.0), uGrayscale * 0.5);
          vec3 finalColor = baseColor;

          float edgeGlowIntensity = uEdgeIntensity * 2.0;
          float edgeGlow = edge * edgeGlowIntensity * (1.0 + uGrayscale * 3.0);
          finalColor += edgeColor * edgeGlow * uEdgeBrightness;

          float edgeZoneWidth = 0.15 * (1.0 - uDissolve) + 0.02;
          float edgeZone = smoothstep(dissolveThreshold - edgeZoneWidth, dissolveThreshold - edgeZoneWidth + 0.04, normalizedDist) * 
                           smoothstep(dissolveThreshold + 0.02, dissolveThreshold - 0.02, normalizedDist);
          float sparkle = hash(floor(vUv * uResolution / 4.0) + vec2(floor(uTime * 24.0), 0.0)) * edgeZone;

          float edgeBrightness = (1.0 - uDissolve) * uEdgeBrightness * (1.0 + uGrayscale * 2.0);
          finalColor += vec3(sparkle * 3.0 * edgeBrightness) * edgeColor;

          float alpha = clamp((1.0 - dissolveMask * 0.75) * 0.88, 0.0, 0.95);

          gl_FragColor = vec4(finalColor, alpha);
        }
      `;

      this.program = this.createProgram(vertexShaderSource, fragmentShaderSource);
      gl.useProgram(this.program);

      // Create Fullscreen Quad Buffer
      const positionBuffer = gl.createBuffer();
      gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
      gl.bufferData(
        gl.ARRAY_BUFFER,
        new Float32Array([
          -1.0, -1.0,
           1.0, -1.0,
          -1.0,  1.0,
          -1.0,  1.0,
           1.0, -1.0,
           1.0,  1.0,
        ]),
        gl.STATIC_DRAW
      );

      const positionLocation = gl.getAttribLocation(this.program, "a_position");
      gl.enableVertexAttribArray(positionLocation);
      gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);

      // Cache Uniform Locations
      this.uniforms = {
        uResolution: gl.getUniformLocation(this.program, "uResolution"),
        uDissolve: gl.getUniformLocation(this.program, "uDissolve"),
        uCenter: gl.getUniformLocation(this.program, "uCenter"),
        uTime: gl.getUniformLocation(this.program, "uTime"),
        uGrayscale: gl.getUniformLocation(this.program, "uGrayscale"),
        uEdgeIntensity: gl.getUniformLocation(this.program, "uEdgeIntensity"),
        uEdgeBrightness: gl.getUniformLocation(this.program, "uEdgeBrightness"),
      };

      this.resize();
      this.bindEvents();
      this.render();
    }

    createProgram(vertexSrc, fragmentSrc) {
      const gl = this.gl;
      const vs = gl.createShader(gl.VERTEX_SHADER);
      gl.shaderSource(vs, vertexSrc);
      gl.compileShader(vs);

      const fs = gl.createShader(gl.FRAGMENT_SHADER);
      gl.shaderSource(fs, fragmentSrc);
      gl.compileShader(fs);

      const program = gl.createProgram();
      gl.attachShader(program, vs);
      gl.attachShader(program, fs);
      gl.linkProgram(program);
      return program;
    }

    resize() {
      this.width = this.canvas.width = window.innerWidth;
      this.height = this.canvas.height = window.innerHeight;
      this.gl.viewport(0, 0, this.width, this.height);
    }

    bindEvents() {
      window.addEventListener("resize", () => this.resize());

      window.addEventListener("mousemove", (e) => {
        this.mouse.targetX = e.clientX / window.innerWidth;
        this.mouse.targetY = 1.0 - (e.clientY / window.innerHeight);
      });

      window.addEventListener("scroll", () => {
        const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
        this.scrollProgress = maxScroll > 0 ? window.scrollY / maxScroll : 0;
      }, { passive: true });
    }

    render() {
      const gl = this.gl;
      const now = performance.now();
      const timeInSeconds = (now - this.startTime) * 0.001;

      // Smooth mouse interpolation
      this.mouse.x += (this.mouse.targetX - this.mouse.x) * 0.08;
      this.mouse.y += (this.mouse.targetY - this.mouse.y) * 0.08;

      gl.useProgram(this.program);

      // Pass exact uniforms matching SceneProps logic
      gl.uniform2f(this.uniforms.uResolution, this.width, this.height);
      gl.uniform1f(this.uniforms.uTime, timeInSeconds);
      gl.uniform2f(this.uniforms.uCenter, this.mouse.x, this.mouse.y);

      // Scroll-derived dissolve and grayscale transition
      const dissolve = Math.min(1.0, this.scrollProgress * 1.6);
      const grayscale = Math.min(1.0, this.scrollProgress / 0.4);
      const edgeIntensity = this.scrollProgress * 0.6 + 0.3;
      const edgeBrightness = Math.max(0.2, 1.0 - this.scrollProgress * 0.5);

      gl.uniform1f(this.uniforms.uDissolve, dissolve);
      gl.uniform1f(this.uniforms.uGrayscale, grayscale);
      gl.uniform1f(this.uniforms.uEdgeIntensity, edgeIntensity);
      gl.uniform1f(this.uniforms.uEdgeBrightness, edgeBrightness);

      gl.drawArrays(gl.TRIANGLES, 0, 6);

      requestAnimationFrame(() => this.render());
    }
  }

  // Initialize on Canvas
  document.addEventListener("DOMContentLoaded", () => {
    const canvas = document.getElementById("webgl-canvas");
    if (canvas) {
      new ScrollDissolveShader(canvas);
    }
  });
})();
