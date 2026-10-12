---
name: post
description: 업로드용 캡션·해시태그·커버 문구·예약 시간을 channels/<채널>/episodes/epNN/post.md 로 만든다. 업로드(예약 버튼)는 사람이 직접 한다.
---

# /post <채널> <편> — 업로드 문구

1. `python -m tools.factcheck <채널> <편> --check` 가 통과하지 않았으면 멈춘다 (초안 영상은 올리지 않는다).
2. 초안: `python -m tools.post <채널> <편> --month <다시 볼 달> --tags <넓은1> <넓은2> <주제1> <주제2>`
   - 넓은 태그는 `channel.json` 의 broad_tags 에서, 주제 태그는 영상 핵심어. 채널 태그는 자동으로 붙는다.
3. 다듬기: 첫 줄 = 후킹 그대로, 둘째 줄 = '저장해두고 ○월에 다시 보기', 본문 2~3줄, 해시태그 정확히 5개.
4. 예약 표: 이 채널 `schedule` 의 요일·시간. **이 영상은 이 채널 계정에만** 올린다 (다른 계정에 같은 영상 금지).
5. **업로드·예약은 하지 않는다.** 사람이 각 플랫폼 공식 도구(Meta Business Suite / TikTok Studio / YouTube Studio)에서 직접 누른다.
