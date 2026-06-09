/* ==========================================
   TRAFFICAI — SCRIPT.JS
   ========================================== */

// ---- CURSOR PERSONALIZADO ---- //
const cursor = document.getElementById('cursor');
const cursorTrail = document.getElementById('cursorTrail');
let mouseX = 0, mouseY = 0;

document.addEventListener('mousemove', (e) => {
  mouseX = e.clientX;
  mouseY = e.clientY;
  cursor.style.left = mouseX + 'px';
  cursor.style.top = mouseY + 'px';
  cursorTrail.style.left = mouseX + 'px';
  cursorTrail.style.top = mouseY + 'px';
});

document.addEventListener('mousedown', () => cursor.style.transform = 'translate(-50%,-50%) scale(0.7)');
document.addEventListener('mouseup', () => cursor.style.transform = 'translate(-50%,-50%) scale(1)');

// Cursor hover em elementos interativos
document.querySelectorAll('a, button, .step-card, .sev-card, .upload-area').forEach(el => {
  el.addEventListener('mouseenter', () => {
    cursor.style.transform = 'translate(-50%,-50%) scale(1.6)';
    cursorTrail.style.transform = 'translate(-50%,-50%) scale(1.4)';
  });
  el.addEventListener('mouseleave', () => {
    cursor.style.transform = 'translate(-50%,-50%) scale(1)';
    cursorTrail.style.transform = 'translate(-50%,-50%) scale(1)';
  });
});

// ---- NAVBAR SCROLL ---- //
const navbar = document.getElementById('navbar');

window.addEventListener('scroll', () => {
  if (window.scrollY > 50) {
    navbar.classList.add('scrolled');
  } else {
    navbar.classList.remove('scrolled');
  }
});

// ---- HAMBURGER / MOBILE MENU ---- //
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobileMenu');

hamburger.addEventListener('click', () => {
  hamburger.classList.toggle('active');
  mobileMenu.classList.toggle('open');
  document.body.style.overflow = mobileMenu.classList.contains('open') ? 'hidden' : '';
});

function closeMobileMenu() {
  hamburger.classList.remove('active');
  mobileMenu.classList.remove('open');
  document.body.style.overflow = '';
}

// ---- CONTADOR ANIMADO ---- //
function animateCounter(el, target, duration = 1800) {
  let start = 0;
  const step = target / (duration / 16);
  const timer = setInterval(() => {
    start += step;
    if (start >= target) {
      start = target;
      clearInterval(timer);
    }
    el.textContent = Math.floor(start).toLocaleString('pt-BR');
  }, 16);
}

// ---- INTERSECTION OBSERVER — Animações de entrada ---- //
const observerOptions = {
  threshold: 0.15,
  rootMargin: '0px 0px -40px 0px'
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');

      // Contadores hero
      if (entry.target.classList.contains('hero')) {
        entry.target.querySelectorAll('.stat-number').forEach(el => {
          const target = parseInt(el.dataset.target);
          animateCounter(el, target, 1200);
        });
      }

      // Contadores de estatísticas
      if (entry.target.classList.contains('estatisticas')) {
        entry.target.querySelectorAll('.big-number').forEach(el => {
          const target = parseInt(el.dataset.target);
          if (target) animateCounter(el, target, 2000);
        });
        // Barras
        setTimeout(() => {
          entry.target.querySelectorAll('.bar-fill').forEach(bar => {
            bar.style.width = bar.dataset.width + '%';
          });
        }, 300);
      }

      observer.unobserve(entry.target);
    }
  });
}, observerOptions);

// Observar seções
document.querySelectorAll('.hero, .sobre, .como-funciona, .severidade, .estatisticas, .demo, .contato').forEach(section => {
  observer.observe(section);
});

// Observer para step-cards e sev-cards (stagger)
const cardObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const cards = entry.target.querySelectorAll('.step-card, .sev-card, .big-stat');
      cards.forEach((card, i) => {
        setTimeout(() => {
          card.style.opacity = '1';
          card.style.transform = 'translateY(0)';
        }, i * 120);
      });
      cardObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });

// Inicializar cards como invisíveis para animar
document.querySelectorAll('.step-card, .sev-card, .big-stat').forEach(card => {
  card.style.opacity = '0';
  card.style.transform = 'translateY(24px)';
  card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
});

document.querySelectorAll('.steps-container, .severity-cards, .stats-grid').forEach(container => {
  cardObserver.observe(container);
});

// ---- DRAG & DROP UPLOAD ---- //
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');

uploadArea.addEventListener('dragover', (e) => {
  e.preventDefault();
  uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
  uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
  e.preventDefault();
  uploadArea.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith('image/')) {
    handleFileUpload(file);
  } else {
    showToast('⚠️ Por favor, envie apenas arquivos de imagem.');
  }
});

fileInput.addEventListener('change', (e) => {
  if (e.target.files[0]) {
    handleFileUpload(e.target.files[0]);
  }
});

document.getElementById('analyzeBtn').addEventListener('click', runDemo);
document.getElementById('descInput').addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
    e.preventDefault();
    runDemo();
  }
});

let uploadedFile = null;

function handleFileUpload(file) {
  uploadedFile = file;

  const uploadIcon = uploadArea.querySelector('.upload-icon svg');
  const uploadTitle = uploadArea.querySelector('.upload-title');
  const uploadSub = uploadArea.querySelector('.upload-sub');

  uploadTitle.textContent = `✓ Arquivo carregado: ${file.name}`;
  uploadSub.textContent = `${(file.size / 1024).toFixed(1)} KB — Pronto para análise`;
  uploadArea.style.borderColor = 'var(--success)';
  uploadArea.style.background = 'rgba(63,185,80,0.04)';
  if (uploadIcon) uploadIcon.style.color = 'var(--success)';

  showToast(`📷 Imagem "${file.name}" carregada com sucesso!`);
}

// ---- DEMO IA (API Flask) ---- //
const API_BASE = window.location.protocol === 'file:'
  ? 'http://127.0.0.1:5000'
  : window.location.origin;
const SEVERITY_COLORS = {
  LEVE: 'var(--success)',
  MODERADO: 'var(--warning)',
  CRÍTICO: 'var(--danger)',
};

function severityColor(label) {
  return SEVERITY_COLORS[label] || 'var(--accent)';
}

function collectFormFields() {
  const fields = {};
  const idade = document.getElementById('fieldIdade').value.trim();
  const sexo = document.getElementById('fieldSexo').value;
  const especie = document.getElementById('fieldEspecie').value;
  const cinto = document.getElementById('fieldCinto').value;
  const condutor = document.getElementById('fieldCondutor').value;
  const pedestre = document.getElementById('fieldPedestre').value;
  const passageiro = document.getElementById('fieldPassageiro').value;
  const turno = document.getElementById('fieldTurno').value;

  if (idade) fields.idade = parseInt(idade, 10);
  if (sexo) fields.sexo = sexo;
  if (especie) fields.especie_veiculo = especie;
  if (cinto) fields.cinto_seguranca = cinto;
  if (condutor) fields.condutor = condutor;
  if (pedestre) fields.pedestre = pedestre;
  if (passageiro) fields.passageiro = passageiro;
  if (turno) fields.turno = turno;

  return fields;
}

function updateApiStatus(online, info = {}) {
  const statusEl = document.getElementById('apiStatus');
  if (!statusEl) return;

  const dot = statusEl.querySelector('.api-status-dot');
  const text = statusEl.querySelector('.api-status-text');

  if (online) {
    statusEl.classList.add('online');
    statusEl.classList.remove('offline');
    const mode = info.model_loaded ? 'Modelo .pkcls ativo' : 'Heurística (sem modelo)';
    text.textContent = `API conectada — ${mode}`;
  } else {
    statusEl.classList.add('offline');
    statusEl.classList.remove('online');
    text.textContent = 'API offline — execute: python api/app.py';
  }
}

function renderAnalysisResult(data) {
  const demoResult = document.getElementById('demoResult');
  const color = severityColor(data.severity);

  const now = new Date();
  document.getElementById('resultTime').textContent =
    `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;

  const severityEl = document.getElementById('resultSeverity');
  severityEl.textContent = data.severity;
  severityEl.style.color = color;

  document.getElementById('confPct').textContent = `${data.confidence}%`;
  document.getElementById('confPct').style.color = color;

  const confBar = document.getElementById('confBar');
  confBar.style.background = color;
  confBar.style.width = '0%';

  document.getElementById('suggestedResource').textContent = data.resource;
  document.getElementById('analysisTime').textContent = data.analysis_time;

  const sourceEl = document.getElementById('analysisSource');
  if (sourceEl) {
    sourceEl.textContent = data.source === 'model' ? 'Modelo Orange (.pkcls)' : 'Heurística textual';
  }

  demoResult.style.display = 'block';

  setTimeout(() => {
    confBar.style.width = `${data.confidence}%`;
  }, 100);
}

async function runDemo() {
  const desc = document.getElementById('descInput').value.trim();
  const hasImage = Boolean(uploadedFile || fileInput.files[0]);
  const analyzeBtn = document.getElementById('analyzeBtn');
  const demoResult = document.getElementById('demoResult');

  if (!desc && !hasImage && Object.keys(collectFormFields()).length === 0) {
    showToast('⚠️ Insira uma descrição, preencha os dados contextuais ou faça upload de uma imagem.');
    return;
  }

  analyzeBtn.classList.add('loading');
  analyzeBtn.querySelector('span').textContent = 'Analisando';
  demoResult.style.display = 'none';

  try {
    const response = await fetch(`${API_BASE}/api/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        description: desc,
        image: hasImage,
        fields: collectFormFields(),
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Não foi possível concluir a análise.');
    }

    renderAnalysisResult(data);
    showToast(`✅ Análise concluída — Severidade: ${data.severity}`);
  } catch (err) {
    showToast(`⚠️ ${err.message || 'Erro ao contactar a API. Inicie o servidor Flask.'}`);
  } finally {
    analyzeBtn.classList.remove('loading');
    analyzeBtn.querySelector('span').textContent = 'Analisar com IA';
  }
}

// ---- CONTATO ---- //
function submitContact() {
  const inputs = document.querySelectorAll('.contato-form input, .contato-form textarea');
  let valid = true;
  inputs.forEach(input => {
    if (!input.value.trim()) {
      valid = false;
      input.style.borderColor = 'var(--danger)';
      setTimeout(() => { input.style.borderColor = ''; }, 2000);
    }
  });

  if (!valid) {
    showToast('⚠️ Por favor, preencha todos os campos.');
    return;
  }

  const btn = document.querySelector('.contato-form .btn-primary');
  btn.classList.add('loading');
  btn.querySelector('span').textContent = 'Enviando';

  setTimeout(() => {
    btn.classList.remove('loading');
    btn.querySelector('span').textContent = 'Enviar Mensagem';
    inputs.forEach(input => { input.value = ''; });
    showToast('✅ Mensagem enviada com sucesso! Em breve entraremos em contato.');
  }, 1800);
}

// ---- TOAST ---- //
let toastTimeout;
function showToast(msg) {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.classList.add('show');
  clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => {
    toast.classList.remove('show');
  }, 3500);
}

// ---- SMOOTH SCROLL para links internos ---- //
document.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener('click', (e) => {
    const target = document.querySelector(link.getAttribute('href'));
    if (target) {
      e.preventDefault();
      const offset = 80;
      const top = target.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({ top, behavior: 'smooth' });
    }
  });
});

// ---- PARALLAX SUTIL no Hero ---- //
window.addEventListener('scroll', () => {
  const scrollY = window.scrollY;
  const heroContent = document.querySelector('.hero-content');
  const heroVisual = document.querySelector('.hero-visual');

  if (heroContent && scrollY < window.innerHeight) {
    heroContent.style.transform = `translateY(${scrollY * 0.08}px)`;
    if (heroVisual) heroVisual.style.transform = `translateY(${scrollY * 0.04}px)`;
  }
});

// ---- RIPPLE EFFECT nos botões ---- //
document.querySelectorAll('.btn-primary, .btn-secondary, .nav-cta').forEach(btn => {
  btn.addEventListener('click', function(e) {
    const rect = this.getBoundingClientRect();
    const ripple = document.createElement('span');
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;

    ripple.style.cssText = `
      position: absolute;
      width: ${size}px;
      height: ${size}px;
      left: ${x}px;
      top: ${y}px;
      border-radius: 50%;
      background: rgba(255,255,255,0.15);
      transform: scale(0);
      animation: ripple-anim 0.5s ease-out;
      pointer-events: none;
    `;

    this.style.position = 'relative';
    this.style.overflow = 'hidden';
    this.appendChild(ripple);
    setTimeout(() => ripple.remove(), 500);
  });
});

// Keyframe de ripple via JS
const styleEl = document.createElement('style');
styleEl.textContent = `
  @keyframes ripple-anim {
    to { transform: scale(2.5); opacity: 0; }
  }
`;
document.head.appendChild(styleEl);

// ---- ACTIVE SECTION NO SCROLL (navbar highlight) ---- //
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav-links a');

window.addEventListener('scroll', () => {
  let current = '';
  sections.forEach(section => {
    const top = section.offsetTop - 120;
    if (window.scrollY >= top) {
      current = section.getAttribute('id');
    }
  });

  navLinks.forEach(link => {
    link.style.color = '';
    if (link.getAttribute('href') === `#${current}`) {
      link.style.color = 'var(--accent)';
    }
  });
});

// ---- INIT: hero stats counter no load ---- //
window.addEventListener('load', () => {
  setTimeout(() => {
    document.querySelectorAll('.stat-number').forEach(el => {
      const target = parseInt(el.dataset.target);
      if (target) animateCounter(el, target, 1400);
    });
  }, 600);
});

fetch(`${API_BASE}/api/health`)
  .then((res) => res.json())
  .then((info) => {
    updateApiStatus(true, info);
    const mode = info.model_loaded ? 'modelo Orange carregado' : 'heurística (sem modelo)';
    console.log(
      `%c⬡ TrafficAI%c — API ativa • ${mode}`,
      'color: #3b82f6; font-size: 18px; font-weight: bold;',
      'color: #e6edf3; font-size: 18px;'
    );
  })
  .catch(() => {
    updateApiStatus(false);
    console.warn('TrafficAI: API Flask não detectada. Execute: python api/app.py');
  });
