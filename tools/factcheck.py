"""대본에서 숫자가 들어간 문구를 뽑아 사실 확인 표(factcheck.md)를 만들고 검사한다.

    python -m tools.factcheck ep01           # 표 만들기/갱신 (이미 적은 출처·확인 표시는 보존)
    python -m tools.factcheck ep01 --check   # 모든 숫자에 출처 URL + ✅ 가 있는지 검사

규칙: 출처 링크가 없는 숫자는 영상에 넣지 않는다. --check 가 실패하면 렌더하지 않는다.
"""
from __future__ import annotations

import argparse
import re
import sys

from tools.common import episode_dir, load_script, plain, scene_texts

HEADER = [
    "# 사실 확인 — {id} {title}",
    "",
    "- 출처는 국세청·법령정보센터·정부 누리집 같은 **공식 출처**를 우선으로 적습니다.",
    "- 확인 칸: 출처 원문을 눈으로 확인했으면 `✅`, 틀렸으면 `❌` 후 대본 수정.",
    "",
    "| # | 장면 | 화면 문구 | 출처 (URL) | 확인 |",
    "|---|---|---|---|---|",
]
_NUMBERING = re.compile(r"^\d{2}\s")  # '01  문턱' 같은 장면 번호 라벨은 제외
_ROW = re.compile(r"^\|\s*\d+\s*\|\s*(\d+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*$")


def claims(data: dict) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    for i, s in enumerate(data["scenes"], 1):
        for text in scene_texts(s):
            t = plain(text).strip()
            if re.search(r"\d", t) and not _NUMBERING.match(t) and (i, t) not in out:
                out.append((i, t))
    return out


def parse_rows(md: str) -> dict[tuple[int, str], tuple[str, str]]:
    rows = {}
    for line in md.splitlines():
        m = _ROW.match(line)
        if m:
            rows[(int(m.group(1)), m.group(2))] = (m.group(3), m.group(4))
    return rows


def build(data: dict, existing: str = "") -> str:
    old = parse_rows(existing)
    lines = [h.format(**data) for h in HEADER]
    for n, (scene, text) in enumerate(claims(data), 1):
        src, ok = old.get((scene, text), ("", "☐"))
        lines.append(f"| {n} | {scene:02d} | {text} | {src} | {ok} |")
    return "\n".join(lines) + "\n"


def problems(md: str) -> list[str]:
    out = []
    for (scene, text), (src, ok) in parse_rows(md).items():
        if not src.startswith("http"):
            out.append(f"장면 {scene:02d} \"{text}\": 출처 URL 없음")
        elif "✅" not in ok:
            out.append(f"장면 {scene:02d} \"{text}\": 아직 확인 안 됨 ({ok or '빈칸'})")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ep")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    data = load_script(a.ep)
    path = episode_dir(a.ep) / "factcheck.md"
    existing = path.read_text(encoding="utf-8") if path.exists() else ""

    if a.check:
        if not existing:
            print(f"{path.name} 이 없습니다. 먼저 `python -m tools.factcheck {a.ep}`")
            return 1
        # 대본이 바뀌어 표에 없는 숫자가 생겼는지도 본다
        missing = [c for c in claims(data) if c not in parse_rows(existing)]
        issues = [f"장면 {s:02d} \"{t}\": 표에 없음 (대본 수정 후 표를 다시 만드세요)" for s, t in missing]
        issues += problems(existing)
        for i in issues:
            print("  ✗", i)
        print(f"[{a.ep}] 사실 확인 {'통과' if not issues else f'미완료 {len(issues)}건'}")
        return 1 if issues else 0

    path.write_text(build(data, existing), encoding="utf-8")
    print(f"{path.relative_to(path.parents[2])} — 숫자 문구 {len(claims(data))}개")
    return 0


if __name__ == "__main__":
    sys.exit(main())
