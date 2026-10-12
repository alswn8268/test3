"""script.json 이 CLAUDE.md 의 대본·디자인 규칙을 지키는지 검사한다.

    python -m tools.validate ep01          # 한 편
    python -m tools.validate --all         # 전체

오류(ERROR)가 하나라도 있으면 종료코드 1 → 렌더 전에 반드시 고친다.
경고(WARN)는 화면이 넘칠 수 있다는 신호라 미리보기 PNG로 눈으로 확인한다.
"""
from __future__ import annotations

import argparse
import sys

from tools.common import EDGE_DUR, EPISODES, SCENE_COUNT, SCENE_TYPES, TOTAL_SEC, load_script, plain

MAX_LINE_CHARS = 9  # 제목 자막 한 줄 최대 글자 수 (공백 제외)

REQUIRED = {
    "hook": ("lines",),
    "point": ("lines",),
    "cta": ("lines",),
    "number": ("big", "pre", "sub"),
    "compare": ("left", "right"),
    "check": ("label", "items"),
}


def check(data: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warns: list[str] = []
    scenes = data.get("scenes", [])
    for key in ("id", "series", "title"):
        if not data.get(key):
            errors.append(f"'{key}' 가 비어 있음")

    if len(scenes) != SCENE_COUNT:
        errors.append(f"장면 수 {len(scenes)}개 (규칙: {SCENE_COUNT}개)")
    total = round(sum(s.get("dur", 0) for s in scenes), 2)
    if abs(total - TOTAL_SEC) > 0.01:
        errors.append(f"총 길이 {total}초 (규칙: {TOTAL_SEC:g}초)")
    if scenes and scenes[0].get("type") != "hook":
        errors.append("첫 장면은 hook 이어야 함")
    if scenes and scenes[-1].get("type") != "cta":
        errors.append("마지막 장면은 cta 여야 함")

    for i, s in enumerate(scenes, 1):
        tag = f"장면 {i:02d}({s.get('type')})"
        t = s.get("type")
        if t not in SCENE_TYPES:
            errors.append(f"{tag}: 알 수 없는 type")
            continue
        for key in REQUIRED[t]:
            if not s.get(key):
                errors.append(f"{tag}: '{key}' 없음")
        if not s.get("say"):
            errors.append(f"{tag}: 내레이션 'say' 없음")
        if t in ("hook", "cta") and abs(s.get("dur", 0) - EDGE_DUR) > 0.01:
            warns.append(f"{tag}: 후킹·CTA 는 {EDGE_DUR:g}초 권장 (지금 {s.get('dur')}초)")

        for line in s.get("lines", []):
            n = len(plain(line).replace(" ", ""))
            if n > MAX_LINE_CHARS:
                warns.append(f"{tag}: 한 줄 {n}글자 > {MAX_LINE_CHARS} → 화면 넘침 확인: \"{plain(line)}\"")

        visible = " ".join(s.get("lines", []) + [s.get("sub", ""), s.get("pre", "")] + s.get("items", []))
        n_hl = visible.count("[")
        if n_hl > 1:
            warns.append(f"{tag}: 형광펜 강조 {n_hl}개 (규칙: 장면당 1개)")
        if visible.count("[") != visible.count("]") or visible.count("{") != visible.count("}"):
            errors.append(f"{tag}: 괄호 [ ] 또는 {{ }} 짝이 맞지 않음")
    return errors, warns


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("eps", nargs="*", help="ep01 ep02 …")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args(argv)
    eps = sorted(p.name for p in EPISODES.glob("ep*") if (p / "script.json").exists()) if a.all else a.eps
    if not eps:
        ap.error("편 번호를 주거나 --all 을 쓰세요")

    failed = 0
    for ep in eps:
        errors, warns = check(load_script(ep))
        status = "통과" if not errors else "실패"
        print(f"[{ep}] {status} — 오류 {len(errors)} · 경고 {len(warns)}")
        for e in errors:
            print(f"  ERROR {e}")
        for w in warns:
            print(f"  WARN  {w}")
        failed += bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
