"""새 계정(채널) 폴더를 만든다. 색·음악·소품은 기존 채널과 겹치지 않게 고른다.

    python -m tools.new_channel cook "자취 요리 3분" --signal "#E8A100" --bgm bright --hashtag 자취요리3분
"""
from __future__ import annotations

import argparse
import sys

from tools.audio import STYLES
from tools.common import CHANNELS, list_channels, load_channel, save_json


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug", help="영문 폴더 이름 (예: cook)")
    ap.add_argument("name", help="화면 워드마크 = 계정 이름")
    ap.add_argument("--signal", required=True, help="신호색 (#RRGGBB) — 먹색 글자가 위에 올라가도 읽히는 중간 밝기")
    ap.add_argument("--bgm", choices=sorted(STYLES), required=True)
    ap.add_argument("--hashtag", required=True, help="채널 고유 해시태그 (# 없이)")
    a = ap.parse_args(argv)

    if (CHANNELS / a.slug).exists():
        ap.error(f"이미 있는 채널: {a.slug}")
    others = [load_channel(ch) for ch in list_channels()]
    if any(o["colors"]["signal"].lower() == a.signal.lower() for o in others):
        ap.error("다른 채널과 같은 신호색입니다 — 계정마다 색을 다르게")
    seed = max((o["bgm"]["seed"] for o in others), default=0) + 17
    d = CHANNELS / a.slug
    save_json(d / "channel.json", {
        "slug": a.slug, "name": a.name, "concept": "TODO: 누구에게 무엇을 (한 줄)", "voice": "TODO: 말투",
        "pillars": ["TODO"] * 5,
        "colors": {"paper": "#EEEDE8", "ink": "#151513", "signal": a.signal},
        "props": {"hero": "card", "stack": "keycap", "point": ["card", "receipt", "keycap"]},
        "bgm": {"style": a.bgm, "seed": seed},
        "hashtag": f"#{a.hashtag}", "broad_tags": ["TODO", "TODO"],
        "factcheck": "required", "factcheck_scope": "every_scene", "official_sources": [],
        "accounts": {"instagram": "", "tiktok": "", "youtube": ""},
        "schedule": [{"day": "월", "time": "12:00"}],
    })
    (d / "episodes").mkdir()
    (d / "topics").mkdir()
    (d / "topics" / ".gitkeep").touch()
    (d / "metrics.csv").write_text(
        "ep,platform,posted_at,views,viewed_3s,avg_watch_sec,saves,shares,profile_visits,follows,sends,viewed_vs_swiped\n", encoding="utf-8")
    (d / "learnings.md").write_text(f"# {a.name} — 배운 것 (최신이 위)\n", encoding="utf-8")
    (d / "backlog.md").write_text(f"# {a.name} — 주제 백로그\n", encoding="utf-8")
    print(f"channels/{a.slug}/ 생성 — channel.json 의 TODO 를 채우세요")
    return 0


if __name__ == "__main__":
    sys.exit(main())
