"""업로드 48시간 뒤 수치(metrics.csv)로 편마다 통과·미달을 매긴다.

    python -m tools.review money          # 한 채널
    python -m tools.review money ep01     # 한 편

기준은 시작용 가설이다. 4주 뒤엔 내 채널 중앙값으로 THRESHOLDS 를 바꾼다.
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

from tools.common import TOTAL_SEC, channel_dir

COLUMNS = ["ep", "platform", "posted_at", "views", "viewed_3s", "avg_watch_sec",
           "saves", "shares", "profile_visits", "follows"]

# (이름, 계산, 통과 기준, 미달이면 고칠 곳)
THRESHOLDS = [
    ("3초 유지율", lambda r: r["viewed_3s"] / r["views"], 0.70, "후킹 문장, 첫 장면 3D 진입 속도"),
    ("완주율", lambda r: r["avg_watch_sec"] / TOTAL_SEC, 0.50, "중간 장면 수 줄이기, 정보 3개 → 2개"),
    ("저장률", lambda r: r["saves"] / r["views"], 0.01, "체크리스트 장면 추가, '나중에 볼 이유' CTA"),
    ("공유율", lambda r: r["shares"] / r["views"], 0.005, "'부모님·친구에게' 같은 공유 대상 지목"),
    ("팔로우 전환", lambda r: r["follows"] / r["profile_visits"], 0.10, "프로필 첫 줄, 시리즈 고정 게시물"),
]


def read_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8", newline="") as f:
        rows = []
        for r in csv.DictReader(f):
            if not r.get("ep"):
                continue
            for k in COLUMNS[3:]:
                r[k] = float(r[k] or 0)
            rows.append(r)
        return rows


def grade(row: dict) -> list[tuple[str, float | None, bool, str]]:
    out = []
    for name, fn, target, fix in THRESHOLDS:
        try:
            v = fn(row)
        except ZeroDivisionError:
            out.append((name, None, False, fix))
            continue
        out.append((name, v, v >= target, fix))
    return out


def report(rows: list[dict]) -> str:
    lines = ["| 편 | 플랫폼 | " + " | ".join(t[0] for t in THRESHOLDS) + " | 통과 | 판단 |",
             "|---|---|" + "---|" * len(THRESHOLDS) + "---|---|"]
    misses: Counter[str] = Counter()
    fixes = {t[0]: t[3] for t in THRESHOLDS}
    for r in rows:
        g = grade(r)
        cells = [("–" if v is None else f"{v * 100:.1f}% {'✅' if ok else '❌'}") for _, v, ok, _ in g]
        passed = sum(ok for _, _, ok, _ in g)
        for name, _, ok, _ in g:
            if not ok:
                misses[name] += 1
        verdict = "후속편 후보" if passed >= 2 else "개선 필요"
        lines.append(f"| {r['ep']} | {r['platform']} | " + " | ".join(cells) + f" | {passed}/5 | {verdict} |")
    if misses:
        worst, n = misses.most_common(1)[0]
        lines += ["", f"**다음 주 고칠 것 1개:** {worst} ({n}편 미달) → {fixes[worst]}"]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("channel")
    ap.add_argument("ep", nargs="?")
    a = ap.parse_args(argv)
    rows = [r for r in read_rows(channel_dir(a.channel) / "metrics.csv") if not a.ep or r["ep"] == a.ep]
    if not rows:
        print("metrics.csv 에 해당 편 수치가 없습니다. 인사이트 수치를 먼저 입력하세요.")
        return 1
    print(report(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
