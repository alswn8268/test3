---
name: assemble
description: 장면 클립을 이어 붙이고 배경음·자막(SRT)을 붙여 final.mp4 를 만든다. FilmCraft MCP 우선, 실패하면 ffmpeg 대체 경로.
---

# /assemble — 조립·사운드

1. `episodes/<ep>/clips/s01~s12.mp4` 가 모두 있는지 확인. 없으면 `/render <ep>` 안내.
2. **기본 경로 — FilmCraft MCP** (`.mcp.json` 의 `filmcraft` 서버가 연결돼 있을 때):
   클립 12개를 순서대로 타임라인에 올리고, 컷 전환은 하드컷, 배경음은 `assets/bgm/` 의 직접 만든 음원만,
   자막은 `captions.srt`, 1080×1920 30fps H.264 로 `episodes/<ep>/final.mp4` 내보내기. 프로젝트 파일은
   `episodes/<ep>/<ep>.fcproj` 로 저장해 사람이 손볼 수 있게 한다.
3. **대체 경로 — ffmpeg** (FilmCraft 가 없거나 실패):
   `python -m tools.assemble <ep> [--bgm assets/bgm/<파일>]` → `final.mp4` + `captions.srt`.
4. 결과 확인: `ffprobe` 로 길이 30초·1080×1920·30fps 인지 확인하고, 사람에게 '최종 1회 시청'을 요청한다.
5. 인기 사운드는 넣지 않는다 (업로드할 때 앱에서 얹기). 다음은 `/post <ep>`.
