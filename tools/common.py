"""여러 도구가 함께 쓰는 공통 함수.

채널(계정) 하나 = channels/<채널>/ 폴더 하나.
    channels/money/channel.json          채널 설정 (이름·색·3D 소품·배경음·계정·업로드 시간)
    channels/money/episodes/ep01/        한 편 (script.json, factcheck.md, …)
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHANNELS = ROOT / "channels"

DEFAULT_DUR = 2.4  # 설명 장면 길이(초) = 100BPM 한 마디
EDGE_DUR = 3.0  # 후킹·CTA 장면 길이(초) = 100BPM 다섯 박
SCENE_COUNT = 12
TOTAL_SEC = 30.0
SCENE_TYPES = {"hook", "point", "number", "compare", "check", "keys", "cta"}

_MARK = re.compile(r"[\[\]{}]")

# 협찬·광고 표시 (공정위 '추천·보증 심사지침': 경제적 이해관계를 소비자가 쉽게 알 수 있게, 내용과 가까운 곳에)
SPONSOR_KINDS = {
    "paid": ("유료 광고 포함", "[광고]"),            # 돈을 받고 만든 영상
    "gifted": ("협찬 · 제품 제공", "[협찬]"),        # 제품·서비스를 무료로 받음
    "affiliate": ("제휴 링크 · 수수료 받음", "[광고]"),  # 구매 시 수수료 (쿠팡 파트너스, 유튜브 쇼핑 제휴 등)
}
COUPANG_NOTICE = "이 게시물은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다."


def sponsor_label(data: dict) -> tuple[str, str] | None:
    sp = data.get("sponsor")
    return SPONSOR_KINDS.get(sp["kind"]) if sp else None


def list_channels() -> list[str]:
    return sorted(p.name for p in CHANNELS.iterdir() if (p / "channel.json").exists())


def channel_dir(ch: str) -> Path:
    d = CHANNELS / ch
    if not (d / "channel.json").exists():
        raise SystemExit(f"채널 '{ch}' 이 없습니다. 있는 채널: {', '.join(list_channels())}")
    return d


def load_channel(ch: str) -> dict:
    with open(channel_dir(ch) / "channel.json", encoding="utf-8") as f:
        return json.load(f)


def list_episodes(ch: str) -> list[str]:
    return sorted(p.name for p in (channel_dir(ch) / "episodes").glob("ep*") if (p / "script.json").exists())


def episode_dir(ch: str, ep: str) -> Path:
    return channel_dir(ch) / "episodes" / ep


def load_script(ch: str, ep: str) -> dict:
    with open(episode_dir(ch, ep) / "script.json", encoding="utf-8") as f:
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
    """자막 표기([형광펜], {강조 글자})를 지운 순수 문장."""
    return _MARK.sub("", text)


def scene_texts(scene: dict) -> list[str]:
    """화면에 보이는 모든 글자 (사실 확인용)."""
    out: list[str] = []
    for key in ("label", "pre", "big", "sub"):
        if scene.get(key):
            out.append(scene[key])
    out += scene.get("lines", []) + scene.get("title", []) + scene.get("items", [])
    if scene.get("keys"):
        out.append(" + ".join(scene["keys"]))
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
