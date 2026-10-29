import express from 'express';
import { chromium } from 'playwright';
import archiver from 'archiver';
import fs from 'node:fs/promises';
import { createWriteStream } from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const app = express();
const PORT = Number(process.env.PORT || 4173);
const HOST = process.env.HOST || '127.0.0.1';
const PUBLIC_DIR = path.join(__dirname, 'public');
const RUNS_DIR = path.join(__dirname, 'data', 'runs');
const ZIPS_DIR = path.join(__dirname, 'data', 'zips');
const jobs = new Map();
let activeRuns = 0;
const MAX_ACTIVE_RUNS = 2;

await fs.mkdir(RUNS_DIR, { recursive: true });
await fs.mkdir(ZIPS_DIR, { recursive: true });

app.use(express.json({ limit: '64kb' }));
app.use(express.static(PUBLIC_DIR, { extensions: ['html'] }));

function cleanSlug(value, fallback = 'capture') {
  return String(value || fallback)
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 42) || fallback;
}

function parseUrl(input) {
  let parsed;
  try {
    parsed = new URL(String(input).trim());
  } catch {
    throw new Error(`Invalid URL: ${String(input).slice(0, 100)}`);
  }
  if (!['http:', 'https:'].includes(parsed.protocol)) {
    throw new Error(`Only http:// and https:// URLs are supported: ${parsed.href}`);
  }
  if (parsed.username || parsed.password) {
    throw new Error('URLs containing a username or password are not supported.');
  }
  return parsed.href;
}

function addLog(job, message, level = 'info') {
  const entry = { at: new Date().toISOString(), level, message: String(message).slice(0, 500) };
  job.logs.push(entry);
  if (job.logs.length > 250) job.logs.shift();
}

function publicJob(job) {
  return {
    id: job.id,
    status: job.status,
    progress: job.progress,
    total: job.total,
    currentUrl: job.currentUrl,
    logs: job.logs,
    screenshots: job.screenshots,
    errors: job.errors,
    startedAt: job.startedAt,
    finishedAt: job.finishedAt,
    options: job.options,
    downloadUrl: job.status === 'completed' ? `/api/runs/${job.id}/download` : null
  };
}

function screenshotUrl(jobId, filename) {
  return `/api/artifacts/${encodeURIComponent(jobId)}/${encodeURIComponent(filename)}`;
}

async function waitBriefly(page, ms = 450) {
  try { await page.waitForTimeout(ms); } catch { /* the page may have closed */ }
}

async function dismissCookieDialogs(page, job) {
  const labels = [
    /accept all cookies/i,
    /accept all/i,
    /accept cookies/i,
    /^i agree$/i,
    /^agree and continue$/i,
    /^allow all$/i,
    /^got it$/i
  ];
  for (const label of labels) {
    try {
      const button = page.getByRole('button', { name: label }).first();
      if (await button.isVisible({ timeout: 250 })) {
        await button.click({ timeout: 900 });
        addLog(job, `Dismissed a cookie/consent dialog (${String(label)}).`);
        await waitBriefly(page, 250);
        return;
      }
    } catch { /* move on to the next common label */ }
  }
}

async function saveScreenshot(page, job, runDir, name, meta = {}) {
  const file = `${String(job.screenshots.length + 1).padStart(3, '0')}-${cleanSlug(name)}.png`;
  const filePath = path.join(runDir, file);
  try {
    await page.screenshot({
      path: filePath,
      fullPage: Boolean(meta.fullPage),
      animations: 'disabled',
      caret: 'hide',
      timeout: 25000
    });
    const screenshot = {
      file,
      url: screenshotUrl(job.id, file),
      label: meta.label || name,
      type: meta.type || 'viewport',
      pageUrl: page.url(),
      title: await page.title().catch(() => ''),
      capturedAt: new Date().toISOString(),
      width: job.options.width,
      height: job.options.height
    };
    job.screenshots.push(screenshot);
    job.progress = Math.min(job.total, job.screenshots.length + job.completedActions);
    addLog(job, `Captured ${screenshot.label}`);
    return screenshot;
  } catch (error) {
    const message = `Could not capture "${meta.label || name}": ${error.message}`;
    job.errors.push(message);
    addLog(job, message, 'warn');
    return null;
  }
}

async function clickUserSelectors(page, job, runDir, selectors, pageIndex) {
  let step = 0;
  for (const selector of selectors) {
    step += 1;
    try {
      const locator = page.locator(selector).first();
      await locator.waitFor({ state: 'visible', timeout: 1800 });
      const text = await locator.innerText({ timeout: 1000 }).catch(() => 'custom selector');
      await locator.click({ timeout: 2200 });
      await waitBriefly(page, 500);
      await saveScreenshot(page, job, runDir, `p${pageIndex}-selector-${step}-${text}`, {
        label: `Custom step: ${text.trim().slice(0, 70) || selector}`,
        type: 'interaction'
      });
    } catch (error) {
      addLog(job, `Selector skipped (${selector}): ${error.message}`, 'warn');
      job.completedActions += 1;
    }
  }
}

async function getNextTabCandidate(page, visited, markerNo) {
  return page.evaluate(({ visitedKeys, marker }) => {
    const visited = new Set(visitedKeys);
    const selector = [
      '[role="tab"]',
      '[data-bs-toggle="tab"]',
      '[data-toggle="tab"]',
      'button[aria-controls]',
      'a[href^="#"]',
      'button[class*="tab" i]',
      '[role="button"][class*="tab" i]'
    ].join(',');
    const items = Array.from(document.querySelectorAll(selector));
    const excluded = /\b(log ?out|sign ?out|delete|remove|cancel account|purchase|buy now|pay now|place order|subscribe now|submit|checkout)\b/i;
    const tabLike = /\b(overview|features?|details?|specifications?|reviews?|pricing|plans?|gallery|photos?|highlights?|description|faq|compare|comparison|itinerary|included|map|schedule|amenities|more info|what is included)\b/i;
    const isVisible = (el) => {
      const rect = el.getBoundingClientRect();
      const style = getComputedStyle(el);
      return rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none' && style.opacity !== '0';
    };
    const slug = (s) => String(s || '').toLowerCase().replace(/\s+/g, ' ').trim().slice(0, 100);
    for (const el of items) {
      if (!isVisible(el) || el.disabled || el.getAttribute('aria-disabled') === 'true') continue;
      const text = (el.innerText || el.getAttribute('aria-label') || el.getAttribute('title') || '').replace(/\s+/g, ' ').trim();
      if (!text || text.length > 90 || excluded.test(text)) continue;
      const role = el.getAttribute('role') || '';
      const href = el.getAttribute('href') || '';
      const className = typeof el.className === 'string' ? el.className : '';
      const explicitTab = role === 'tab' || el.hasAttribute('aria-controls') || el.hasAttribute('data-bs-toggle') || el.hasAttribute('data-toggle') || /\btab\b/i.test(className);
      const plausibleLabel = tabLike.test(text);
      const hashLink = el.tagName === 'A' && href.startsWith('#') && href.length > 1;
      if (!(explicitTab || (plausibleLabel && (el.tagName === 'BUTTON' || el.getAttribute('role') === 'button')) || hashLink)) continue;
      const key = [slug(text), slug(el.getAttribute('aria-controls')), slug(href), slug(role)].join('|');
      if (visited.has(key)) continue;
      const targetId = `shotbot-${marker}`;
      el.setAttribute('data-shotbot-target', targetId);
      return { key, label: text, selector: `[data-shotbot-target="${targetId}"]` };
    }
    return null;
  }, { visitedKeys: Array.from(visited), marker: markerNo });
}

async function exploreTabs(page, job, runDir, pageIndex) {
  const visited = new Set();
  const maxTabs = job.options.maxTabs;
  for (let index = 0; index < maxTabs; index += 1) {
    let candidate;
    try {
      candidate = await getNextTabCandidate(page, visited, `${pageIndex}-${index}`);
    } catch (error) {
      addLog(job, `Could not inspect tab controls: ${error.message}`, 'warn');
      break;
    }
    if (!candidate) break;
    visited.add(candidate.key);
    try {
      await page.locator(candidate.selector).first().click({ timeout: 2200 });
      await waitBriefly(page, 600);
      await saveScreenshot(page, job, runDir, `p${pageIndex}-tab-${candidate.label}`, {
        label: `Tab: ${candidate.label}`,
        type: 'tab'
      });
    } catch (error) {
      addLog(job, `Tab skipped (${candidate.label}): ${error.message}`, 'warn');
      job.completedActions += 1;
    }
  }
}

async function scrollCapture(page, job, runDir, pageIndex) {
  const steps = job.options.scrollSteps;
  if (!steps) return;
  const dimensions = await page.evaluate(() => ({
    scrollHeight: Math.max(document.body?.scrollHeight || 0, document.documentElement.scrollHeight),
    viewportHeight: window.innerHeight
  })).catch(() => ({ scrollHeight: 0, viewportHeight: job.options.height }));
  const maxScroll = Math.max(0, dimensions.scrollHeight - dimensions.viewportHeight);
  if (maxScroll < 120) {
    addLog(job, 'Page is too short for meaningful scroll captures.');
    return;
  }
  for (let step = 1; step <= steps; step += 1) {
    const y = Math.round(maxScroll * (step / steps));
    await page.evaluate((scrollY) => window.scrollTo(0, scrollY), y).catch(() => {});
    await waitBriefly(page, 450);
    await saveScreenshot(page, job, runDir, `p${pageIndex}-scroll-${step}`, {
      label: `Scroll ${step}/${steps} · ${Math.round((step / steps) * 100)}% down`,
      type: 'scroll'
    });
  }
  await page.evaluate(() => window.scrollTo(0, 0)).catch(() => {});
  await waitBriefly(page, 250);
}

async function createZip(job, runDir) {
  const zipPath = path.join(ZIPS_DIR, `${job.id}.zip`);
  await new Promise((resolve, reject) => {
    const output = createWriteStream(zipPath);
    const archive = archiver('zip', { zlib: { level: 6 } });
    output.on('close', resolve);
    output.on('error', reject);
    archive.on('error', reject);
    archive.pipe(output);
    archive.directory(runDir, false);
    archive.finalize();
  });
  return zipPath;
}

async function runCapture(job) {
  activeRuns += 1;
  job.status = 'running';
  job.startedAt = new Date().toISOString();
  addLog(job, 'Starting Chromium browser session.');
  const runDir = path.join(RUNS_DIR, job.id);
  await fs.mkdir(runDir, { recursive: true });
  let browser;
  try {
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
      viewport: { width: job.options.width, height: job.options.height },
      deviceScaleFactor: job.options.deviceScaleFactor,
      locale: 'en-CA',
      colorScheme: job.options.colorScheme,
      reducedMotion: 'reduce',
      ignoreHTTPSErrors: false
    });
    context.setDefaultNavigationTimeout(30000);
    context.setDefaultTimeout(5000);

    for (let idx = 0; idx < job.options.urls.length; idx += 1) {
      const url = job.options.urls[idx];
      const pageIndex = idx + 1;
      job.currentUrl = url;
      addLog(job, `Opening page ${pageIndex}/${job.options.urls.length}: ${url}`);
      const page = await context.newPage();
      page.on('pageerror', (error) => addLog(job, `Page script error: ${error.message}`, 'warn'));
      page.on('console', (message) => {
        if (message.type() === 'error') addLog(job, `Console error: ${message.text().slice(0, 220)}`, 'warn');
      });
      try {
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
        await waitBriefly(page, 1400);
        if (job.options.dismissCookies) await dismissCookieDialogs(page, job);
        await saveScreenshot(page, job, runDir, `p${pageIndex}-initial`, {
          label: `Page ${pageIndex} · initial view`,
          type: 'initial'
        });

        if (job.options.includeFullPage) {
          const size = await page.evaluate(() => ({
            width: Math.max(document.body?.scrollWidth || 0, document.documentElement.scrollWidth),
            height: Math.max(document.body?.scrollHeight || 0, document.documentElement.scrollHeight)
          })).catch(() => ({ width: 0, height: 0 }));
          if (size.height <= 16000 && size.width <= 4000) {
            await page.evaluate(() => window.scrollTo(0, 0)).catch(() => {});
            await saveScreenshot(page, job, runDir, `p${pageIndex}-full-page`, {
              label: `Page ${pageIndex} · full page`,
              type: 'full-page',
              fullPage: true
            });
          } else {
            addLog(job, `Skipped full-page capture because the document is very large (${size.width}×${size.height}).`, 'warn');
          }
        }

        await scrollCapture(page, job, runDir, pageIndex);
        if (job.options.customSelectors.length) {
          await clickUserSelectors(page, job, runDir, job.options.customSelectors, pageIndex);
        }
        if (job.options.exploreTabs) {
          await exploreTabs(page, job, runDir, pageIndex);
        }
      } catch (error) {
        const message = `Page failed (${url}): ${error.message}`;
        job.errors.push(message);
        addLog(job, message, 'error');
      } finally {
        await page.close().catch(() => {});
      }
    }

    const manifest = {
      app: 'Pageframe Screenshot Bot',
      runId: job.id,
      createdAt: job.startedAt,
      finishedAt: new Date().toISOString(),
      options: job.options,
      screenshots: job.screenshots,
      errors: job.errors,
      logs: job.logs
    };
    await fs.writeFile(path.join(runDir, 'manifest.json'), JSON.stringify(manifest, null, 2), 'utf8');
    await createZip(job, runDir);
    job.status = 'completed';
    job.progress = Math.max(job.progress, job.screenshots.length);
    job.finishedAt = new Date().toISOString();
    addLog(job, `Capture finished: ${job.screenshots.length} screenshots saved.`);
    // Refresh the manifest so its log includes the final status lines.
    manifest.finishedAt = job.finishedAt;
    manifest.logs = job.logs;
    await fs.writeFile(path.join(runDir, 'manifest.json'), JSON.stringify(manifest, null, 2), 'utf8');
    // Rebuild so the final manifest included in the archive is current.
    await createZip(job, runDir);
  } catch (error) {
    job.status = 'failed';
    job.errors.push(error.message);
    addLog(job, `Capture failed: ${error.message}`, 'error');
  } finally {
    if (browser) await browser.close().catch(() => {});
    job.currentUrl = null;
    job.finishedAt ||= new Date().toISOString();
    activeRuns = Math.max(0, activeRuns - 1);
  }
}

app.get('/api/health', (_req, res) => {
  res.json({ ok: true, engine: 'Playwright / Chromium', activeRuns, maxActiveRuns: MAX_ACTIVE_RUNS });
});

app.post('/api/runs', (req, res) => {
  const inFlight = [...jobs.values()].filter((job) => job.status === 'queued' || job.status === 'running').length;
  if (inFlight >= MAX_ACTIVE_RUNS || activeRuns >= MAX_ACTIVE_RUNS) {
    return res.status(429).json({ error: 'The browser is busy with two capture jobs. Try again shortly.' });
  }
  try {
    const rawUrls = Array.isArray(req.body.urls) ? req.body.urls : String(req.body.urls || '').split(/\r?\n/);
    const urls = [...new Set(rawUrls.map((value) => parseUrl(value)).filter(Boolean))];
    if (!urls.length) return res.status(400).json({ error: 'Enter at least one http:// or https:// page URL.' });
    if (urls.length > 8) return res.status(400).json({ error: 'A single run can capture up to 8 URLs.' });

    const customSelectors = String(req.body.customSelectors || '')
      .split(/\r?\n/).map((line) => line.trim()).filter(Boolean).slice(0, 8);
    if (customSelectors.some((selector) => selector.length > 250)) {
      return res.status(400).json({ error: 'Each CSS selector must be 250 characters or fewer.' });
    }
    const width = Math.min(1920, Math.max(800, Number(req.body.width) || 1440));
    const height = Math.min(1200, Math.max(600, Number(req.body.height) || 1000));
    const scrollSteps = Math.min(5, Math.max(0, Number(req.body.scrollSteps) || 0));
    const maxTabs = Math.min(8, Math.max(0, Number(req.body.maxTabs ?? 5) || 0));
    const options = {
      urls,
      width,
      height,
      deviceScaleFactor: 1,
      colorScheme: req.body.colorScheme === 'dark' ? 'dark' : 'light',
      includeFullPage: req.body.includeFullPage !== false,
      scrollSteps,
      exploreTabs: req.body.exploreTabs !== false,
      maxTabs,
      dismissCookies: req.body.dismissCookies !== false,
      customSelectors
    };
    const id = `${Date.now().toString(36)}-${crypto.randomBytes(4).toString('hex')}`;
    const job = {
      id,
      status: 'queued',
      options,
      progress: 0,
      total: urls.length * (1 + (options.includeFullPage ? 1 : 0) + scrollSteps + maxTabs + customSelectors.length),
      completedActions: 0,
      currentUrl: null,
      logs: [],
      screenshots: [],
      errors: [],
      startedAt: null,
      finishedAt: null
    };
    jobs.set(id, job);
    addLog(job, `Queued ${urls.length} page${urls.length === 1 ? '' : 's'}.`);
    // Start asynchronously after returning the job identifier to the UI.
    setImmediate(() => { void runCapture(job); });
    return res.status(202).json(publicJob(job));
  } catch (error) {
    return res.status(400).json({ error: error.message });
  }
});

app.get('/api/runs/:id', (req, res) => {
  const job = jobs.get(req.params.id);
  if (!job) return res.status(404).json({ error: 'Capture run not found. Runs are stored in memory until the server restarts.' });
  return res.json(publicJob(job));
});

app.get('/api/runs/:id/download', async (req, res) => {
  const job = jobs.get(req.params.id);
  if (!job || job.status !== 'completed') return res.status(404).json({ error: 'The ZIP is not ready for this run.' });
  const zipPath = path.join(ZIPS_DIR, `${job.id}.zip`);
  try {
    await fs.access(zipPath);
    return res.download(zipPath, `pageframe-${job.id}.zip`);
  } catch {
    return res.status(404).json({ error: 'ZIP file not found.' });
  }
});

app.get('/api/artifacts/:id/:filename', async (req, res) => {
  const { id, filename } = req.params;
  if (!/^[a-z0-9-]+$/i.test(id) || path.basename(filename) !== filename || !filename.endsWith('.png')) {
    return res.status(400).end('Invalid artifact path.');
  }
  const artifactPath = path.join(RUNS_DIR, id, filename);
  try {
    await fs.access(artifactPath);
    res.setHeader('Cache-Control', 'no-store');
    return res.sendFile(artifactPath);
  } catch {
    return res.status(404).end('Screenshot not found.');
  }
});

app.listen(PORT, HOST, () => {
  console.log(`Pageframe Screenshot Bot running at http://${HOST}:${PORT}`);
  console.log('For local use only by default. Do not expose this URL-runner publicly without authentication and network restrictions.');
});
