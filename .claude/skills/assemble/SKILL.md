---
name: assemble
description: 장면 클립을 이어 붙이고 자체 합성 BGM·효과음·자막(SRT)을 넣어 final.mp4 를 만든다. 인자는 채널 + 편.
---

# /assemble <채널> <편> — 조립·사운드

1. `channels/<채널>/episodes/<편>/clips/s01~s12.mp4` 확인. 없으면 `/render`.
2. 기본: `python -m tools.assemble <채널> <편>`
   - `channel.json` 의 bgm 스타일로 배경음을 **직접 합성** (100BPM, 컷이 박자에 맞음, 편마다 멜로디 다름)
   - 컷 휙 · 강조 팝 · 체크 틱 · 키 딸깍 · 숫자 딩 · 도장 쿵 효과음을 화면 애니메이션 시점에 맞춰 넣음
   - 음량 약 -14 LUFS 로 맞추고 `final.mp4` + `captions.srt` 생성
3. 외부 무료 음원을 쓰고 싶다면: `assets/bgm/LICENSES.md` 에 출처·라이선스를 먼저 적은 뒤 `--bgm assets/bgm/<파일>`.
   라이선스 기록이 없으면 쓰지 않는다. 인기 사운드는 넣지 않는다(앱에서 얹기). 무음본이 필요하면 `--silent`.
4. FilmCraft MCP 가 연결돼 있으면 손으로 다듬을 프로젝트 파일을 만들 때만 쓴다 (기본 경로는 위 명령).
5. 확인: `ffprobe` 로 30초·1080×1920·30fps, 사람에게 '최종 1회 시청' 요청. 다음은 `/post <채널> <편>`.
