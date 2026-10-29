# Pageframe — Promotional Screenshot Bot

A local web app that opens webpages in a real Chromium browser, takes screenshots as it navigates and scrolls, explores visible tab-like controls, and packages the result into a downloadable ZIP.

## What it does

- Accepts up to 8 page URLs in one run.
- Captures the initial viewport and (optionally) one full-page PNG per URL.
- Scrolls through the page and captures up to 5 additional viewport positions.
- Looks for common UI tabs (for example, elements with `role="tab"`, `aria-controls`, tab data attributes, and likely tab labels) and captures the selected state after clicking them.
- Lets you supply up to 8 custom CSS selectors, one per line, for tabs or buttons the automatic detector misses.
- Can try to dismiss common cookie-consent dialogs.
- Shows a live progress log and gallery in the website UI.
- Exports screenshots plus `manifest.json` as one ZIP file.

## Requirements

- Node.js 20 or newer.
- npm.
- A one-time download of Playwright's Chromium browser.

## Run it locally

1. Extract the ZIP.
2. Open a terminal in the extracted `pageframe-bot` directory.
3. Install Node dependencies:

   ```bash
   npm install
   npx playwright install chromium
   ```

4. Start the website:

   ```bash
   npm start
   ```

5. Open **http://127.0.0.1:4173** in your browser.
6. Paste one or more URLs, set the capture options, then click **Start capture**.
7. Review the screenshots in the gallery and click **Download screenshot ZIP**.

On Linux servers, Playwright may also require OS libraries. See the Playwright browser installation documentation if Chromium reports missing system dependencies.

## Using custom selectors

If a tab is not detected automatically, add its CSS selector to **Optional custom click selectors**, one selector per line. Examples:

```css
#pricing-tab
button[aria-controls="gallery"]
[data-testid="details-tab"]
```

The bot clicks the first visible matching element for each selector and captures the resulting state. Test selectors against your page first; a selector can click any element it matches.

## Practical limits

- The bot does not log in, defeat CAPTCHA, bypass a paywall, or evade a site's access controls. Pages that require an account should be captured only with authorized access and an appropriate workflow.
- Dynamic interfaces differ. The automatic tab detector is heuristic; custom selectors help when the page uses a nonstandard component.
- Full-page captures are skipped when a document is extremely large. Scroll captures can be used instead.
- The app listens on `127.0.0.1` by default so it is local-only. **Do not expose it to the public internet as-is.** The app accepts target URLs and runs a browser; a public deployment should add authentication, request limits, and network/SSRF restrictions before binding to a public interface.
- Runs are held in memory for the duration of the server process; the image files remain in `data/runs/` and ZIPs in `data/zips/`. Restarting the server clears the in-memory run list.

## Stack

Node.js, Express 5, and Playwright. The current dependency versions are listed in `package.json`.
