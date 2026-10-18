---
name: review
description: 업로드 48시간 뒤 인사이트 수치를 channels/<채널>/metrics.csv 에 넣고 통과·미달을 판정해 learnings.md 와 다음 주 대본 규칙에 반영한다.
---

# /review <채널> [편] — 48시간 점검

1. 사람이 준 수치를 `channels/<채널>/metrics.csv` 에 플랫폼마다 한 줄씩 추가 — platform 값은 `tiktok` · `youtube` · `reels` 로 통일
   (빠진 숫자는 추측하지 말고 묻기). 플랫폼마다 3초 유지율·완주율 이름이 달라도 같은 칸에 맞춰 넣는다.
   - `sends`(인스타 DM 보내기 수)·`viewed_vs_swiped`(유튜브 쇼츠 '본 비율' %)는 있으면 적고, 없으면 비워 둔다.
2. `python -m tools.review <채널> [<편>]` 로 판정표.
3. `channels/<채널>/learnings.md` 맨 위에 이번 주 항목: 판정표 · 잘된 편과 안 된 편의 차이 · **미달 지표 하나만** 골라 다음 주 규칙 1줄 ·
   2개 이상 통과한 편은 후속편 후보로 backlog 에.
4. 채널끼리 비교할 때는 같은 지표만 본다 (주제가 달라 조회수 크기는 비교하지 않는다).
5. 4주치가 쌓이면 `tools/review.py` THRESHOLDS 를 채널 중앙값으로 바꾸자고 제안.
