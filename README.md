# 월급 사용설명서 — 숏폼 제작 저장소

20~30대 직장인의 '월급 지키기'를 다루는 숏폼 채널의 제작 공장이에요.
대본 → 사실 확인 → 3D 장면 렌더 → 조립 → 업로드 문구 → 48시간 성과 점검까지,
**Claude Code 슬래시 명령 하나씩**으로 돌아가도록 만들었어요. 사람이 꼭 판단하는 곳은
②주제 선정 · ④사실 확인 · ⑦업로드 세 군데뿐이에요.

> 운영 규칙 원본: '숏폼 수익화 운영 파이프라인 — 월급 사용설명서' 문서.
> 그 규칙은 [`CLAUDE.md`](CLAUDE.md) 로 옮겨져 있어서, 이 폴더를 Claude Code 로 열면 매번 자동으로 지켜져요.

---

## 1. 처음 한 번만: 설치

필요한 것: Node.js 20 이상, Python 3.11 이상, ffmpeg, (Chromium — Playwright 가 사용)

```bash
cd shorts-channel
make setup          # = npm install + npm run setup
```

`npm run setup` 은 렌더러가 쓰는 three.js 와 큰 숫자용 폰트(Noto Serif KR)를 `render/vendor/` 에 복사해요.
이 폴더는 git 에 올리지 않고, 지워져도 이 명령으로 다시 만들 수 있어요.

> 💡 Playwright 가 브라우저를 못 찾으면 `npx playwright install chromium` 을 한 번 실행하거나,
> 이미 설치된 크롬 경로를 `CHROMIUM_PATH=/경로/chrome` 로 알려주세요.

## 2. 바로 해보기: 1편 미리보기 만들기

```bash
make stills EP=ep01        # episodes/ep01/preview/s01.png ~ s12.png
```

이렇게 12장의 PNG 가 나오면 성공이에요. 예를 들어 `s01.png` 는 검정 배경에 "연봉의 25%" 가
주황 형광펜과 함께 나오는 후킹 장면이에요. (1편 시안: [`design/ep01_storyboard.png`](design/ep01_storyboard.png))

영상까지 뽑아보려면:

```bash
node render/capture.mjs ep01      # 장면 클립 12개 (장면당 약 20~30초)
make assemble EP=ep01             # → episodes/ep01/final.mp4 + captions.srt
```

> `make render` 는 사실 확인(④)이 끝나야 실행돼요. 처음 받은 5편은 아직 출처 칸이 비어 있어서,
> 연습할 땐 위처럼 `node render/capture.mjs` 를 직접 쓰면 돼요.

---

## 3. 매주 하는 일 (Claude Code 에서)

| 단계 | 명령 | 하는 일 | 결과 파일 | 사람이 할 일 |
|---|---|---|---|---|
| ① 트렌드 | `/trend` | 이번 주 뜨는 포맷·사운드·돈 이슈 조사 | `research/2026-W42.md` | 앱 직접 탐색 15분 |
| ② 주제 | `/topics` | 주제 5개 추천 (시즌 2 + 상시 3) | `topics/2026-W42.md` | **최종 선택** |
| ③ 대본 | `/script ep06` | 12장면 30초 대본 | `episodes/ep06/script.json` | 말투 다듬기 |
| ④ 사실 확인 | `/factcheck ep06` | 숫자마다 공식 출처 링크 | `episodes/ep06/factcheck.md` | **원문 확인 후 ✅** |
| ⑤ 렌더 | `/render ep06` | 미리보기 PNG + 장면 클립 | `preview/`, `clips/` | 미리보기 확인 |
| ⑥ 조립 | `/assemble ep06` | 클립 연결 + 배경음 + 자막 | `final.mp4`, `captions.srt` | 최종 1회 시청 |
| ⑦ 업로드 | `/post ep06` | 캡션·해시태그·예약 시간 | `post.md` | **예약 버튼** |
| ⑧ 점검 | `/review ep06` | 48시간 수치로 통과·미달 판정 | `metrics.csv`, `learnings.md` | 수치 입력 |

**주간 루틴** (1인 기준 주 3시간 안팎으로 주 5회 업로드)

- 일: `/trend` → `/topics` → 5편 `/script` → `/factcheck` (1시간 30분)
- 일 밤: 5편 `/render` + `/assemble` 걸어두고 자기 (자동 약 1시간)
- 월: 5편 최종 시청 → `/post` → 플랫폼 예약 (40분)
- 화~토: 예약 게시, 댓글 답글 (하루 10분) / 업로드 +48시간: 수치 입력 → `/review`
- 토: `learnings.md` 읽고 다음 주 `backlog.md` 정리 (15분)

---

## 4. 대본 파일(script.json) 읽는 법

한 편 = 장면 12개. 장면 하나는 이렇게 생겼어요:

```json
{ "type": "point", "label": "01  문턱",
  "lines": ["카드값이 연봉의", "[25%]를 넘어야"],
  "sub": "그때부터 공제가 시작돼요",
  "say": "카드 소득공제는 1년 카드값이 연봉의 25퍼센트를 넘은 부분부터 계산돼요.",
  "visual": "종이 배경, 문장이 아래에서 위로 올라옴",
  "dur": 2.4 }
```

- `lines` 큰 제목 자막 (한 줄 9글자 이하) · `sub` 보조 자막 · `say` 내레이션 · `visual` 화면 설명
- `[25%]` → 주황 형광펜이 그어짐, `{0원}` → 주황 글자. 한 장면에 강조는 하나만.
- `type`: `hook`(검정·후킹) · `point`(설명) · `number`(검정·큰 숫자 카운트업) · `compare`(좌우 비교) · `check`(체크리스트) · `cta`(저장·공유 도장)

대본을 고친 뒤엔 꼭 검사하세요:

```bash
python3 -m tools.validate ep01     # 오류 0 이어야 렌더 가능
make check                         # 전체 편 검사
```

## 5. 사실 확인 표(factcheck.md)

```bash
python3 -m tools.factcheck ep01          # 숫자가 들어간 문구를 표로 뽑기
python3 -m tools.factcheck ep01 --check  # 모든 줄에 출처 URL + ✅ 가 있는지 검사
```

| # | 장면 | 화면 문구 | 출처 (URL) | 확인 |
|---|---|---|---|---|
| 1 | 01 | 연봉의 25% | https://www.nts.go.kr/… | ✅ |

**출처 링크가 없는 숫자는 영상에 넣지 않는 것**이 이 채널의 제일 중요한 규칙이에요.
`/factcheck` 는 Claude 가 링크를 찾아 채우고, ✅ 는 사람이 원문을 직접 보고 찍어요.

## 6. 성과 점검(metrics.csv)

플랫폼 인사이트 숫자를 한 줄씩 넣으면 돼요:

```csv
ep,platform,posted_at,views,viewed_3s,avg_watch_sec,saves,shares,profile_visits,follows
ep01,reels,2026-10-14 21:20,1000,750,12,20,2,50,6
```

```bash
make review
```

| 지표 | 계산 | 통과 기준 | 미달이면 고칠 곳 |
|---|---|---|---|
| 3초 유지율 | 3초 넘게 본 사람 ÷ 조회 | 70% | 후킹 문장, 첫 장면 진입 속도 |
| 완주율 | 평균 시청 시간 ÷ 30초 | 50% | 중간 장면 줄이기 |
| 저장률 | 저장 ÷ 조회 | 1% | 체크리스트 장면, '나중에 볼 이유' CTA |
| 공유율 | 공유 ÷ 조회 | 0.5% | '부모님·친구에게' 같은 공유 대상 지목 |
| 팔로우 전환 | 팔로우 ÷ 프로필 방문 | 10% | 프로필 첫 줄, 고정 게시물 |

2개 이상 통과한 편은 '후속편 후보'가 되고, 가장 많이 미달한 지표 하나만 다음 주 대본 규칙에 반영해요.

---

## 7. 폴더 구조

```
shorts-channel/
  CLAUDE.md              채널 규칙 (타깃·말투·디자인 시스템·사실 확인)
  .mcp.json              FilmCraft MCP 등록 (조립용, 따로 설치 필요)
  .claude/skills/        trend · topics · script · factcheck · render · assemble · post · review
  assets/fonts/          Pretendard (SIL OFL)
  assets/bgm/            직접 만든 배경음
  design/                1편 12장면 시안
  render/                render.html (three.js 렌더러) · capture.mjs (촬영기)
  tools/                 파이썬 도구 (validate · factcheck · assemble · post · review · new_episode)
  tests/                 도구 단위 테스트 (python3 -m pytest)
  research/  topics/     주간 리서치·주제 선정 기록
  episodes/ep01~ep05/    script.json · factcheck.md (+ 렌더하면 preview/ clips/ final.mp4)
  metrics.csv  learnings.md  backlog.md (12개월 콘텐츠 달력 포함)
```

## 8. 들어 있는 5편

| 편 | 시리즈 | 제목 | 업로드(제안) |
|---|---|---|---|
| ep01 | 상시 · 카드 쓰는 법 | 연봉의 25%, 카드 공제 문턱 | 화 21:20 |
| ep02 | 시즌 · 연말정산 | 12월 31일 IRP 막차 | 목 21:20 |
| ep03 | 시즌 · 연말정산 | 고향사랑기부 20만 원의 비밀 | 토 10:30 |
| ep04 | 상시 · 통장 관리 | 월급 통장 4개로 쪼개기 | 월 12:10 |
| ep05 | 상시 · 자취 돈 | 월세 세액공제 170만 원 | 수 07:50 |

## 9. 알아둘 점

- **업로드는 끝까지 사람이 눌러요.** 계정 정지 위험과 최종 품질 확인 때문에 자동 게시는 넣지 않았어요.
- 인기 사운드는 영상에 넣지 않고 업로드할 때 앱에서 얹어요 (음원 문제로 음소거되는 것 방지).
- 틱톡 예약은 한 번 걸면 수정이 안 돼요. 문구를 확정한 뒤 예약하세요.
- FilmCraft 는 이 저장소에 포함돼 있지 않아요. 설치 전까지 `/assemble` 은 ffmpeg 대체 경로(`tools/assemble.py`)로 돌아가요.
- 남은 개발: 일요일 밤 자동 실행(리서치~렌더 예약 실행)은 위 명령들이 안정된 뒤에 붙일 예정이에요.
