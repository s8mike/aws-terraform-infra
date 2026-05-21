// ─────────────────────────────────────────────────────────────
// MecandjeoOps Portfolio — Frontend Logic
// Effects: typing animation, scroll fade-in,
//          floating particles, tech-grid background
// ─────────────────────────────────────────────────────────────

const $ = (id) => document.getElementById(id);

// ── Fetch Helper ──────────────────────────────────────────────
async function apiFetch(path) {
  try {
    const res = await fetch(path);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error(`Failed to fetch ${path}:`, err);
    return null;
  }
}

// ─────────────────────────────────────────────────────────────
// EFFECT 1 — TECH GRID + FLOATING PARTICLES
// ─────────────────────────────────────────────────────────────
function initHeroCanvas() {
  const canvas = $('hero-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  function resize() {
    canvas.width  = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  function drawGrid() {
    ctx.strokeStyle = 'rgba(59,130,246,0.07)';
    ctx.lineWidth   = 1;
    const spacing   = 44;
    for (let x = 0; x < canvas.width; x += spacing) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, canvas.height);
      ctx.stroke();
    }
    for (let y = 0; y < canvas.height; y += spacing) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(canvas.width, y);
      ctx.stroke();
    }
    ctx.fillStyle = 'rgba(59,130,246,0.14)';
    for (let x = 0; x < canvas.width; x += spacing) {
      for (let y = 0; y < canvas.height; y += spacing) {
        ctx.beginPath();
        ctx.arc(x, y, 1.5, 0, Math.PI * 2);
        ctx.fill();
      }
    }
  }

  const particles = Array.from({ length: 30 }, () => ({
    x:     Math.random() * 1200,
    y:     Math.random() * 500,
    r:     Math.random() * 2.5 + 1,
    vx:    (Math.random() - 0.5) * 0.35,
    vy:    (Math.random() - 0.5) * 0.35,
    alpha: Math.random() * 0.5 + 0.15,
    color: ['59,130,246', '99,102,241', '139,92,246'][
      Math.floor(Math.random() * 3)
    ],
  }));

  function drawConnections() {
    particles.forEach((a, i) => {
      particles.slice(i + 1).forEach(b => {
        const dist = Math.hypot(a.x - b.x, a.y - b.y);
        if (dist < 130) {
          ctx.strokeStyle =
            `rgba(59,130,246,${0.07 * (1 - dist / 130)})`;
          ctx.lineWidth = 0.8;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.stroke();
        }
      });
    });
  }

  function updateParticles() {
    particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0 || p.x > canvas.width)  p.vx *= -1;
      if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
    });
  }

  function drawParticles() {
    particles.forEach(p => {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${p.color},${p.alpha})`;
      ctx.fill();
    });
  }

  function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawGrid();
    drawConnections();
    updateParticles();
    drawParticles();
    requestAnimationFrame(animate);
  }

  animate();
}

// ─────────────────────────────────────────────────────────────
// EFFECT 2 — TYPING ANIMATION
// ─────────────────────────────────────────────────────────────
function typeText(element, text, speed = 55) {
  return new Promise(resolve => {
    element.textContent = '';
    const cursor = document.createElement('span');
    cursor.className = 'typing-cursor';
    element.parentNode.insertBefore(cursor, element.nextSibling);
    let i = 0;
    const interval = setInterval(() => {
      element.textContent += text[i];
      i++;
      if (i >= text.length) {
        clearInterval(interval);
        setTimeout(() => {
          cursor.style.display = 'none';
          resolve();
        }, 1000);
      }
    }, speed);
  });
}

// ─────────────────────────────────────────────────────────────
// EFFECT 3 — SCROLL FADE-IN
// ─────────────────────────────────────────────────────────────
function initScrollFadeIn() {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12 }
  );

  document.querySelectorAll(
    '.section-header, .skill-category, .project-card, .contact-card'
  ).forEach((el, i) => {
    el.classList.add('fade-in');
    if (i % 4 === 1) el.classList.add('fade-in-delay-1');
    if (i % 4 === 2) el.classList.add('fade-in-delay-2');
    if (i % 4 === 3) el.classList.add('fade-in-delay-3');
    observer.observe(el);
  });
}

// ─────────────────────────────────────────────────────────────
// TOOL ICONS — simpleicons.org CDN
// ─────────────────────────────────────────────────────────────
const TOOL_ICONS = {
  'AWS':               'https://cdn.simpleicons.org/amazonwebservices/ff9900',
  'ECS Fargate':       'https://cdn.simpleicons.org/amazonwebservices/ff9900',
  'VPC / Networking':  'https://cdn.simpleicons.org/amazonwebservices/ff9900',
  'EC2':               'https://cdn.simpleicons.org/amazonwebservices/ff9900',
  'S3':                'https://cdn.simpleicons.org/amazons3/3f8624',
  'IAM':               'https://cdn.simpleicons.org/amazonwebservices/ff9900',
  'CloudWatch':        'https://cdn.simpleicons.org/amazoncloudwatch/ff4f8b',
  'Terraform':         'https://cdn.simpleicons.org/terraform/844FBA',
  'Docker':            'https://cdn.simpleicons.org/docker/2496ED',
  'Kubernetes':        'https://cdn.simpleicons.org/kubernetes/326CE5',
  'GitHub Actions':    'https://cdn.simpleicons.org/githubactions/2088FF',
  'CI/CD Pipelines':   'https://cdn.simpleicons.org/githubactions/2088FF',
  'Python':            'https://cdn.simpleicons.org/python/3776AB',
  'Bash / Shell':      'https://cdn.simpleicons.org/gnubash/4EAA25',
  'YAML':              'https://cdn.simpleicons.org/yaml/CB171E',
  'Git':               'https://cdn.simpleicons.org/git/F03C2E',
  'Linux':             'https://cdn.simpleicons.org/linux/fCC624',
};

function getSkillIcon(name) {
  const url = TOOL_ICONS[name];
  if (url) {
    return `<img src="${url}" alt="${name}"
      onerror="this.style.display='none'" />`;
  }
  return `<svg viewBox="0 0 24 24" fill="none">
    <circle cx="12" cy="12" r="11"
      fill="rgba(59,130,246,0.15)"
      stroke="rgba(59,130,246,0.3)" stroke-width="1"/>
    <text x="12" y="16.5" text-anchor="middle"
      font-size="10" font-weight="700"
      fill="#60a5fa">${name.charAt(0)}</text>
  </svg>`;
}

// ─────────────────────────────────────────────────────────────
// DATA LOADERS
// ─────────────────────────────────────────────────────────────

async function loadProfile() {
  const data = await apiFetch('/api/profile');
  if (!data) return;

  $('nav-name').textContent      = data.name;
  $('nav-available').textContent =
    data.available ? '✅ Available' : 'Not Available';
  $('hero-bio').textContent      = data.bio;
  $('hero-location').textContent = `📍 ${data.location}`;
  $('hero-status').textContent   =
    data.available ? '✅ Open to opportunities' : '🔴 Not available';
  $('hero-github').href          = data.github;
  $('hero-github').textContent   = 'GitHub ↗';
  $('footer-name').textContent   = `${data.name} — ${data.role}`;

  // Typing animation sequence
  await typeText($('hero-name'),    data.name,    55);
  await typeText($('hero-role'),    data.role,    40);
  await typeText($('hero-tagline'), data.tagline, 18);
}

async function loadSkills() {
  const data = await apiFetch('/api/skills');
  if (!data) return;

  const container = $('skills-categories');
  container.innerHTML = '';

  data.categories.forEach(category => {
    const skills  = data.grouped[category];
    const section = document.createElement('div');
    section.className = 'skill-category';
    section.innerHTML = `
      <div class="skill-category-title">${category}</div>
      <div class="skill-items" id="cat-${category}"></div>
    `;
    container.appendChild(section);

    const itemsContainer =
      section.querySelector(`#cat-${category}`);

    skills.forEach(skill => {
      const item = document.createElement('div');
      item.className = 'skill-item';
      item.innerHTML = `
        <div class="skill-header">
          <div class="skill-icon">${getSkillIcon(skill.name)}</div>
          <div class="skill-name">${skill.name}</div>
        </div>
        <div class="skill-bar-wrap">
          <div class="skill-bar" data-level="${skill.level}"></div>
        </div>
        <div class="skill-level">${skill.level}%</div>
      `;
      itemsContainer.appendChild(item);
    });
  });

  setTimeout(() => {
    document.querySelectorAll('.skill-bar').forEach(bar => {
      bar.style.width = `${bar.dataset.level}%`;
    });
  }, 300);
}

async function loadProjects() {
  const data = await apiFetch('/api/projects');
  if (!data) return;

  const grid = $('projects-grid');
  grid.innerHTML = '';

  data.projects.forEach(project => {
    const card = document.createElement('div');
    card.className = `project-card ${
      project.highlight ? 'project-card--highlight' : ''
    }`;

    const badge = project.highlight
      ? '<span class="project-badge">Featured</span>'
      : '';

    const tags = project.tags
      .map(t => `<span class="project-tag">${t}</span>`)
      .join('');

    const githubLink = project.github
      ? `<a href="${project.github}" target="_blank"
           class="project-link">GitHub ↗</a>`
      : '';

    const liveLink = project.live
      ? `<a href="${project.live}" target="_blank"
           class="project-link">Live ↗</a>`
      : '';

    card.innerHTML = `
      ${badge}
      <div class="project-title">${project.title}</div>
      <div class="project-subtitle">${project.subtitle}</div>
      <p class="project-desc">${project.description}</p>
      <div class="project-tags">${tags}</div>
      <div class="project-links">${githubLink}${liveLink}</div>
    `;
    grid.appendChild(card);
  });
}

async function loadContact() {
  const data = await apiFetch('/api/profile');
  if (!data) return;

  const container = $('contact-links');
  container.innerHTML = '';

  const links = [
    {
      icon:  '📧',
      label: data.email,
      href:  `mailto:${data.email}`
    },
    {
      icon:  '💻',
      label: 'GitHub — ' + data.github.replace('https://', ''),
      href:  data.github
    },
    {
      icon:  '🔗',
      label: 'LinkedIn',
      href:  data.linkedin
    },
  ].filter(l => l.href && !l.href.includes('example'));

  links.forEach(link => {
    const a = document.createElement('a');
    a.className = 'contact-link';
    a.href = link.href;
    if (!link.href.startsWith('mailto')) a.target = '_blank';
    a.innerHTML = `
      <span class="contact-link-icon">${link.icon}</span>
      <span>${link.label}</span>
    `;
    container.appendChild(a);
  });
}

// ─────────────────────────────────────────────────────────────
// BOOT
// ─────────────────────────────────────────────────────────────
async function init() {
  initHeroCanvas();
  await Promise.all([
    loadProfile(),
    loadSkills(),
    loadProjects(),
    loadContact(),
  ]);
  initScrollFadeIn();
}

document.addEventListener('DOMContentLoaded', init);










// // ─────────────────────────────────────────────────────────────
// // MecandjeoOps Portfolio — Frontend Logic
// // Effects: typing animation, scroll fade-in, particles, tech-grid
// // ─────────────────────────────────────────────────────────────

// const $ = (id) => document.getElementById(id);

// // ── Fetch Helper ──────────────────────────────────────────────
// async function apiFetch(path) {
//   try {
//     const res = await fetch(path);
//     if (!res.ok) throw new Error(`HTTP ${res.status}`);
//     return await res.json();
//   } catch (err) {
//     console.error(`Failed to fetch ${path}:`, err);
//     return null;
//   }
// }

// // ─────────────────────────────────────────────────────────────
// // EFFECT 1 — TECH GRID + FLOATING PARTICLES
// // Draws an animated grid and floating dots on the hero canvas
// // ─────────────────────────────────────────────────────────────
// function initHeroCanvas() {
//   const canvas = $('hero-canvas');
//   if (!canvas) return;
//   const ctx = canvas.getContext('2d');

//   // Resize canvas to match hero section
//   function resize() {
//     canvas.width  = canvas.offsetWidth;
//     canvas.height = canvas.offsetHeight;
//   }
//   resize();
//   window.addEventListener('resize', resize);

//   // ── Grid ──────────────────────────────────────────────────
//   function drawGrid() {
//     ctx.strokeStyle = 'rgba(37, 99, 235, 0.06)';
//     ctx.lineWidth   = 1;
//     const spacing   = 40;

//     for (let x = 0; x < canvas.width; x += spacing) {
//       ctx.beginPath();
//       ctx.moveTo(x, 0);
//       ctx.lineTo(x, canvas.height);
//       ctx.stroke();
//     }
//     for (let y = 0; y < canvas.height; y += spacing) {
//       ctx.beginPath();
//       ctx.moveTo(0, y);
//       ctx.lineTo(canvas.width, y);
//       ctx.stroke();
//     }

//     // Grid intersection dots
//     ctx.fillStyle = 'rgba(37, 99, 235, 0.12)';
//     for (let x = 0; x < canvas.width; x += spacing) {
//       for (let y = 0; y < canvas.height; y += spacing) {
//         ctx.beginPath();
//         ctx.arc(x, y, 1.5, 0, Math.PI * 2);
//         ctx.fill();
//       }
//     }
//   }

//   // ── Floating Particles ────────────────────────────────────
//   const particles = Array.from({ length: 28 }, () => ({
//     x:      Math.random() * 800,
//     y:      Math.random() * 400,
//     r:      Math.random() * 3 + 1,
//     vx:     (Math.random() - 0.5) * 0.4,
//     vy:     (Math.random() - 0.5) * 0.4,
//     alpha:  Math.random() * 0.5 + 0.1,
//     color:  Math.random() > 0.5 ? '37, 99, 235' : '124, 58, 237',
//   }));

//   // Connection lines between nearby particles
//   function drawConnections() {
//     particles.forEach((a, i) => {
//       particles.slice(i + 1).forEach(b => {
//         const dist = Math.hypot(a.x - b.x, a.y - b.y);
//         if (dist < 120) {
//           ctx.strokeStyle =
//             `rgba(37, 99, 235, ${0.08 * (1 - dist / 120)})`;
//           ctx.lineWidth = 0.8;
//           ctx.beginPath();
//           ctx.moveTo(a.x, a.y);
//           ctx.lineTo(b.x, b.y);
//           ctx.stroke();
//         }
//       });
//     });
//   }

//   function updateParticles() {
//     particles.forEach(p => {
//       p.x += p.vx;
//       p.y += p.vy;
//       if (p.x < 0 || p.x > canvas.width)  p.vx *= -1;
//       if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
//     });
//   }

//   function drawParticles() {
//     particles.forEach(p => {
//       ctx.beginPath();
//       ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
//       ctx.fillStyle = `rgba(${p.color}, ${p.alpha})`;
//       ctx.fill();
//     });
//   }

//   // ── Animation Loop ────────────────────────────────────────
//   function animate() {
//     ctx.clearRect(0, 0, canvas.width, canvas.height);
//     drawGrid();
//     drawConnections();
//     updateParticles();
//     drawParticles();
//     requestAnimationFrame(animate);
//   }

//   animate();
// }

// // ─────────────────────────────────────────────────────────────
// // EFFECT 2 — TYPING ANIMATION
// // Types text character by character with a blinking cursor
// // ─────────────────────────────────────────────────────────────
// function typeText(element, text, speed = 60) {
//   return new Promise(resolve => {
//     element.textContent = '';

//     // Add blinking cursor
//     const cursor = document.createElement('span');
//     cursor.className = 'typing-cursor';
//     element.parentNode.insertBefore(cursor, element.nextSibling);

//     let i = 0;
//     const interval = setInterval(() => {
//       element.textContent += text[i];
//       i++;
//       if (i >= text.length) {
//         clearInterval(interval);
//         // Remove cursor after typing completes
//         setTimeout(() => {
//           cursor.style.display = 'none';
//           resolve();
//         }, 1200);
//       }
//     }, speed);
//   });
// }

// // ─────────────────────────────────────────────────────────────
// // EFFECT 3 — SCROLL FADE-IN
// // Observes elements and fades them in when they enter viewport
// // ─────────────────────────────────────────────────────────────
// function initScrollFadeIn() {
//   const observer = new IntersectionObserver(
//     (entries) => {
//       entries.forEach(entry => {
//         if (entry.isIntersecting) {
//           entry.target.classList.add('visible');
//           observer.unobserve(entry.target);
//         }
//       });
//     },
//     { threshold: 0.15 }
//   );

//   // Add fade-in class to all section content
//   document.querySelectorAll(
//     '.section-header, .skill-category, .project-card, .contact-card'
//   ).forEach((el, i) => {
//     el.classList.add('fade-in');
//     if (i % 4 === 1) el.classList.add('fade-in-delay-1');
//     if (i % 4 === 2) el.classList.add('fade-in-delay-2');
//     if (i % 4 === 3) el.classList.add('fade-in-delay-3');
//     observer.observe(el);
//   });
// }

// // ─────────────────────────────────────────────────────────────
// // DATA LOADERS
// // ─────────────────────────────────────────────────────────────

// // ── Load Profile ──────────────────────────────────────────────
// async function loadProfile() {
//   const data = await apiFetch('/api/profile');
//   if (!data) return;

//   // Navigation
//   $('nav-name').textContent  = data.name;
//   $('nav-available').textContent =
//     data.available ? '✅ Available' : 'Not Available';

//   // Avatar — first letter of name
//   $('hero-avatar').textContent = data.name.charAt(0).toUpperCase();

//   // Static fields
//   $('hero-bio').textContent      = data.bio;
//   $('hero-location').textContent = `📍 ${data.location}`;
//   $('hero-status').textContent   =
//     data.available ? '✅ Open to opportunities' : '🔴 Not available';
//   $('hero-github').href          = data.github;
//   $('hero-github').textContent   = 'GitHub ↗';
//   $('footer-name').textContent   = `${data.name} — ${data.role}`;

//   // Typing animation — name first then role
//   const nameEl    = $('hero-name');
//   const roleEl    = $('hero-role');
//   const taglineEl = $('hero-tagline');

//   nameEl.textContent    = '';
//   roleEl.textContent    = '';
//   taglineEl.textContent = '';

//   await typeText(nameEl, data.name, 55);
//   await typeText(roleEl, data.role, 40);
//   await typeText(taglineEl, data.tagline, 20);
// }

// // ── Load Skills ───────────────────────────────────────────────
// async function loadSkills() {
//   const data = await apiFetch('/api/skills');
//   if (!data) return;

//   const container = $('skills-categories');
//   container.innerHTML = '';

//   data.categories.forEach(category => {
//     const skills  = data.grouped[category];
//     const section = document.createElement('div');
//     section.className = 'skill-category';
//     section.innerHTML = `
//       <div class="skill-category-title">${category}</div>
//       <div class="skill-items" id="cat-${category}"></div>
//     `;
//     container.appendChild(section);

//     const itemsContainer =
//       section.querySelector(`#cat-${category}`);

//     skills.forEach(skill => {
//       const item = document.createElement('div');
//       item.className = 'skill-item';
//       item.innerHTML = `
//         <div class="skill-name">${skill.name}</div>
//         <div class="skill-bar-wrap">
//           <div class="skill-bar" data-level="${skill.level}"></div>
//         </div>
//         <div class="skill-level">${skill.level}%</div>
//       `;
//       itemsContainer.appendChild(item);
//     });
//   });

//   // Animate skill bars after render
//   setTimeout(() => {
//     document.querySelectorAll('.skill-bar').forEach(bar => {
//       bar.style.width = `${bar.dataset.level}%`;
//     });
//   }, 300);
// }

// // ── Load Projects ─────────────────────────────────────────────
// async function loadProjects() {
//   const data = await apiFetch('/api/projects');
//   if (!data) return;

//   const grid = $('projects-grid');
//   grid.innerHTML = '';

//   data.projects.forEach(project => {
//     const card = document.createElement('div');
//     card.className = `project-card ${
//       project.highlight ? 'project-card--highlight' : ''
//     }`;

//     const badge = project.highlight
//       ? '<span class="project-badge">Featured</span>'
//       : '';

//     const tags = project.tags
//       .map(t => `<span class="project-tag">${t}</span>`)
//       .join('');

//     const githubLink = project.github
//       ? `<a href="${project.github}" target="_blank"
//            class="project-link">GitHub ↗</a>`
//       : '';

//     const liveLink = project.live
//       ? `<a href="${project.live}" target="_blank"
//            class="project-link">Live ↗</a>`
//       : '';

//     card.innerHTML = `
//       ${badge}
//       <div class="project-title">${project.title}</div>
//       <div class="project-subtitle">${project.subtitle}</div>
//       <p class="project-desc">${project.description}</p>
//       <div class="project-tags">${tags}</div>
//       <div class="project-links">${githubLink}${liveLink}</div>
//     `;
//     grid.appendChild(card);
//   });
// }

// // ── Load Contact ──────────────────────────────────────────────
// async function loadContact() {
//   const data = await apiFetch('/api/profile');
//   if (!data) return;

//   const container = $('contact-links');
//   container.innerHTML = '';

//   const links = [
//     {
//       icon:  '📧',
//       label: data.email,
//       href:  `mailto:${data.email}`
//     },
//     {
//       icon:  '💻',
//       label: 'GitHub — ' + data.github.replace('https://', ''),
//       href:  data.github
//     },
//     {
//       icon:  '🔗',
//       label: 'LinkedIn',
//       href:  data.linkedin
//     },
//   ].filter(l => l.href && !l.href.includes('example'));

//   links.forEach(link => {
//     const a = document.createElement('a');
//     a.className = 'contact-link';
//     a.href = link.href;
//     if (!link.href.startsWith('mailto')) a.target = '_blank';
//     a.innerHTML = `
//       <span class="contact-link-icon">${link.icon}</span>
//       <span>${link.label}</span>
//     `;
//     container.appendChild(a);
//   });
// }

// // ─────────────────────────────────────────────────────────────
// // BOOT — Initialise everything
// // ─────────────────────────────────────────────────────────────
// async function init() {
//   // Start canvas immediately — does not need API data
//   initHeroCanvas();

//   // Load all data
//   await Promise.all([
//     loadProfile(),
//     loadSkills(),
//     loadProjects(),
//     loadContact(),
//   ]);

//   // Init scroll observer after content is loaded
//   initScrollFadeIn();
// }

// document.addEventListener('DOMContentLoaded', init);