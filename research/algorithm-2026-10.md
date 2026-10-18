# 릴스·틱톡·쇼츠 추천 알고리즘 정리 (2026-10)

> 공식 발표(인스타그램·틱톡·유튜브)와 업계 자료를 바탕으로 정리. 업계 자료의 숫자·조건은 '방향 참고'.

## 한 줄 요약
세 플랫폼 모두 새 영상을 **작은 무리에게 먼저 보여 주고**, 그 사람들이 **끝까지 보고 · 누군가에게 보내면** 더 크게 민다.
유튜브 쇼츠 책임자 표현으로 "시청자가 곧 알고리즘". 알고리즘을 맞추는 게 아니라 **처음 몇백 명의 반응**을 만드는 일이다.

## 플랫폼이 직접 말한 신호

| 플랫폼 | 중요하다고 밝힌 신호 | 덜 추천한다고 밝힌 것 |
|---|---|---|
| 인스타 릴스 | 시청 시간 · **도달 대비 DM 보내기** · 도달 대비 좋아요 (보내기가 비팔로워 확산에 가장 큼) | 워터마크, 저화질, **글자 위주 영상**, 남의 콘텐츠 재게시 |
| 틱톡 | **시청 시간**이 가장 크고, 좋아요·공유·댓글·건너뛰기 | 이미 본 영상, 가이드라인 위반 |
| 유튜브 쇼츠 | '본 비율(스와이프 안 하고 본 사람)', 독창성 | 다른 창작자 콘텐츠 재업로드 |

'도달 대비'는 총합이 아니라 비율 — 1,000명 중 10명 보내기(1%)가 10,000명 중 30명(0.3%)보다 낫다. 작은 계정도 불리하지 않다.

## 우리 채널에 적용한 것 / 할 것

| # | 근거 | 할 일 | 상태 |
|---|---|---|---|
| 1 | 인스타가 '글자 위주' 릴스를 덜 보여 준다고 공식 명시 | 우리 12장면은 큰 자막 위주 → **내레이션(목소리)** 추가 (`say` 문장이 이미 있음), 가능하면 실제 화면·물건 컷 1~2개 | 결정 필요 (TTS 방식) |
| 2 | 보내기가 비팔로워 확산에 가장 강함 | CTA 에서 **보낼 사람을 구체적으로**: "카드만 쓰는 회사 동기에게" > "공유해 주세요" | 대본 규칙 반영 |
| 3 | 틱톡 검색은 말·화면 글자를 읽고, 초반 이탈이 확산을 멈춤 | **첫 1초에 주제어를 말 + 자막으로**, 캡션 첫 줄 맨 앞에도 같은 주제어 | 대본 규칙 반영 |
| 4 | 인스타 재게시 추천 제외, 유튜브 재업로드 감소 | 플랫폼마다 **원본 MP4**를 따로 업로드 (워터마크 파일 금지) | 이미 적용 (`publish.py`) |
| 5 | 인스타 'Your Algorithm' — 시청자가 주제를 고름 | 채널 기둥 5개 안에서만 (단발성 주제 금지) | 이미 적용 (`channel.json` pillars) |
| 6 | 체험판 릴스(Trial Reels) = 비팔로워에게만 노출 | 같은 영상, 후킹만 두 가지로 24시간 시험 → 좋은 쪽을 본 업로드 (자격 조건은 앱에서 확인) | 수동 실험 |

## 생각보다 덜 중요한 것
- **해시태그**: 모세리 "노출을 늘리지 않는다, 무슨 글인지 설명할 뿐". 인스타는 게시물당 5개 제한을 도입 중 → 우리 규칙(5개)과 같음.
- **올리는 시간**: 유튜브 쇼츠 책임자 "최적화 대상이 아니다". 정확한 분보다 **꾸준함**.
- **팔로워 수**: 틱톡 공식 페이지에 추천 피드의 직접 요인으로 나오지 않음.

## 수익화 확인 사항
틱톡 크리에이터 리워드는 **1분 넘는 영상**만 대상 (+ 팔로워 1만, 30일 조회 10만, 국내 19세 이상, 한국 지원 여부 미확인).
→ 30초 포맷은 '성장용'. 계정이 크면 틱톡용 61~90초 버전을 따로 만드는 것을 검토. 당장은 협찬·제휴가 더 현실적.

## 48시간 점검에 추가한 지표 (`tools/review.py`)
- `sends` — 인스타 DM 보내기 수 → **보내기율** (시작 기준 0.5%)
- `viewed_vs_swiped` — 유튜브 쇼츠 '본 비율' % → **스와이프 안 함** (시작 기준 70%)
- 인사이트에 없으면 비워 두면 된다 (미달로 세지 않음). 4주 뒤 내 채널 중앙값으로 기준을 바꾼다.

## 출처
- [Instagram Ranking Explained (공식, 2023)](https://about.instagram.com/blog/announcements/instagram-ranking-explained)
- [TikTok — How TikTok recommends content (공식)](https://support.tiktok.com/en/using-tiktok/exploring-videos/how-tiktok-recommends-content)
- [Kompozy — 모세리의 랭킹 신호](https://kompozy.io/news/instagram-mosseri-ranking-signals-guidance)
- [Tubefilter — 독창적이지 않은 재게시 불이익 (2026-04)](https://tubefilter.com/2026/04/30/instagram-removes-algorithm-recommendations-repost-content-aggregator)
- [Social Media Today — 인스타 해시태그 5개 제한](https://www.socialmediatoday.com/news/instagram-implements-new-limits-on-hashtag-use/808309/)
- [SocialPilot — 2026 릴스 알고리즘 변화](https://www.socialpilot.co/?p=563048)
- [Social Champ — 체험판 릴스](https://www.socialchamp.com/blog/instagram-trial-reels/)
- [Blitzcut — 틱톡 검색 최적화](https://blitzcutai.com/blog/tiktok-seo-guide-2026)
- [OutlierKit — 유튜브의 쇼츠 랭킹 발언](https://outlierkit.com/resources/youtube-shorts-algorithm/)
- [TTCalculator — 틱톡 크리에이터 리워드 조건](https://ttcalculator.net/guides/creator-rewards-program/)
