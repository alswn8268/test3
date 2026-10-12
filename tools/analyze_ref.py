"""잘 된 숏폼(참고 영상)을 숫자로 뜯어본다: 길이 · 컷 속도 · 첫 3초 컷 수 · 음량 · 템포(BPM).

    python -m tools.analyze_ref refs/*.mp4                  # 표로 출력
    python -m tools.analyze_ref refs/*.mp4 --out research/refs-2026-W42.md

참고 영상은 앱의 '저장'이나 화면 녹화로 내 PC에만 두고 분석용으로만 쓴다 (재업로드·편집 사용 금지).
결과의 중앙값을 우리 포맷(장면 2.4초, 100BPM, -14 LUFS)과 비교해 바꿀 점을 찾는다.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
import sys
from pathlib import Path

import numpy as np

OURS = {"shot": 2.4, "bpm": 100, "lufs": -14.0, "dur": 30.0}


def probe(path: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height",
                          "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout
    info = json.loads(out)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), {})
    return {"dur": float(info["format"]["duration"]), "w": v.get("width"), "h": v.get("height"),
            "audio": any(s["codec_type"] == "audio" for s in info["streams"])}


def cuts(path: Path, threshold: float = 0.12) -> list[float]:
    """화면이 크게 바뀌는 순간(컷) 시각 목록."""
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-vf",
                          f"select='gt(scene,{threshold})',showinfo", "-an", "-f", "null", "-"],
                         capture_output=True, text=True, check=False).stderr
    return [float(m) for m in re.findall(r"pts_time:([\d.]+)", err)]


def loudness(path: Path) -> float | None:
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True, check=False).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", err)
    return float(m[-1]) if m else None


def tempo(path: Path, sr: int = 11025) -> float | None:
    """소리 세기 변화의 반복 주기로 BPM 을 어림한다 (70~180 범위)."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True, check=False).stdout
    x = np.frombuffer(raw, dtype=np.float32)
    if len(x) < sr * 5:
        return None
    hop = 64
    frames = len(x) // hop
    env = np.sqrt((x[: frames * hop].reshape(frames, hop) ** 2).mean(axis=1))
    onset = np.maximum(np.diff(env), 0)
    onset -= onset.mean()
    ac = np.correlate(onset, onset, mode="full")[len(onset) - 1:]
    fps = sr / hop
    lags = np.arange(len(ac))
    bpm = 60 * fps / np.maximum(lags, 1)
    ok = (bpm >= 70) & (bpm <= 180)
    if not ok.any():
        return None
    i = int(lags[ok][np.argmax(ac[ok])])
    # 꼭짓점 보간으로 소수 프레임까지 정밀하게
    a, b, c = ac[i - 1], ac[i], ac[i + 1]
    shift = 0.5 * (a - c) / (a - 2 * b + c) if (a - 2 * b + c) != 0 else 0.0
    return round(float(60 * fps / (i + shift)), 1)


def analyze(path: Path) -> dict:
    p = probe(path)
    c = cuts(path)
    shots = np.diff([0.0, *c, p["dur"]])
    return {
        "file": path.name, "dur": round(p["dur"], 1), "vertical": bool(p["h"] and p["w"] and p["h"] > p["w"]),
        "cuts": len(c), "shot": round(float(np.median(shots)), 2) if len(shots) else None,
        "cuts_3s": sum(t < 3 for t in c), "first_cut": round(c[0], 2) if c else None,
        "lufs": loudness(path) if p["audio"] else None, "bpm": tempo(path) if p["audio"] else None,
    }


def report(rows: list[dict]) -> str:
    head = "| 파일 | 길이(초) | 세로 | 컷 수 | 컷 간격 중앙값(초) | 첫 3초 컷 | 첫 컷(초) | 음량(LUFS) | BPM |"
    lines = [head, "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['file']} | {r['dur']} | {'O' if r['vertical'] else 'X'} | {r['cuts']} | {r['shot']} | "
                     f"{r['cuts_3s']} | {r['first_cut']} | {r['lufs']} | {r['bpm']} |")

    def med(key):
        vals = [r[key] for r in rows if r[key] is not None]
        return round(statistics.median(vals), 2) if vals else None

    m = {k: med(k) for k in ("dur", "shot", "cuts_3s", "first_cut", "lufs", "bpm")}
    lines += ["", (f"**중앙값** — 길이 {m['dur']}초 · 컷 간격 {m['shot']}초 · 첫 3초 컷 {m['cuts_3s']}개 · "
                   f"첫 컷 {m['first_cut']}초 · 음량 {m['lufs']} LUFS · {m['bpm']} BPM"), "",
              (f"**우리 포맷** — 길이 {OURS['dur']:g}초 · 장면 {OURS['shot']}초(장면 안에서 글자·3D가 계속 움직임) · "
               f"{OURS['bpm']} BPM · {OURS['lufs']} LUFS"), "", "**바꿔볼 점 (한 번에 하나만)**"]
    tips = []
    if m["shot"] and m["shot"] < OURS["shot"] * 0.7:
        tips.append(f"- 참고 영상의 컷이 더 빠름({m['shot']}초) → 설명 장면 하나를 둘로 나누거나 장면 안 움직임을 늘리기")
    if m["first_cut"] and m["first_cut"] < 2.0:
        tips.append(f"- 첫 컷이 {m['first_cut']}초에 나옴 → 후킹 3초 안에 화면 변화(숫자 확대·3D 등장)를 하나 더")
    if m["dur"] and m["dur"] < OURS["dur"] * 0.75:
        tips.append(f"- 참고 영상이 더 짧음({m['dur']}초) → 정보 3개 → 2개로 줄인 20초 버전 시험")
    if m["lufs"] and m["lufs"] > OURS["lufs"] + 2:
        tips.append(f"- 참고 영상이 더 큼({m['lufs']} LUFS) → 효과음 볼륨을 조금 올려 보기")
    lines += tips or ["- 큰 차이 없음 → 후킹 문장·주제 선정에 집중"]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", type=Path)
    ap.add_argument("--out", type=Path, help="결과를 마크다운 파일로 저장")
    a = ap.parse_args(argv)
    rows = []
    for f in a.files:
        if not f.exists():
            print(f"없음: {f}")
            continue
        rows.append(analyze(f))
        print(f"분석: {f.name}", file=sys.stderr)
    if not rows:
        return 1
    text = report(rows)
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text("# 참고 영상 분석\n\n" + text, encoding="utf-8")
        print(f"저장: {a.out}")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
