---
name: topics
description: 한 채널의 이번 주 주제 5개를 골라 channels/<채널>/topics/YYYY-Www.md 에 정리한다. 인자는 채널 이름. 최종 선택은 사람이 한다.
---

# /topics <채널> — 주제 선정

입력: `channels/<채널>/channel.json`(concept·pillars), `research/<이번주>.md`, `channels/<채널>/backlog.md`,
`channels/<채널>/learnings.md`, `python -m tools.review <채널>`(수치가 있으면).

1. 후보: 리서치의 이 채널 후보 + backlog 미사용 항목 + 지난주 '후속편 후보'.
2. 점수(각 1~3): 관심도 · 경쟁 낮음 · 시의성 · 공식 출처 확보 쉬움. **다른 채널과 겹치는 주제는 빼기** (계정마다 주제 분리).
3. money 채널은 시즌 2 + 상시 3 비율(`channels/money/backlog.md` 12개월 달력). 다른 채널은 기둥(pillars) 5개를 고르게.
4. `channels/<채널>/topics/<주차>.md` 표: 순위 · 주제 · 시리즈 태그 · 점수 · 후킹 초안 · 예정 편 번호 · 업로드 요일(채널 schedule).
5. **최종 5개는 사람에게 묻는다** (AskUserQuestion). 확정되면 ✅, 고르지 않은 후보는 backlog 에 추가.
6. 확정 주제마다 `/script <채널> <주제>` 안내.
