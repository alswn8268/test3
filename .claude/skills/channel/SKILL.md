---
name: channel
description: 새 주제 계정(채널)을 만든다 — 주제 검증, channel.json, 첫 백로그. 인자는 만들고 싶은 주제.
---

# /channel <주제> — 새 계정 만들기

1. 주제를 검증하고 근거를 단계별로 보여준다: ① 타깃이 누구인가 ② 공식 출처가 있는가(사실 확인 가능?)
   ③ 소재가 100개 이상 나오는가 ④ 기존 채널(`channels/*/channel.json`)과 겹치지 않는가 ⑤ 저장·공유를 부르는 형식인가.
   하나라도 약하면 사람에게 먼저 말한다.
2. `python -m tools.new_channel <slug> "<계정 이름>" --signal "#RRGGBB" --bgm <lofi|upbeat|bright> --hashtag <태그>`
   - 신호색: 먹색 글자가 위에 올라가도 읽히는 중간 밝기 (기존 채널과 다르게)
3. `channel.json` 의 TODO 채우기: concept · voice · pillars 5개 · props(3D 소품) · broad_tags · official_sources · schedule.
4. `backlog.md` 에 첫 주제 후보 10개. 첫 편은 `/script <slug> <주제>`.
5. 계정 개설·로그인·업로드는 사람이 한다. `accounts` 칸에 계정 핸들을 적어 두게 안내.
