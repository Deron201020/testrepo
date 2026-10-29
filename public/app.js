const $ = (selector) => document.querySelector(selector);
const form = $('#capture-form');
const startButton = $('#start-button');
const formError = $('#form-error');
const emptyRun = $('#empty-run');
const runDetails = $('#run-details');
const runState = $('#run-state');
const progressTitle = $('#progress-title');
const progressNumber = $('#progress-number');
const progressFill = $('#progress-fill');
const currentUrl = $('#current-url');
const runLog = $('#run-log');
const downloadButton = $('#download-button');
const gallery = $('#gallery');
const screenshotCount = $('#screenshot-count');
const galleryState = $('#gallery-state');
const engineDot = $('#engine-dot');
const engineStatus = $('#engine-status');
const toast = $('#toast');
let activeJobId = null;
let lastLogCount = 0;
let toastTimer = null;

function showToast(message) {
  toast.textContent = message;
  toast.classList.add('visible');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('visible'), 3800);
}

function formatTime(iso) {
  if (!iso) return '';
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function setRunState(status) {
  runState.className = `state-pill ${status}`;
  runState.textContent = status.toUpperCase();
}

function appendLogs(logs = []) {
  const fresh = logs.slice(lastLogCount);
  for (const item of fresh) {
    const line = document.createElement('div');
    line.className = `log-line ${item.level || 'info'}`;
    line.textContent = `${formatTime(item.at)}  ${item.message}`;
    runLog.appendChild(line);
  }
  lastLogCount = logs.length;
  runLog.scrollTop = runLog.scrollHeight;
}

function addScreenshotCard(screenshot) {
  const card = document.createElement('article');
  card.className = 'screenshot-card';
  const imageWrap = document.createElement('div');
  imageWrap.className = 'screenshot-image-wrap';
  const img = document.createElement('img');
  img.className = 'screenshot-image';
  img.src = screenshot.url;
  img.alt = screenshot.label || 'Captured webpage screenshot';
  img.loading = 'lazy';
  img.addEventListener('error', () => {
    img.remove();
    const placeholder = document.createElement('span');
    placeholder.className = 'screenshot-placeholder';
    placeholder.textContent = 'Screenshot preview unavailable';
    imageWrap.appendChild(placeholder);
  }, { once: true });
  const type = document.createElement('span');
  type.className = 'screenshot-type';
  type.textContent = (screenshot.type || 'viewport').replace('-', ' ');
  imageWrap.append(img, type);
  const meta = document.createElement('div');
  meta.className = 'screenshot-meta';
  const title = document.createElement('strong');
  title.textContent = screenshot.label || screenshot.file;
  const page = document.createElement('p');
  page.textContent = screenshot.pageUrl || '';
  page.title = screenshot.pageUrl || '';
  const openLink = document.createElement('a');
  openLink.href = screenshot.url;
  openLink.target = '_blank';
  openLink.rel = 'noreferrer';
  openLink.textContent = 'Open PNG ↗';
  meta.append(title, page, openLink);
  card.append(imageWrap, meta);
  gallery.append(card);
}

function renderScreenshots(screenshots = []) {
  if (!screenshots.length) return;
  if (gallery.querySelector('.gallery-empty')) gallery.innerHTML = '';
  const existing = gallery.querySelectorAll('.screenshot-card').length;
  for (const screenshot of screenshots.slice(existing)) addScreenshotCard(screenshot);
  screenshotCount.textContent = String(screenshots.length);
  galleryState.textContent = `${screenshots.length} screenshot${screenshots.length === 1 ? '' : 's'} captured`;
}

function showCaptureError(message) {
  formError.hidden = false;
  formError.textContent = message;
  showToast(message);
}

async function checkEngine() {
  try {
    const response = await fetch('/api/health');
    if (!response.ok) throw new Error('Unavailable');
    const data = await response.json();
    engineDot.className = 'status-dot ok';
    engineStatus.textContent = `${data.engine} ready`;
  } catch {
    engineDot.className = 'status-dot bad';
    engineStatus.textContent = 'Browser engine offline';
  }
}

async function pollJob(jobId) {
  let keepPolling = true;
  while (keepPolling) {
    let data;
    try {
      const response = await fetch(`/api/runs/${encodeURIComponent(jobId)}`);
      data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Could not read capture status.');
    } catch (error) {
      showToast(error.message);
      break;
    }
    const percent = data.status === 'completed' ? 100 : Math.min(99, Math.round((data.progress / Math.max(1, data.total)) * 100));
    progressNumber.textContent = `${percent}%`;
    progressFill.style.width = `${percent}%`;
    progressTitle.textContent = data.status === 'completed' ? 'Capture complete' : data.status === 'failed' ? 'Capture failed' : data.status === 'queued' ? 'Queued for browser' : 'Exploring page states';
    currentUrl.textContent = data.currentUrl || (data.status === 'completed' ? 'All pages processed' : 'Starting browser…');
    setRunState(data.status);
    appendLogs(data.logs || []);
    renderScreenshots(data.screenshots || []);
    if (data.status === 'completed') {
      downloadButton.href = data.downloadUrl;
      downloadButton.hidden = false;
      startButton.disabled = false;
      startButton.innerHTML = '<span class="button-spark">✳</span> Start another run <span class="button-arrow">↗</span>';
      galleryState.textContent = `${data.screenshots.length} screenshot${data.screenshots.length === 1 ? '' : 's'} ready to review`;
      showToast(`Capture finished: ${data.screenshots.length} screenshots saved.`);
      keepPolling = false;
    } else if (data.status === 'failed') {
      startButton.disabled = false;
      startButton.innerHTML = '<span class="button-spark">✳</span> Try again <span class="button-arrow">↗</span>';
      downloadButton.hidden = true;
      showToast('The capture run failed. Check the run log for details.');
      keepPolling = false;
    } else {
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  formError.hidden = true;
  const urls = $('#urls').value.split(/\r?\n/).map((url) => url.trim()).filter(Boolean);
  if (!urls.length) return showCaptureError('Add at least one webpage URL first.');
  if (urls.length > 8) return showCaptureError('A run can include up to 8 URLs.');
  const payload = {
    urls,
    width: Number($('#width').value),
    height: Number($('#height').value),
    scrollSteps: Number($('#scroll-steps').value),
    maxTabs: Number($('#max-tabs').value),
    includeFullPage: $('#full-page').checked,
    dismissCookies: $('#dismiss-cookies').checked,
    exploreTabs: $('#explore-tabs').checked,
    customSelectors: $('#selectors').value
  };
  startButton.disabled = true;
  startButton.innerHTML = '<span class="button-spark">◌</span> Starting browser…';
  emptyRun.hidden = true;
  runDetails.hidden = false;
  runLog.innerHTML = '';
  lastLogCount = 0;
  gallery.innerHTML = '<div class="gallery-empty"><div class="empty-frame"><span></span><span></span><span></span><b>PNG</b></div><strong>Capturing your pages…</strong><p>New screenshots will appear here as they are saved.</p></div>';
  screenshotCount.textContent = '0';
  galleryState.textContent = 'Capture in progress';
  downloadButton.hidden = true;
  progressFill.style.width = '0%';
  progressNumber.textContent = '0%';
  progressTitle.textContent = 'Preparing browser';
  currentUrl.textContent = 'Waiting for job…';
  setRunState('queued');
  try {
    const response = await fetch('/api/runs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Could not start capture.');
    activeJobId = data.id;
    showToast('Browser session started. Screenshots will appear as they are captured.');
    await pollJob(activeJobId);
  } catch (error) {
    startButton.disabled = false;
    startButton.innerHTML = '<span class="button-spark">✳</span> Start capture <span class="button-arrow">↗</span>';
    setRunState('failed');
    showCaptureError(error.message);
  }
});

for (const link of document.querySelectorAll('.nav-item[href^="#"]')) {
  link.addEventListener('click', (event) => {
    const target = document.querySelector(link.getAttribute('href'));
    if (target) {
      event.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      document.querySelectorAll('.nav-item').forEach((item) => item.classList.remove('active'));
      link.classList.add('active');
    }
  });
}

checkEngine();
