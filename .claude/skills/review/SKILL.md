---
name: review
description: 업로드 48시간 뒤 인사이트 수치를 metrics.csv 에 넣고 통과·미달을 판정해 learnings.md 와 다음 주 대본 규칙에 반영한다.
---

# /review — 48시간 점검

1. 사람이 준 인사이트 수치를 `metrics.csv` 에 한 줄씩 추가한다 (플랫폼마다 한 줄).
   열: `ep,platform,posted_at,views,viewed_3s,avg_watch_sec,saves,shares,profile_visits,follows`
   숫자가 빠지면 추측하지 말고 물어본다.
2. `python -m tools.review [<ep>]` 로 판정표를 만든다.
   기준: 3초 유지율 70% · 완주율 50% · 저장률 1% · 공유율 0.5% · 팔로우 전환 10% (시작용 가설).
3. `learnings.md` 맨 위에 이번 주 항목을 추가한다:
   - 판정표, 잘된 편·안 된 편의 차이(후킹 문장, 장면 타입, 업로드 시간)
   - **미달 지표 하나만** 골라 다음 주 대본 규칙 1줄 (예: "후킹 첫 줄에 금액을 넣는다")
   - 2개 이상 통과한 편 → '후속편 후보'로 `backlog.md` 에 추가 (같은 후킹, 다른 주제)
4. 4주치 데이터가 쌓이면 `tools/review.py` 의 THRESHOLDS 를 내 채널 중앙값으로 바꾸자고 제안한다.
