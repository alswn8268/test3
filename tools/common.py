"""여러 도구가 함께 쓰는 공통 함수 (표준 라이브러리만 사용)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EPISODES = ROOT / "episodes"

DEFAULT_DUR = 2.4  # 설명 장면 길이(초)
EDGE_DUR = 3.0  # 후킹·CTA 장면 길이(초)
SCENE_COUNT = 12
TOTAL_SEC = 30.0
SCENE_TYPES = {"hook", "point", "number", "compare", "check", "cta"}

_MARK = re.compile(r"[\[\]{}]")


def episode_dir(ep: str) -> Path:
    """'ep01' 또는 'episodes/ep01' 둘 다 받는다."""
    p = Path(ep)
    return p if p.is_dir() else EPISODES / p.name


def load_script(ep: str) -> dict:
    path = episode_dir(ep) / "script.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for s in data["scenes"]:
        s.setdefault("dur", DEFAULT_DUR)
    return data


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def plain(text: str) -> str:
    """자막 표기([형광펜], {빨간 글자})를 지운 순수 문장."""
    return _MARK.sub("", text)


def scene_texts(scene: dict) -> list[str]:
    """화면에 보이는 모든 글자 (숫자 사실 확인용)."""
    out: list[str] = []
    for key in ("label", "pre", "big", "sub"):
        if scene.get(key):
            out.append(scene[key])
    out += scene.get("lines", []) + scene.get("items", [])
    for key in ("left", "right"):
        if scene.get(key):
            out.append(" ".join(scene[key]))
    return out


def timeline(scenes: list[dict]) -> list[tuple[float, float]]:
    """장면마다 (시작초, 끝초)."""
    t, out = 0.0, []
    for s in scenes:
        out.append((t, t + s["dur"]))
        t += s["dur"]
    return out
