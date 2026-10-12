---
name: publish
description: 최종본을 승인해 2일 주기 자동 업로드 대기열에 넣거나, 자동 업로드 상태(다음 차례·기록·실패)를 확인한다. 인자는 채널 + 편, 또는 status.
---

# /publish <채널> <편> | status — 승인과 자동 업로드

## 승인 (`/publish why ep01`)
1. `python -m tools.approve <채널> <편>` 을 **먼저 검사용으로** 돌려 막히는 항목을 보여준다
   (대본 오류 · 사실 확인 ✅ 누락 · final.mp4 · post.md 세 플랫폼 문구).
2. 모두 통과하면 사람에게 확인한다: "final.mp4 를 끝까지 보셨나요? 승인하면 다음 차례(2일 주기)에 3개 플랫폼에 올라갑니다."
   **사람이 '예'라고 답한 경우에만** 승인 상태로 둔다. 아니면 `--revoke`.
3. 승인은 `script.json` 의 status 를 바꾸는 것이라, 커밋해서 **main 브랜치에 반영돼야** 예약 실행이 본다.

## 상태 (`/publish status`)
- `python -m tools.publish --list-due` — 오늘 올라갈 (채널, 편)
- `python -m tools.publish --due --dry-run` — 플랫폼별로 무엇이 올라갈지
- `channels/*/published.csv` — 올린 기록. `error:` 로 시작하는 줄이 있으면 원인(토큰 만료·심사 전 제한 등)을 설명하고 고칠 방법을 안내한다.

## 하지 않는 것
- 사람 확인 없이 approve 하지 않는다. `--live` 업로드를 Claude 가 직접 실행하지 않는다 (예약 실행이나 사람이 한다).
- 토큰·비밀키를 출력하거나 파일·커밋에 넣지 않는다.
- 브라우저 자동 클릭·비공식 업로드 도구는 쓰지 않는다.
