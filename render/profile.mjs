// 채널 프로필 이미지(1080×1080 PNG)를 만든다:  node render/profile.mjs  → assets/profiles/<채널>.png
import { chromium } from 'playwright';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const MIME = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.otf': 'font/otf', '.woff2': 'font/woff2' };
const server = http.createServer((req, res) => {
  const p = path.normalize(path.join(ROOT, decodeURIComponent(new URL(req.url, 'http://x').pathname)));
  if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const out = path.join(ROOT, 'assets', 'profiles');
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
const page = await browser.newPage({ viewport: { width: 1080, height: 1080 } });
for (const ch of fs.readdirSync(path.join(ROOT, 'channels'))) {
  if (!fs.existsSync(path.join(ROOT, 'channels', ch, 'channel.json'))) continue;
  await page.goto(`http://127.0.0.1:${server.address().port}/render/profile.html?ch=${ch}`);
  await page.waitForFunction('window.ready === true');
  await page.screenshot({ path: path.join(out, `${ch}.png`) });
  console.log('profile', `assets/profiles/${ch}.png`);
}
await browser.close(); server.close();
