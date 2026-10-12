"""업로드 문구 초안(post.md)을 틱톡 · 유튜브 쇼츠 · 인스타그램 릴스 세 곳용으로 만든다.
본문은 /post 스킬에서 Claude가 다듬는다. 업로드(예약 버튼)는 사람이 직접 한다.

    python -m tools.post money ep01 --month 12 --tags 연말정산 직장인 카드공제 체크카드

공통 규칙: 첫 줄 = 후킹 문장 그대로, 둘째 줄 = 저장할 이유, 해시태그 5개 = 넓은 것 2 + 주제 2 + 채널 태그 1.
같은 주제 계정의 세 플랫폼에는 같은 영상(final.mp4 원본)을 올린다 — 다른 플랫폼에서 받은 워터마크 영상은 쓰지 않는다.
"""
from __future__ import annotations

import argparse
import sys

from tools.common import episode_dir, load_channel, load_script, plain


def hook_sentence(data: dict) -> str:
    return " ".join(plain(x) for x in data["scenes"][0]["lines"])


def build(channel: dict, data: dict, month: str, tags: list[str]) -> str:
    tags = [t if t.startswith("#") else f"#{t}" for t in tags][:4]
    tags += ["#TODO"] * (4 - len(tags))
    all_tags = " ".join(tags + [channel["hashtag"]])
    hook = hook_sentence(data)
    save = f"저장해두고 {month}월에 다시 보기" if month != "○" else "저장해두고 다시 보기"
    acc = channel["accounts"]
    times = " · ".join(f"{x['day']} {x['time']}" for x in channel.get("schedule", []))
    return "\n".join([
        f"# 업로드 문구 — {channel['name']} · {data['id']} {data['title']}",
        "",
        "## 공통",
        "- 올릴 파일: `final.mp4` — 세 플랫폼 모두 이 원본 파일 (틱톡에서 받은 워터마크 영상을 릴스·쇼츠에 올리지 않기)",
        "- 커버: `preview/s01.png` (후킹 장면) · 자막 파일: `captions.srt` (유튜브에 올리면 검색에 도움)",
        "- 인기 사운드를 얹을 땐 앱에서 볼륨 10~20%로 (영상 속 배경음이 이미 있음)",
        f"- 이 채널 업로드 시간: {times}",
        "",
        f"## 틱톡 — {acc.get('tiktok') or '(계정 미정)'}",
        hook,
        save,
        all_tags,
        "",
        f"## 유튜브 쇼츠 — {acc.get('youtube') or '(계정 미정)'}",
        f"제목: {data['title']}",
        "설명:",
        hook,
        "(본문 1~2줄: 영상 핵심 + 지금 할 일)",
        " ".join(tags[:2] + [channel["hashtag"]]),
        "",
        f"## 인스타그램 릴스 — {acc.get('instagram') or '(계정 미정)'}",
        hook,
        save,
        "",
        "(본문 2~3줄: 영상 핵심 + 지금 할 일 1개)",
        "",
        all_tags,
        "",
        "## 예약",
        "| 플랫폼 | 날짜 | 시간 | 완료 |",
        "|---|---|---|---|",
        "| 틱톡 (TikTok Studio, 예약 후 수정 불가) |  |  | ☐ |",
        "| 유튜브 쇼츠 (YouTube Studio) |  |  | ☐ |",
        "| 인스타 릴스 (Meta Business Suite) |  |  | ☐ |",
        "",
    ])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("channel")
    ap.add_argument("ep")
    ap.add_argument("--month", default="○", help="다시 볼 달 (예: 12)")
    ap.add_argument("--tags", nargs="*", default=[], help="넓은 것 2 + 주제 2 (# 없이)")
    ap.add_argument("--force", action="store_true", help="이미 있는 post.md 덮어쓰기")
    a = ap.parse_args(argv)
    path = episode_dir(a.channel, a.ep) / "post.md"
    if path.exists() and not a.force:
        print(f"{path.name} 이 이미 있습니다 (--force 로 덮어쓰기)")
        return 1
    path.write_text(build(load_channel(a.channel), load_script(a.channel, a.ep), a.month, a.tags), encoding="utf-8")
    print(f"channels/{a.channel}/episodes/{a.ep}/post.md 작성")
    return 0


if __name__ == "__main__":
    sys.exit(main())
