---
name: factcheck
description: 대본 내용을 공식 출처와 대조해 channels/<채널>/episodes/epNN/factcheck.md 에 출처 링크를 채운다. 업로드 전 필수 단계.
---

# /factcheck <채널> <편> — 사실 확인

틀린 정보 하나가 채널 신뢰를 깎는다. 이 단계는 건너뛰지 않는다.

1. `python -m tools.factcheck <채널> <편>` — 확인할 문구를 표로 뽑는다 (적힌 출처·확인 표시는 보존).
   범위는 `channel.json` 의 `factcheck_scope`: `numbers`(숫자가 든 문구) 또는 `every_scene`(장면마다 규칙 전체).
2. 줄마다 공식 출처를 찾는다 (`channel.json` 의 `official_sources` 우선, `research/` 의 '확인된 공식 출처' 참고):
   - money: 국세청·홈택스·법령정보센터 — 귀속연도·시행일 확인, 계산은 직접 다시
   - shortcut: 마이크로소프트 공식 도움말 — 버전(엑셀 2013 이상, 윈도우 10/11)·키보드 배열 확인
   - spelling: 국립국어원 표준국어대사전·온라인가나다 — 예문까지 맞는지 확인
3. 출처 칸에 URL, 확인 칸은 `☐` 그대로. **Claude 는 ✅ 를 찍지 않는다.** 원문과 다르면 `❌ 원문: …` + 대본 수정안.
4. 사람에게 링크 목록을 보여주고 원문을 직접 본 줄만 ✅ 로 바꾸게 한다.
5. 대본을 고쳤으면 표를 다시 만들고, `python -m tools.factcheck <채널> <편> --check` 통과 확인 후 `/render` 안내.
