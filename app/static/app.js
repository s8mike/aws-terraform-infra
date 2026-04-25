// ─────────────────────────────────────────────────────────────
// MecanjeoOps Dashboard — Frontend Logic
// ─────────────────────────────────────────────────────────────

const API_BASE = '';  // same origin — FastAPI serves both

// ─── Utility ──────────────────────────────────────────────────
const $ = (id) => document.getElementById(id);
const fmt = (n) => `${Math.round(n)}%`;
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

// ─── Fetch with Error Handling ────────────────────────────────
async function apiFetch(path) {
  try {
    const res = await fetch(`${API_BASE}${path}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error(`Failed to fetch ${path}:`, err);
    return null;
  }
}

// ─── Health Check ─────────────────────────────────────────────
async function updateHealth() {
  const data = await apiFetch('/health');
  const dot  = $('health-dot');
  if (data && data.status === 'healthy') {
    dot.classList.remove('unhealthy');
    dot.title = `Healthy — ${data.timestamp}`;
  } else {
    dot.classList.add('unhealthy');
    dot.title = 'Unhealthy';
  }
}

// ─── Stats ────────────────────────────────────────────────────
async function updateStats() {
  const data = await apiFetch('/api/stats');
  if (!data) return;
  $('stat-deployments').textContent = data.total_deployments;
  $('stat-success').textContent     = data.successful;
  $('stat-failed').textContent      = data.failed;
  $('stat-rate').textContent        = data.success_rate;
}

// ─── System Metrics ───────────────────────────────────────────
async function updateSystem() {
  const data = await apiFetch('/api/system');
  if (!data) return;

  // CPU bar
  $('cpu-bar').style.width   = `${data.cpu_percent}%`;
  $('cpu-value').textContent = fmt(data.cpu_percent);

  // Memory bar
  $('mem-bar').style.width   = `${data.memory_percent}%`;
  $('mem-value').textContent = fmt(data.memory_percent);

  // Details
  $('uptime').textContent     = data.uptime;
  $('platform').textContent   = data.platform;
  $('python-ver').textContent = data.python_version;
}

// ─── Infrastructure ───────────────────────────────────────────
async function updateInfra() {
  const data = await apiFetch('/api/infrastructure');
  if (!data) return;

  $('env-badge').textContent      = data.environment.toUpperCase();
  $('version-badge').textContent  = `v${data.version}`;
  $('region-badge').textContent   = data.region;

  $('infra-project').textContent  = data.project;
  $('infra-platform').textContent = data.platform;
  $('infra-runtime').textContent  = data.runtime;
  $('infra-iac').textContent      = data.iac_tool;
  $('infra-registry').textContent = data.registry;
  $('infra-port').textContent     = data.container_port;
}

// ─── Services ─────────────────────────────────────────────────
async function updateServices() {
  const data = await apiFetch('/api/services');
  if (!data) return;

  const grid = $('services-grid');
  grid.innerHTML = '';

  const allOk = data.services.every(s => s.status === 'operational');
  const label = $('all-operational');
  label.textContent = allOk ? '✓ All Systems Operational' : '⚠ Degraded';
  label.className   = `all-operational ${allOk ? '' : 'degraded'}`;

  data.services.forEach(svc => {
    const icon = svc.status === 'operational' ? '✓'
               : svc.status === 'degraded'    ? '!'
               : '✕';
    const card = document.createElement('div');
    card.className = `service-card ${svc.status}`;
    card.innerHTML = `
      <div class="service-dot"></div>
      <div class="service-info">
        <div class="service-name">${svc.name}</div>
        <div class="service-desc">${svc.description}</div>
      </div>`;
    grid.appendChild(card);
  });
}

// ─── Deployment Timeline ──────────────────────────────────────
async function updateTimeline() {
  const data = await apiFetch('/api/deployments');
  if (!data) return;

  const timeline = $('timeline');
  timeline.innerHTML = '';

  data.deployments.forEach(dep => {
    const icon = dep.status === 'success' ? '✓' : '✕';
    const ts   = new Date(dep.timestamp).toLocaleString();
    const item = document.createElement('div');
    item.className = 'timeline-item';
    item.innerHTML = `
      <div class="timeline-icon ${dep.status}">${icon}</div>
      <div class="timeline-content">
        <div class="timeline-top">
          <span class="timeline-version">v${dep.version}</span>
          <span class="timeline-status status-${dep.status}">
            ${dep.status}
          </span>
        </div>
        <div class="timeline-msg">${dep.message}</div>
        <div class="timeline-meta">
          <span class="timeline-by">
            Deployed by <span>${dep.deployed_by}</span>
          </span>
          <span class="timeline-ts">
            <span>${ts}</span>
          </span>
        </div>
      </div>`;
    timeline.appendChild(item);
  });
}

// ─── Last Updated ─────────────────────────────────────────────
function updateTimestamp() {
  $('last-updated').textContent =
    `Last updated: ${new Date().toLocaleTimeString()}`;
}

// ─── Full Dashboard Refresh ───────────────────────────────────
async function refreshAll() {
  await Promise.all([
    updateHealth(),
    updateStats(),
    updateSystem(),
    updateInfra(),
    updateServices(),
    updateTimeline(),
  ]);
  updateTimestamp();
}

// ─── Auto Refresh Every 10 Seconds ───────────────────────────
async function startAutoRefresh() {
  await refreshAll();
  setInterval(refreshAll, 10000);
}

// ─── Boot ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', startAutoRefresh);