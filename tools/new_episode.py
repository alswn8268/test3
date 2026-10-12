"""다음 번호의 에피소드 폴더와 12장면 빈 대본(script.json)을 만든다.

    python -m tools.new_episode "연말정산 미리보기 쓰는 법" --series "시즌 · 연말정산" --slug preview
"""
from __future__ import annotations

import argparse
import sys

from tools.common import DEFAULT_DUR, EDGE_DUR, EPISODES, save_json

# 3초 후킹 → 정보 3개(장면 9개) → 지금 할 일 → CTA
SKELETON = (["hook"] + ["point", "point", "number"] * 3 + ["check", "cta"])[:12]


def next_number() -> int:
    nums = [int(p.name[2:4]) for p in EPISODES.glob("ep[0-9][0-9]*") if p.name[2:4].isdigit()]
    return max(nums, default=0) + 1


def template(ep_id: str, series: str, title: str) -> dict:
    scenes = []
    for t in SKELETON:
        s: dict = {"type": t, "dur": EDGE_DUR if t in ("hook", "cta") else DEFAULT_DUR}
        if t in ("hook", "point", "cta"):
            s["lines"] = ["TODO", "[TODO]"]
            s["sub"] = "TODO"
        if t == "point":
            s["label"] = "TODO"
        if t == "number":
            s.update(big="0", pre="TODO", sub="TODO")
        if t == "check":
            s.update(label="지금 할 일", items=["TODO", "TODO", "TODO"])
        s.update(say="TODO", visual="TODO")
        scenes.append(s)
    return {"id": ep_id, "series": series, "title": title, "status": "draft", "scenes": scenes}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("title")
    ap.add_argument("--series", required=True, help="예: '시즌 · 연말정산', '상시 · 통장 관리'")
    ap.add_argument("--slug", required=True, help="영문 짧은 이름 (예: irp)")
    a = ap.parse_args(argv)
    n = next_number()
    d = EPISODES / f"ep{n:02d}"
    save_json(d / "script.json", template(f"ep{n:02d}_{a.slug}", a.series, a.title))
    print(f"episodes/{d.name}/script.json 생성 — TODO 를 채우세요")
    return 0


if __name__ == "__main__":
    sys.exit(main())
