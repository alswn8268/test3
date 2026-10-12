// npm install 다음에 한 번 실행: 렌더러가 쓰는 라이브러리·폰트를 render/vendor/ 로 복사한다.
// (vendor/ 는 git에 올리지 않는다 — 언제든 이 스크립트로 다시 만들 수 있음)
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const NM = path.join(ROOT, 'node_modules');
const VENDOR = path.join(ROOT, 'render', 'vendor');

if (!fs.existsSync(path.join(NM, 'three'))) {
  console.error('node_modules 가 없습니다. 먼저 `npm install` 을 실행하세요.');
  process.exit(1);
}
fs.rmSync(VENDOR, { recursive: true, force: true });
fs.mkdirSync(VENDOR, { recursive: true });

// three.js: three.module.js 가 같은 폴더의 three.core.js 를 불러온다
for (const f of ['three.module.js', 'three.core.js']) {
  fs.copyFileSync(path.join(NM, 'three', 'build', f), path.join(VENDOR, f));
}

// 큰 숫자용 Noto Serif KR Black(900): css + 글꼴 조각 파일
const fsrc = path.join(NM, '@fontsource', 'noto-serif-kr');
const fdst = path.join(VENDOR, 'noto-serif-kr');
fs.mkdirSync(path.join(fdst, 'files'), { recursive: true });
fs.copyFileSync(path.join(fsrc, '900.css'), path.join(fdst, '900.css'));
let n = 0;
for (const f of fs.readdirSync(path.join(fsrc, 'files'))) {
  if (f.endsWith('-900-normal.woff2')) { fs.copyFileSync(path.join(fsrc, 'files', f), path.join(fdst, 'files', f)); n++; }
}
console.log(`render/vendor 준비 완료 (three.js 2개, Noto Serif KR 조각 ${n}개)`);
