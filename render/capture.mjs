// 장면 렌더러: script.json 한 편을 받아 미리보기 PNG 또는 장면별 MP4를 만든다.
//
// 사용법 (저장소 최상위 폴더에서):
//   node render/capture.mjs money ep01 --stills   → channels/money/episodes/ep01/preview/s01.png … s12.png
//   node render/capture.mjs money ep01            → channels/money/episodes/ep01/clips/s01.mp4 … (30fps)
//   node render/capture.mjs money ep01 --only 3   → 3번 장면만
//
// 서버를 따로 띄울 필요 없이, 이 스크립트가 프로젝트 폴더를 임시 웹서버로 연다.
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const FPS = 30;

const args = process.argv.slice(2);
const [ch, ep] = args.filter(a => !a.startsWith('--') && !/^\d+$/.test(a));
const stills = args.includes('--stills');
const onlyIdx = args.indexOf('--only');
const only = onlyIdx >= 0 ? Number(args[onlyIdx + 1]) : null;
if (!ch || !ep) {
  console.error('사용법: node render/capture.mjs <채널> <ep01> [--stills] [--only N]');
  process.exit(2);
}
const epDir = path.join(ROOT, 'channels', ch, 'episodes', ep);
const rel = `channels/${ch}/episodes/${ep}`;
if (!fs.existsSync(path.join(epDir, 'script.json'))) {
  console.error(`${rel}/script.json 이 없습니다.`);
  process.exit(2);
}
if (!fs.existsSync(path.join(ROOT, 'render', 'vendor', 'three.module.js'))) {
  console.error('render/vendor 가 비어 있습니다. 먼저 `npm run setup` 을 실행하세요.');
  process.exit(2);
}

// ---------- 정적 파일 서버 (프로젝트 폴더 전체) ----------
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.mjs': 'text/javascript',
  '.json': 'application/json; charset=utf-8', '.css': 'text/css', '.otf': 'font/otf', '.woff2': 'font/woff2',
  '.woff': 'font/woff', '.png': 'image/png' };
const server = http.createServer((req, res) => {
  const p = path.normalize(path.join(ROOT, decodeURIComponent(new URL(req.url, 'http://x').pathname)));
  if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const port = server.address().port;

// ---------- 브라우저 ----------
const launch = { args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] };
if (process.env.CHROMIUM_PATH) launch.executablePath = process.env.CHROMIUM_PATH;
const browser = await chromium.launch(launch);
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
page.on('console', m => { if (m.type() === 'error') console.error('[page]', m.text()); });
page.on('pageerror', e => console.error('[pageerror]', e.message));
await page.goto(`http://127.0.0.1:${port}/render/${process.env.RENDER_PAGE || 'render.html'}?ch=${ch}&ep=${ep}`);
await page.waitForFunction('window.ready === true', null, { timeout: 60000 });
const scenes = await page.evaluate(() => window.SCENES);
// CDP 직접 호출이 page.screenshot 보다 빠르다 (프레임당 약 1/3 절약)
const cdp = await page.context().newCDPSession(page);

const name = i => `s${String(i + 1).padStart(2, '0')}`;
const targets = scenes.map((s, i) => ({ ...s, i })).filter(s => only === null || s.i + 1 === only);

try {
  if (stills) {
    const out = path.join(epDir, 'preview');
    fs.mkdirSync(out, { recursive: true });
    let overflow = 0;
    for (const s of targets) {
      await page.evaluate(t => window.seek(t), s.t0 + Math.min(s.dur - 0.05, 1.4));
      await page.screenshot({ path: path.join(out, `${name(s.i)}.png`) });
      // 안전 영역(오른쪽 150px = 좋아요 버튼 자리)을 넘는 글자 찾기
      const over = await page.evaluate(() => [...document.querySelectorAll('#stage .line, #stage .cmp-title, #stage .big, #stage .item, #stage .keys')]
        .filter(el => { const r = document.createRange(); r.selectNodeContents(el); return r.getBoundingClientRect().right > 1080 - 150 + 2; })
        .map(el => el.textContent.trim()));
      for (const t of over) { console.warn(`  WARN ${name(s.i)}: 오른쪽 안전 영역 침범 → "${t}"`); overflow++; }
    }
    console.log(`미리보기 ${targets.length}장 → ${rel}/preview/` + (overflow ? ` (넘침 ${overflow}건)` : ''));
  } else {
    const out = path.join(epDir, 'clips');
    fs.mkdirSync(out, { recursive: true });
    for (const s of targets) {
      const frames = Math.round(s.dur * FPS);
      const file = path.join(out, `${name(s.i)}.mp4`);
      const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', String(FPS), file]);
      const done = new Promise((resolve, reject) => {
        ff.on('error', reject);
        ff.on('close', code => code === 0 ? resolve() : reject(new Error(`ffmpeg 종료 코드 ${code}`)));
      });
      for (let f = 0; f < frames; f++) {
        await page.evaluate(t => window.seek(t), s.t0 + f / FPS);
        const { data } = await cdp.send('Page.captureScreenshot', { format: 'jpeg', quality: 94, optimizeForSpeed: true });
        const buf = Buffer.from(data, 'base64');
        if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      }
      ff.stdin.end();
      await done;
      console.log('clip', path.relative(ROOT, file));
    }
  }
} finally {
  await browser.close();
  server.close();
}
