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
# 있으면 쓰는 칸 (플랫폼 인사이트에 있을 때만 적는다)
#   sends            인스타 'DM으로 보내기' 수 — 비팔로워에게 퍼지는 가장 강한 신호 (모세리)
#   viewed_vs_swiped 유튜브 쇼츠 '본 비율(스와이프하지 않고 본 사람 %)', 0~100
OPTIONAL = ["sends", "viewed_vs_swiped"]

# (이름, 계산, 통과 기준, 미달이면 고칠 곳)
THRESHOLDS = [
    ("3초 유지율", lambda r: r["viewed_3s"] / r["views"], 0.70, "후킹 문장, 첫 장면 3D 진입 속도"),
    ("완주율", lambda r: r["avg_watch_sec"] / TOTAL_SEC, 0.50, "중간 장면 수 줄이기, 정보 3개 → 2개"),
    ("저장률", lambda r: r["saves"] / r["views"], 0.01, "체크리스트 장면 추가, '나중에 볼 이유' CTA"),
    ("공유율", lambda r: r["shares"] / r["views"], 0.005, "'부모님·친구에게' 같은 공유 대상 지목"),
    ("보내기율", lambda r: r["sends"] / r["views"], 0.005, "CTA 에 보낼 사람을 구체적으로 ('카드만 쓰는 회사 동기에게')"),
    ("스와이프 안 함", lambda r: r["viewed_vs_swiped"] / 100, 0.70, "첫 1초에 주제어를 말+자막으로, 후킹 물건을 더 크게"),
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
            for k in OPTIONAL:  # 비어 있으면 '측정 안 함'(None) — 미달로 세지 않는다
                r[k] = float(r[k]) if r.get(k) not in (None, "") else None
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
        except (TypeError, KeyError):  # 선택 칸이 비었거나 없음 → 표에서 빼기
            continue
        out.append((name, v, v >= target, fix))
    return out


def report(rows: list[dict]) -> str:
    names = [t[0] for t in THRESHOLDS if any(n == t[0] for r in rows for n, *_ in grade(r))]
    lines = ["| 편 | 플랫폼 | " + " | ".join(names) + " | 통과 | 판단 |",
             "|---|---|" + "---|" * len(names) + "---|---|"]
    misses: Counter[str] = Counter()
    fixes = {t[0]: t[3] for t in THRESHOLDS}
    for r in rows:
        g = grade(r)
        by = {n: (v, ok) for n, v, ok, _ in g}
        cells = [("" if n not in by else "–" if by[n][0] is None else f"{by[n][0] * 100:.1f}% {'✅' if by[n][1] else '❌'}")
                 for n in names]
        passed = sum(ok for _, _, ok, _ in g)
        for name, _, ok, _ in g:
            if not ok:
                misses[name] += 1
        verdict = "후속편 후보" if passed >= 2 else "개선 필요"
        lines.append(f"| {r['ep']} | {r['platform']} | " + " | ".join(cells) + f" | {passed}/{len(g)} | {verdict} |")
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
