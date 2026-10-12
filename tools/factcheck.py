"""대본에서 숫자가 들어간 문구를 뽑아 사실 확인 표(factcheck.md)를 만들고 검사한다.

    python -m tools.factcheck money ep01           # 표 만들기/갱신 (이미 적은 출처·확인 표시는 보존)
    python -m tools.factcheck money ep01 --check   # 모든 숫자에 출처 URL + ✅ 가 있는지 검사

규칙: 출처 링크가 없는 숫자는 영상에 넣지 않는다. --check 가 실패하면 렌더하지 않는다.
"""
from __future__ import annotations

import argparse
import re
import sys

from tools.common import episode_dir, load_channel, load_script, plain, scene_texts

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


def claims(data: dict, scope: str = "numbers") -> list[tuple[int, str]]:
    """확인할 문구 목록.
    scope="numbers"     숫자가 든 문구 + 단축키 (금융·단축키 채널)
    scope="every_scene" 후킹·CTA 를 뺀 모든 장면의 화면 문구 한 줄씩 (맞춤법처럼 '규칙'이 사실인 채널)
    """
    out: list[tuple[int, str]] = []
    for i, s in enumerate(data["scenes"], 1):
        if scope == "every_scene":
            if s["type"] not in ("hook", "cta"):
                t = " / ".join(plain(x).strip() for x in scene_texts(s) if not _NUMBERING.match(plain(x)))
                out.append((i, t.replace("|", "/")))
            continue
        for text in scene_texts(s):
            t = plain(text).strip().replace("|", "/")
            is_keys = bool(s.get("keys")) and t == " + ".join(s["keys"])
            if (is_keys or re.search(r"\d", t)) and not _NUMBERING.match(t) and (i, t) not in out:
                out.append((i, t))
    return out


def parse_rows(md: str) -> dict[tuple[int, str], tuple[str, str]]:
    rows = {}
    for line in md.splitlines():
        m = _ROW.match(line)
        if m:
            rows[(int(m.group(1)), m.group(2))] = (m.group(3), m.group(4))
    return rows


def build(data: dict, existing: str = "", scope: str = "numbers") -> str:
    old = parse_rows(existing)
    lines = [h.format(**data) for h in HEADER]
    for n, (scene, text) in enumerate(claims(data, scope), 1):
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


# Claude 가 ✅ 를 찍을 때의 기준 (사람이 Claude 에게 위임한 경우)
#   확인 칸 형식:  ✅ Claude: "출처 원문에서 그대로 옮긴 문장"
#   출처는 공식 도메인만 (정부·공공기관 .go.kr/.gov, 대학, 채널 official_sources)
OFFICIAL_SUFFIXES = (".go.kr", ".gov", ".ac.kr", ".edu", ".or.kr")


def host(url: str) -> str:
    return url.split("//", 1)[-1].split("/", 1)[0].lower().removeprefix("www.")


def official(url: str, extra: list[str]) -> bool:
    h = host(url)
    allowed = {host(u) for u in extra}
    return h.endswith(OFFICIAL_SUFFIXES) or any(h == a or h.endswith("." + a) for a in allowed)


def claude_problems(md: str, official_sources: list[str]) -> list[str]:
    """Claude 가 찍은 ✅ 는 공식 출처 + 원문 인용이 있어야 인정한다."""
    out = []
    for (scene, text), (src, ok) in parse_rows(md).items():
        tag = f"장면 {scene:02d} \"{text[:30]}\""
        if "✅" not in ok:
            continue
        if "Claude" in ok and not re.search(r'Claude:\s*["“].{8,}["”]', ok):
            out.append(f"{tag}: Claude ✅ 에 원문 인용이 없음")
        if "Claude" in ok and not official(src, official_sources):
            out.append(f"{tag}: 공식 출처가 아님 ({host(src)})")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("channel")
    ap.add_argument("ep")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    data = load_script(a.channel, a.ep)
    scope = load_channel(a.channel).get("factcheck_scope", "numbers")
    path = episode_dir(a.channel, a.ep) / "factcheck.md"
    existing = path.read_text(encoding="utf-8") if path.exists() else ""

    if a.check:
        if not existing:
            print(f"{path.name} 이 없습니다. 먼저 `python -m tools.factcheck {a.channel} {a.ep}`")
            return 1
        # 대본이 바뀌어 표에 없는 숫자가 생겼는지도 본다
        missing = [c for c in claims(data, scope) if c not in parse_rows(existing)]
        issues = [f"장면 {s:02d} \"{t}\": 표에 없음 (대본 수정 후 표를 다시 만드세요)" for s, t in missing]
        issues += problems(existing)
        for i in issues:
            print("  ✗", i)
        print(f"[{a.channel}/{a.ep}] 사실 확인 {'통과' if not issues else f'미완료 {len(issues)}건'}")
        return 1 if issues else 0

    path.write_text(build(data, existing, scope), encoding="utf-8")
    print(f"{path.relative_to(path.parents[4])} — 확인할 문구 {len(claims(data, scope))}개")
    return 0


if __name__ == "__main__":
    sys.exit(main())
