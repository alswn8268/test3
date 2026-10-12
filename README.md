# 숏폼 제작 공장 — 주제별 여러 계정

주제가 다른 숏폼 계정 여러 개를 **한 공장**에서 만드는 저장소예요.
대본 → 사실 확인 → 3D 장면 렌더 → **자체 작곡 배경음·효과음** → 조립 → 업로드 문구 → 48시간 성과 점검까지
Claude Code 슬래시 명령으로 돌아가요. 사람이 꼭 판단하는 곳은 주제 선정 · 사실 확인(✅) · 최종 승인 세 군데예요.
승인한 영상은 **2일에 한 번 자동으로** 유튜브 쇼츠 · 틱톡 · 인스타 릴스에 올라가게 할 수 있어요 ([10. 자동 업로드](#10-자동-업로드-2일에-한-번)).

## 지금 있는 계정(채널) 4개 — 각각 틱톡 · 유튜브 쇼츠 · 인스타 릴스

| 채널 | 계정 이름 | 누구에게 무엇을 | 색 | 배경음 | 편 |
|---|---|---|---|---|---|
| `money` | 월급 사용설명서 | 20~30대 직장인의 세금·카드·통장 | 주황 | 로파이 | 5 |
| `shortcut` | 칼퇴 단축키 | 엑셀·윈도우 단축키 하나로 10분 아끼기 | 초록 | 업비트 | 5 |
| `spelling` | 한 끗 맞춤법 | 보고서·카톡에서 자주 틀리는 맞춤법 | 파랑 | 밝은 팝 | 5 |
| `why` | 그거 왜 그래? | 매일 보는 것의 '왜?' — 반전 있는 과학·생활 상식 | 노랑 | 미스터리 | 5 |

> **왜 이 두 주제를 골랐나** (자세한 근거: [`research/2026-W42.md`](research/2026-W42.md))
> 1. 타깃이 기존 채널과 같은 20~30대 직장인이라, 계정끼리 소개해 주기 좋아요.
> 2. 마이크로소프트 도움말·국립국어원처럼 **공식 출처**가 분명해서 사실 확인이 쉬워요.
> 3. 소재가 수백 개라 매일 올려도 바닥나지 않아요.
> 4. '저장'(단축키)과 '공유'(맞춤법 퀴즈)를 부르는 형식이에요.
>
> **'그거 왜 그래?'(호기심 채널)를 더한 이유**: 정보 채널 3개는 '저장'은 잘 받지만 처음 보는 사람을 멈추게 하는 힘이 약해요.
> 호기심형("딸기는 베리가 아닙니다")은 타깃을 가리지 않고 첫 3초에 멈추게 하고, 댓글·공유를 부르기 쉬워요.
> 대신 **어그로는 호기심으로만** 끌고, 논란·공포·낚시는 쓰지 않아요 (규칙: `CLAUDE.md` '후킹 공식').

### 후킹 공식 (어그로는 OK, 낚시는 NO)

| 공식 | 예 (실제 대본) |
|---|---|
| 당신 · 지금 | "지금 보는 해는 **8분 전** 해입니다" |
| 반전 | "딸기는 **베리**가 아닙니다" |
| 무해한 논쟁 | "빨대 구멍은 1개일까 **2개**일까?" |
| 공포 대신 역사 | "네모난 창문 때문에 **추락한 비행기**" |
| 상식 깨기 | "물에 불어서 쭈글해지는 게 **아닙니다**" |

정치·종교·성별·세대 갈등, 건강 공포, 실존 인물 비방, 약속한 답을 안 주는 낚시는 금지예요.

### 계정 이름 · 아이디 · 프로필

| 채널 | 아이디 (틱톡·유튜브·인스타 공통) | 프로필 사진 |
|---|---|---|
| 월급 사용설명서 | `@wolgeup.manual` | `assets/profiles/money.png` |
| 칼퇴 단축키 | `@kaltoe.key` | `assets/profiles/shortcut.png` |
| 한 끗 맞춤법 | `@hankkeut.spell` | `assets/profiles/spelling.png` |
| 그거 왜 그래? | `@geugeo.wae` | `assets/profiles/why.png` |

예비 아이디·소개 문구·이렇게 지은 이유, **한 사람이 여러 계정을 운영해도 되는지(플랫폼 정책)**, **협찬 받기 좋은 주제와 광고 표시 규칙**은
[`research/accounts-and-sponsorship.md`](research/accounts-and-sponsorship.md)에 정리했어요. 프로필 사진은 `node render/profile.mjs` 로 다시 만들 수 있어요.

### 채널마다 화면이 완전히 달라요

색만 바꾼 게 아니라 **배경 · 글꼴 · 강조 방식 · 글자 등장 · 3D 배치 · 전환음**이 채널마다 달라요.

| 채널 | 화면 테마 | 이렇게 보여요 |
|---|---|---|
| 월급 사용설명서 | 종이 장부 | 종이 질감, 주황 형광펜, 큰 명조 숫자, 동전·카드 3D |
| 칼퇴 단축키 | 엑셀 화면 | 셀 격자와 A·B·C 열 머리, 강조는 '셀 선택 상자', 글자가 한 글자씩 타이핑, 장면 전환 때 키보드 딸깍 |
| 한 끗 맞춤법 | 공책·칠판 | 공책 줄과 빨간 여백선(후킹은 초록 칠판), 명조 제목, 틀린 말엔 펜 취소선·맞는 말엔 동그라미, 종이 넘기는 소리 |
| 그거 왜 그래? | 파란 실험실 | 파란 배경과 움직이는 바닥 격자, 흰 글자 + 굵은 외곽선 가운데 정렬, 노란 키워드가 '팡', 물음표·전구 3D가 크게 |

### 세 플랫폼에 올릴 때

`/post <채널> <편>` 이 `post.md` 에 **틱톡 · 유튜브 쇼츠 · 인스타 릴스** 문구를 따로 만들어 줘요.

| 플랫폼 | 문구 | 주의 |
|---|---|---|
| 틱톡 | 후킹 + 저장 이유 + 해시태그 5개 | 예약 후 수정 불가 → 확정 후 예약 |
| 유튜브 쇼츠 | 짧은 제목 + 설명 첫 줄 후킹 + 해시태그 3개 이내 | `captions.srt` 자막 업로드 추천 |
| 인스타 릴스 | 후킹 + 저장 이유 + 본문 + 해시태그 5개 | 커버 `preview/s01.png` |

세 곳 모두 **`final.mp4` 원본**을 올려요. 틱톡에서 내려받은 워터마크 영상을 릴스·쇼츠에 올리면 추천에서 밀릴 수 있어요.
성과는 `metrics.csv` 에 플랫폼별로(`tiktok` · `youtube` · `reels`) 한 줄씩 넣으면 `/review` 가 같은 기준으로 비교해요.

### 트렌드 소재 찾기

`/trend` 가 웹 조사 + 사람 메모를 합쳐요. 사람 메모는 [trafficscent.com](https://trafficscent.com)(오늘의 이슈 · 유튜브 급상승 ·
해외 레딧/5ch/PTT 글로벌 탭)을 훑고 3~10줄 붙여넣으면 돼요. 커뮤니티 글은 **소재 힌트로만** 쓰고, 글·짤 원본은 가져오지 않으며,
내용은 공식 출처로 다시 확인해요. (이 클라우드 작업 환경에서는 사이트 접속이 막혀 있어서 사람이 보고 붙여넣는 방식이에요.)

---

## 1. 처음 한 번만: 설치

필요한 것: Node.js 20+, Python 3.11+, ffmpeg

```bash
cd shorts-channel
make setup          # npm 패키지 + render/vendor 준비 + 파이썬 numpy·pytest
```

## 2. 바로 해보기

```bash
make stills CH=shortcut EP=ep01      # 미리보기 PNG 12장
make drafts                          # 4개 채널 20편을 전부 영상으로 (초안, 약 45분)
```

결과: `channels/<채널>/episodes/epNN/final.mp4` (세로 1080×1920, 30초, 배경음·효과음 포함)

---

## 3. 소리는 어떻게 넣나요? (저작권 걱정 없이)

**배경음을 코드로 직접 작곡**해요 (`tools/audio.py`). 남의 음원을 쓰지 않으니 저작권 문제가 생기지 않아요.

| 무엇 | 어떻게 |
|---|---|
| 배경음 | 채널마다 스타일 고정(로파이·업비트·밝은 팝·미스터리), **편마다 조성·멜로디가 달라서** 같은 곡이 반복되지 않아요 |
| 박자 | 100BPM 고정 → 한 마디 = 2.4초 = 장면 길이. 그래서 **장면이 바뀌는 순간이 항상 비트에 맞아요** |
| 효과음 | 장면 전환 '휙' · 형광펜 '팝' · 체크 '틱' · 키캡 '딸깍' · 숫자 완성 '딩' · CTA 도장 '쿵' — 화면 애니메이션 시점에 맞춤 |
| 음량 | 약 -14 LUFS (숏폼 플랫폼에서 흔히 쓰는 수준) |

```bash
python3 -m tools.audio --demo upbeat out.wav           # 스타일 미리 듣기
python3 -m tools.assemble shortcut ep01                # 기본: 자체 배경음 + 효과음
python3 -m tools.assemble shortcut ep01 --bgm assets/bgm/song.mp3   # 외부 무료 음원 + 효과음
python3 -m tools.assemble shortcut ep01 --silent       # 무음본 (앱에서 인기 사운드를 얹을 때)
```

외부 무료 음원(유튜브 오디오 보관함, 픽사베이 등)을 쓰려면 **먼저** [`assets/bgm/LICENSES.md`](assets/bgm/LICENSES.md)에
출처와 라이선스를 적어 주세요. 사이트마다 '상업적 이용'·'출처 표기' 조건이 달라요.
인기 사운드는 영상 파일에 넣지 말고, 업로드할 때 앱에서 낮은 볼륨으로 얹는 게 안전해요 (음소거 방지).

---

## 4. 인기 숏폼 분석

두 가지 방법을 함께 써요.

1. **공개된 가이드·정책 조사** — 결과는 [`research/2026-W42.md`](research/2026-W42.md).
   여러 출처에서 겹친 공통점(첫 3초 후킹, 인트로 없음, 자막을 화면에 박기, 잦은 화면 변화, 저장 이유 제시)을 포맷에 반영했어요.
   업체 블로그 숫자는 근거가 약해서 '방향'만 참고해요.
2. **실제 인기 영상을 숫자로 재기** — 잘 된 영상 몇 개를 `refs/` 폴더에 두고(분석용, git에 안 올라감):

```bash
python3 -m tools.analyze_ref refs/*.mp4 --out research/refs-2026-W43.md
```

| 재는 것 | 예시로 알 수 있는 것 |
|---|---|
| 컷 간격 중앙값 | 참고 영상이 1.5초마다 바뀌면 → 우리 2.4초 장면을 쪼갤지 검토 |
| 첫 컷 시점 | 1초 만에 화면이 바뀌면 → 후킹 장면에 움직임 추가 |
| 음량·BPM | 우리 음악이 너무 작거나 느린지 비교 |

마지막에 "바꿔볼 점"을 **하나만** 제안해요 (한 번에 하나씩 바꿔야 무엇이 효과였는지 알 수 있어요).

---

## 5. 여러 계정 운영 — 꼭 지킬 것

플랫폼들이 '같은 영상 반복·대량 업로드'를 점점 엄격하게 보고 있어요 (유튜브 '진정성 없는 콘텐츠' 정책, 인스타 '독창적이지 않은 콘텐츠' 추천 제외).

- ✅ 계정마다 **주제가 달라요** → 영상도 그 계정 전용
- ❌ 같은 영상을 여러 계정에 올리기
- ❌ 계정끼리 좋아요·댓글·팔로우 몰아주기 (참여 조작으로 보일 수 있음)
- ❌ 글자만 바꾼 영상을 대량으로 올리기 — 편마다 새 정보가 있어야 해요
- ✅ 업로드는 공식 예약 도구(Meta Business Suite / TikTok Studio / YouTube Studio)나 공식 API 자동 업로드로만 — 브라우저 자동 클릭 도구는 쓰지 않아요

계정 핸들은 각 `channels/<채널>/channel.json` 의 `accounts` 칸에 적어 두세요. `/post` 가 업로드 문구에 같이 표시해요.

**새 계정 추가하기**:

```bash
python3 -m tools.new_channel cook "자취 요리 3분" --signal "#E8A100" --bgm bright --hashtag 자취요리3분
```

또는 Claude Code에서 `/channel 자취 요리` — 주제가 계정이 될 만한지(출처·소재 수·겹침) 먼저 따져 줘요.

---

## 6. 매주 하는 일 (Claude Code)

| 단계 | 명령 | 결과 | 사람이 할 일 |
|---|---|---|---|
| ① 트렌드 | `/trend` (+ `/analyze`) | `research/2026-W43.md` | 앱 직접 탐색 15분, 참고 영상 모으기 |
| ② 주제 | `/topics shortcut` | `channels/shortcut/topics/…` | **최종 선택** |
| ③ 대본 | `/script shortcut ep06` | `script.json` | 말투 다듬기 |
| ④ 사실 확인 | `/factcheck shortcut ep06` | `factcheck.md` | **원문 보고 ✅** |
| ⑤ 렌더 | `/render shortcut ep06` | `preview/`, `clips/` | 미리보기 확인 |
| ⑥ 조립 | `/assemble shortcut ep06` | `final.mp4`, `captions.srt` | 최종 1회 시청 |
| ⑦ 업로드 문구 | `/post shortcut ep06` | `post.md` (플랫폼 3곳) | 문구 확인 |
| ⑦-1 승인 | `/publish shortcut ep06` | 승인 → 2일 주기 자동 업로드 대기열 | **최종 1회 시청 후 승인** |
| ⑧ 점검 | `/review shortcut` | `metrics.csv`, `learnings.md` | 수치 입력 |

일요일 밤엔 `make batch` 를 걸어두면 사실 확인이 끝난 모든 채널의 모든 편이 영상까지 완성돼요.

---

## 7. 대본 파일(script.json) 장면 종류

| type | 화면 | 예 |
|---|---|---|
| `hook` | 먹 배경 큰 자막 (3초) | "300줄 복붙 / [3초]면 끝" |
| `point` | 종이 배경 설명 | "예시 [한 칸]이 / 곧 명령어" |
| `number` | 먹 배경 큰 숫자 카운트업 | "1,000만" |
| `compare` | 왼쪽(틀림·기존) vs 오른쪽(맞음·추천) | 되요 → **돼요** |
| `keys` | 키캡이 하나씩 눌리며 등장 + 딸깍 | [Ctrl] + [E] |
| `check` | 체크리스트 3개 | 오늘 고칠 것 |
| `cta` | 저장/공유 도장 (3초) | "내일 써먹게 [저장]" |

`[단어]` = 신호색 형광펜, `{단어}` = 신호색 글자, 한 장면에 강조 하나. 대본을 고치면 `make check`.

---

## 8. 폴더 구조

```
shorts-channel/
  CLAUDE.md                      모든 채널 공통 규칙 (Claude Code가 자동으로 읽음)
  .claude/skills/                trend · analyze · topics · script · factcheck · render · assemble · post · review · channel
  channels/
    money/      channel.json · episodes/ep01~05 · topics/ · metrics.csv · learnings.md · backlog.md
    shortcut/   (같은 구조)
    spelling/   (같은 구조)
    why/        (같은 구조)
  research/                      주간 트렌드·참고 영상 분석 (채널 공통)
  render/                        render.html (three.js) · capture.mjs (촬영기)
  tools/                         validate · factcheck · audio · assemble · batch · analyze_ref · post · review · new_episode · new_channel
  assets/fonts/  assets/bgm/     폰트(SIL OFL) · 외부 음원 + 라이선스 기록
  tests/                         python3 -m pytest
```

## 9. 알아둘 점

- 새로 만든 15편(칼퇴 단축키·한 끗 맞춤법·그거 왜 그래?)과 기존 5편 모두 **사실 확인 표의 ✅ 가 아직 비어 있어요**. `make drafts` 로 만든 영상은 초안이니
  `/factcheck` 로 출처를 채우고 직접 확인한 뒤에 올려 주세요.
- 내레이션(목소리)은 아직 없어요. 지금은 '자막 + 음악 + 효과음' 형식이고, `say` 문장이 자막 파일(`captions.srt`)로 들어가요.
- FilmCraft MCP는 선택 사항이에요 (손으로 다듬을 때만).

---

## 10. 자동 업로드 (2일에 한 번)

### 어떻게 돌아가나요?

```
[내가 할 일]  영상 확인 → python -m tools.approve why ep01   (승인 = "이거 올려도 돼")
                  ↓  (main 브랜치에 반영)
[GitHub Actions]  매일 11:40 깨어남 → 채널마다 "마지막 업로드 후 2일 지났나?" 확인
                  → 지났으면 다음 승인 편을 렌더 → 유튜브 · 틱톡 · 인스타에 공식 API로 업로드
                  → channels/<채널>/published.csv 에 기록 (같은 편 두 번 안 올림)
```

- **승인 안 한 편은 절대 안 올라가요.** 승인하려면 사실 확인 표 ✅ · `final.mp4` · `post.md` 세 플랫폼 문구가 모두 끝나 있어야 해요.
- 2일 주기는 `channel.json` → `publish.every_days` 로 바꿀 수 있어요. 승인한 편이 없으면 그냥 쉬어요.
- GitHub Actions는 GitHub 서버에서 도는 무료 예약 실행이라 **내 PC가 꺼져 있어도** 돼요.
  (비공개 저장소는 한 달 무료 시간이 정해져 있어요. 한 번에 약 10~15분 × 하루 1~2편이면 보통 충분해요.)

### 처음 한 번 준비 (플랫폼별)

각 플랫폼 **개발자 앱**을 만들고 계정마다 로그인 토큰을 받아 GitHub Secrets에 넣어요.
토큰은 비밀번호와 같아서 저장소·채팅에 붙여넣으면 안 돼요.

| 플랫폼 | 준비 | 꼭 알아둘 점 |
|---|---|---|
| 유튜브 | Google Cloud 프로젝트 → YouTube Data API v3 사용 → OAuth 클라이언트(데스크톱 앱) → 채널마다 `python -m tools.auth_youtube` 로 refresh token 받기 | **심사(API 감사) 전에는 API로 올린 영상이 '비공개'로 잠겨요.** 공개로 올리려면 Google의 API 감사 신청이 필요해요 (몇 주 걸릴 수 있음) |
| 틱톡 | TikTok for Developers 앱 → Content Posting API → 계정마다 로그인해서 refresh token | 기본은 **받은편지함(초안) 모드**: 틱톡 앱에 알림이 오면 '게시'만 누르면 돼요(10초). 완전 자동 게시는 틱톡 앱 심사를 통과해야 하고, 그 전엔 '나만 보기'로만 올라가요 |
| 인스타그램 | 프로페셔널(비즈니스/크리에이터) 계정 → Meta 개발자 앱(Instagram API, 콘텐츠 게시 권한) → 계정마다 사용자 ID와 장기 토큰 | 장기 토큰은 **약 60일마다 갱신**해야 해요. 인스타그램 로그인 방식이면 `IG_GRAPH_HOST=graph.instagram.com` 도 Secrets에 |

GitHub 저장소 → Settings → Secrets and variables → Actions:

- **Secrets** (공통): `YT_CLIENT_ID` `YT_CLIENT_SECRET` `TIKTOK_CLIENT_KEY` `TIKTOK_CLIENT_SECRET`
- **Secrets** (채널마다, `<채널>` = `MONEY` `SHORTCUT` `SPELLING` `WHY`):
  `YT_REFRESH_TOKEN_<채널>` `TIKTOK_REFRESH_TOKEN_<채널>` `IG_USER_ID_<채널>` `IG_ACCESS_TOKEN_<채널>`
- **Variables**: `SHORTS_AUTOPUBLISH` = `on` (켜기) / `off` (끄기)

### 켜기 전에 시험하기

1. Actions 탭 → `shorts-autopublish` → **Run workflow** (live 체크 안 함) → 무엇이 어디에 올라갈지 미리보기만 해요.
2. 괜찮으면 `SHORTS_AUTOPUBLISH = on`. 그다음부터 매일 11:40에 확인하고, 차례가 된 채널만 올려요.
3. 내 PC에서도 확인할 수 있어요: `python -m tools.publish --list-due` · `python -m tools.publish --due --dry-run`

### 심사가 끝나기 전엔 이렇게 쓰는 걸 추천해요

| 플랫폼 | 심사 전 | 심사 후 |
|---|---|---|
| 유튜브 | 자동 업로드 → 비공개로 올라감 → Studio에서 '공개'로 바꾸기, 또는 Studio 예약 기능 사용 | 완전 자동 |
| 틱톡 | 자동으로 받은편지함까지 → 앱에서 '게시' 한 번 | 완전 자동 (`channel.json` → `publish.tiktok_mode` = `direct`) |
| 인스타 | 내 계정이 앱 관리자·테스터면 개발 모드로 바로 자동 게시 가능 | 완전 자동 |
