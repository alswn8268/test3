---
name: render
description: script.json 을 three.js 렌더러로 찍어 미리보기 PNG 12장과 장면 클립(MP4)을 만든다. 인자는 편 번호(ep06).
---

# /render — 장면 렌더

1. 선행 조건 확인 (하나라도 실패하면 멈추고 이유를 말한다):
   - `python -m tools.validate <ep>` 오류 0
   - `python -m tools.factcheck <ep> --check` 통과
   - `render/vendor/three.module.js` 있음 (없으면 `npm install && npm run setup`)
2. 미리보기: `node render/capture.mjs <ep> --stills` → `episodes/<ep>/preview/s01~s12.png`.
   출력에 `WARN … 안전 영역 침범` 이 있으면 해당 줄을 나눠 대본을 고치고 다시 찍는다.
3. 미리보기 PNG 몇 장(후킹 s01, 숫자 장면, CTA s12)을 Read 로 직접 보고 글자 겹침·잘림을 확인한다.
   사람에게도 보여준다 (SendUserFile 이 있으면 사용).
4. 장면 클립: `node render/capture.mjs <ep>` → `episodes/<ep>/clips/s01~s12.mp4` (장면당 약 20~30초 소요,
   여러 편이면 백그라운드 실행). 한 장면만 다시: `--only 3`.
5. 렌더러 디자인을 바꿔야 할 것 같으면 바로 고치지 말고 제안만 한다 (CLAUDE.md: 한 번에 한 가지만 변경).
