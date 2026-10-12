---
name: render
description: script.json 을 three.js 렌더러로 찍어 미리보기 PNG 12장과 장면 클립(MP4)을 만든다. 인자는 채널 + 편, 또는 --all.
---

# /render <채널> <편> — 장면 렌더

1. 선행 조건 (실패하면 멈추고 이유를 말한다):
   - `python -m tools.validate <채널> <편>` 오류 0
   - `python -m tools.factcheck <채널> <편> --check` 통과 (사람이 '초안만'이라고 하면 건너뛰고 결과에 '초안' 표시)
   - `render/vendor/three.module.js` 있음 (없으면 `make setup`)
2. 미리보기: `node render/capture.mjs <채널> <편> --stills`. `WARN … 안전 영역 침범` 이 나오면 줄을 나눠 다시 찍는다.
3. 미리보기 몇 장(s01, 숫자·비교·키캡 장면, s12)을 Read 로 직접 보고 글자 겹침·잘림·3D 가림을 확인, 사람에게도 보여준다.
4. 클립: `node render/capture.mjs <채널> <편>` (장면당 20초~2분). 여러 편은 `python -m tools.batch <채널…> [--draft] --jobs 3` 을
   백그라운드로 돌린다 (검사 → 미리보기 → 클립 → 조립까지 한 번에).
5. 렌더러 디자인 변경은 제안만 한다 (한 번에 한 가지만, 모든 채널에 영향).
