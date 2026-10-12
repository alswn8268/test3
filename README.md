# 숏폼 제작 공장 — 주제별 여러 계정

주제가 다른 숏폼 계정 여러 개를 **한 공장**에서 만드는 저장소예요.
대본 → 사실 확인 → 3D 장면 렌더 → **자체 작곡 배경음·효과음** → 조립 → 업로드 문구 → 48시간 성과 점검까지
Claude Code 슬래시 명령으로 돌아가요. 사람이 꼭 판단하는 곳은 주제 선정 · 사실 확인(✅) · 업로드 버튼 세 군데예요.

## 지금 있는 계정(채널) 4개

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
- ✅ 업로드는 사람이 공식 도구(Meta Business Suite / TikTok Studio / YouTube Studio)에서 직접

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
| ⑦ 업로드 | `/post shortcut ep06` | `post.md` | **예약 버튼** |
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
