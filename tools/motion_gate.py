"""완성 영상이 '넘기는 슬라이드(PPT)'처럼 보이는지 숫자로 잰다 — 렌더 후 품질 관문.

    python -m tools.motion_gate channels/why/episodes/ep01/final.mp4
    python -m tools.motion_gate --all            # 모든 채널의 final.mp4

방법과 기준선은 huashu-art-motion(MIT, alchaincyf)의 film_gate 설명을 참고해 numpy 로 다시 짠 것이다:
  1) 빠른 움직임 프레임 비율 — 12fps · 가로 320 회색조에서 이웃 프레임 평균 밝기 차 ≥ 9 인 비율.
     장면 전환(컷) 프레임은 뺀다. < 0.035 빨강, < 0.06 노랑. (그쪽 표본 13편에서 좋은 편은 최저 0.068, 나쁜 편은 최고 0.021)
  2) 가운데 구간의 빈 화면 — 테두리·글자가 거의 없는 프레임이 0.3초 이상 이어지면 빨강.
  3) 파랑-보라 배경 비율 — 색상 225°~300° 픽셀이 30% 넘는 프레임의 비율. ≥ 0.30 빨강, ≥ 0.12 노랑
     ('AI 티 나는 보라·남보라 그라데이션' 방지. 남색·하늘색(약 200~220°)은 해당 안 됨).
기준선은 다른 사람 작품으로 맞춘 경험값이라 '판결'이 아니라 '다시 볼 곳'을 알려 주는 용도다.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

from tools.common import CHANNELS

FPS, WIDTH = 12, 320
FAST_DIFF = 9.0           # 빠른 움직임으로 볼 평균 밝기 차
CUT_DIFF = 40.0           # 이 이상이면 장면 전환(컷)으로 보고 뺀다
SUB_BAND = 0.18           # 아래쪽 자막·캡션 영역은 빼고 본다 (세로 영상)


def probe(path: Path) -> tuple[int, int, float]:
    out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=width,height:format=duration", "-of", "json", str(path)])
    j = json.loads(out)
    return int(j["streams"][0]["width"]), int(j["streams"][0]["height"]), float(j["format"]["duration"])


def frames(path: Path, fps: int, width: int, gray: bool) -> np.ndarray:
    w0, h0, _ = probe(path)
    h = int(round(h0 * width / w0 / 2) * 2)
    fmt, ch = ("gray", 1) if gray else ("rgb24", 3)
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-vf",
                                   f"fps={fps},scale={width}:{h}:flags=area", "-pix_fmt", fmt, "-f", "rawvideo", "-"])
    n = len(raw) // (width * h * ch)
    shape = (n, h, width) if gray else (n, h, width, 3)
    return np.frombuffer(raw[: n * width * h * ch], np.uint8).reshape(shape)


def measure(path: Path) -> dict:
    g = frames(path, FPS, WIDTH, gray=True).astype(np.float32)
    g = g[:, : int(g.shape[1] * (1 - SUB_BAND))]
    diff = np.abs(np.diff(g, axis=0)).mean(axis=(1, 2))
    cuts = diff >= CUT_DIFF
    keep = ~(cuts | np.roll(cuts, 1) | np.roll(cuts, -1))       # 컷 앞뒤 프레임도 뺀다
    fast_ratio = float((diff[keep] >= FAST_DIFF).mean()) if keep.any() else 0.0

    # 빈 화면: 밝기 기울기 > 24 인 픽셀이 0.2% 미만이면 빈 프레임
    gy, gx = np.abs(np.diff(g, axis=1))[:, :, :-1], np.abs(np.diff(g, axis=2))[:, :-1, :]
    edge = ((np.maximum(gx, gy) > 24).mean(axis=(1, 2)))
    blank = edge < 0.002
    lo, hi = int(0.5 * FPS), len(blank) - int(0.5 * FPS)
    run = best = 0
    for b in blank[lo:hi]:
        run = run + 1 if b else 0
        best = max(best, run)

    # 파랑-보라 배경
    rgb = frames(path, 2, 160, gray=False).astype(np.float32) / 255
    mx, mn = rgb.max(axis=3), rgb.min(axis=3)
    d = np.where(mx - mn == 0, 1e-6, mx - mn)
    r, gg, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    hue = np.where(mx == r, (gg - b) / d % 6, np.where(mx == gg, (b - r) / d + 2, (r - gg) / d + 4)) * 60
    sat = np.where(mx == 0, 0, (mx - mn) / np.where(mx == 0, 1, mx))
    bp = (hue >= 225) & (hue <= 300) & (sat >= 0.30) & (mx >= 0.06) & (mx <= 0.90)
    bp_share = float((bp.mean(axis=(1, 2)) >= 0.30).mean())

    return {"fast_ratio": round(fast_ratio, 3), "blank_run_s": round(best / FPS, 2), "blue_purple_share": round(bp_share, 3)}


def verdict(m: dict) -> tuple[str, list[str]]:
    notes, level = [], 0
    if m["fast_ratio"] < 0.035:
        notes.append(f"빠른 움직임 {m['fast_ratio']} < 0.035 → 넘기는 슬라이드처럼 보임"); level = 2
    elif m["fast_ratio"] < 0.06:
        notes.append(f"빠른 움직임 {m['fast_ratio']} < 0.06 → 움직임 보강 검토"); level = max(level, 1)
    if m["blank_run_s"] >= 0.3:
        notes.append(f"빈 화면 {m['blank_run_s']}초 연속"); level = 2
    if m["blue_purple_share"] >= 0.30:
        notes.append(f"파랑-보라 배경 {m['blue_purple_share']} ≥ 0.30"); level = 2
    elif m["blue_purple_share"] >= 0.12:
        notes.append(f"파랑-보라 배경 {m['blue_purple_share']} ≥ 0.12"); level = max(level, 1)
    return ["초록", "노랑", "빨강"][level], notes


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", type=Path)
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args(argv)
    files = sorted(CHANNELS.glob("*/episodes/*/final.mp4")) if a.all else a.files
    if not files:
        ap.error("영상 경로를 주거나 --all")
    red = False
    for f in files:
        m = measure(f)
        light, notes = verdict(m)
        red |= light == "빨강"
        name = "/".join(f.parts[-4:-1]) if "channels" in f.parts else str(f)
        print(f"[{light}] {name}  빠른움직임 {m['fast_ratio']} · 빈화면 {m['blank_run_s']}s · 파랑보라 {m['blue_purple_share']}"
              + ("".join(f"\n    - {n}" for n in notes)))
    return 2 if red else 0


if __name__ == "__main__":
    sys.exit(main())
