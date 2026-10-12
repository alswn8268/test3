"""배경음(BGM)과 효과음(SFX)을 코드로 직접 합성한다 → 저작권 걱정 없는 100% 자체 제작 음원.

    python -m tools.audio money ep01            # channels/money/episodes/ep01/audio.wav 만들기
    python -m tools.audio --demo lofi out.wav   # 스타일 들어보기 (lofi · upbeat · bright)

왜 100BPM 인가:  한 박 = 0.6초, 한 마디 = 2.4초.  장면 길이(후킹 3.0초 = 5박, 설명 2.4초 = 1마디)가
전부 박자 위에 떨어져서 컷이 바뀌는 순간이 항상 비트와 맞는다.

효과음 시점은 render/render.html 의 애니메이션 시간표와 같게 맞춘다 (EVENT_TIMES 참고).
"""
from __future__ import annotations

import argparse
import sys
import wave
import zlib
from pathlib import Path

import numpy as np

from tools.common import episode_dir, load_channel, load_script, timeline

SR = 48000
BPM = 100
BEAT = 60 / BPM  # 0.6초
BAR = BEAT * 4  # 2.4초

# render.html 애니메이션과 맞춘 효과음 시점 (장면 시작 기준 초)
EVENT_TIMES = {
    "highlight": (0.35, 0.10),  # 형광펜 k번째: 0.35 + k*0.10
    "check": (0.45, 0.45),  # 체크 k번째: 0.45 + k*0.45
    "key": (0.30, 0.20),  # 키캡 k번째: 0.30 + k*0.20
    "count_end": 0.90,  # 큰 숫자 카운트업이 거의 끝나는 시점
    "stamp": 0.82,  # CTA 도장이 찍히는 시점
}

NOTE = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}

# 스타일별: 코드 진행(조 기준 반음), 드럼 패턴, 음색
STYLES = {
    # 따뜻한 로파이: 메이저7 코드, 느슨한 스윙, 바이닐 잡음
    "lofi": {"keys": ["F", "D", "G", "A#"], "prog": [[0, 4, 7, 11], [9, 12, 16, 19], [2, 5, 9, 12], [7, 11, 14, 17]],
             "kick": [0, 2.5], "snare": [1, 3], "hat": 8, "swing": 0.12, "pad": 0.22, "pluck": 0.10,
             "bell": 0.0, "crackle": 0.012, "bright": 2400},
    # 경쾌한 업비트: 4박 킥, 엇박 하이햇, 통통 튀는 아르페지오
    "upbeat": {"keys": ["C", "D", "E", "G"], "prog": [[0, 4, 7], [7, 11, 14], [9, 12, 16], [5, 9, 12]],
               "kick": [0, 1, 2, 3], "snare": [1, 3], "hat": 16, "swing": 0.0, "pad": 0.10, "pluck": 0.18,
               "bell": 0.0, "crackle": 0.0, "bright": 6000},
    # 호기심·미스터리: 단조 코드, 통통 튀는 플럭 + 벨, 가벼운 킥 ("어? 왜지?" 느낌)
    "mystery": {"keys": ["A", "E", "D", "C"], "prog": [[0, 3, 7], [8, 12, 15], [3, 7, 10], [10, 14, 17]],
                "kick": [0, 2.5], "snare": [1, 3], "hat": 8, "swing": 0.06, "pad": 0.12, "pluck": 0.13,
                "bell": 0.08, "crackle": 0.0, "bright": 5000},
    # 밝은 팝: 박수, 벨 소리 멜로디
    "bright": {"keys": ["D", "E", "F", "A"], "prog": [[5, 9, 12], [7, 11, 14], [4, 7, 11], [9, 12, 16]],
               "kick": [0, 1.5, 2], "snare": [1, 3], "hat": 8, "swing": 0.0, "pad": 0.14, "pluck": 0.0,
               "bell": 0.14, "crackle": 0.0, "bright": 7000},
}


# ---------------------------------------------------------------- 기본 재료
def _t(sec: float) -> np.ndarray:
    return np.arange(int(sec * SR)) / SR


def _hz(midi: float) -> float:
    return 440.0 * 2 ** ((midi - 69) / 12)


def _env(n: int, attack: float, decay: float) -> np.ndarray:
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    return a * np.exp(-np.maximum(t - attack, 0) / decay)


def _filter(x: np.ndarray, low: float = 0, high: float = SR / 2) -> np.ndarray:
    """주파수 영역에서 자르는 간단한 필터 (low~high 만 남김)."""
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    gain = np.ones_like(f)
    if low > 0:
        gain *= 1 / (1 + (low / np.maximum(f, 1)) ** 4)
    if high < SR / 2:
        gain *= 1 / (1 + (f / high) ** 4)
    return np.fft.irfft(spec * gain, n=len(x))


def _add(buf: np.ndarray, sound: np.ndarray, at: float, gain: float = 1.0, pan: float = 0.0) -> None:
    """buf(스테레오)에 sound(모노)를 at 초 위치에 더한다. pan: -1 왼쪽 ~ 1 오른쪽."""
    i = int(at * SR)
    if i >= len(buf) or i + len(sound) <= 0:
        return
    s = sound[max(0, -i):]
    i = max(i, 0)
    s = s[: len(buf) - i]
    buf[i:i + len(s), 0] += s * gain * (1 - max(pan, 0))
    buf[i:i + len(s), 1] += s * gain * (1 + min(pan, 0))


# ---------------------------------------------------------------- 악기
def kick() -> np.ndarray:
    t = _t(0.35)
    freq = 45 + 85 * np.exp(-t / 0.03)
    return np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-t / 0.12)


def snare(rng: np.random.Generator, clap: bool = False) -> np.ndarray:
    t = _t(0.25)
    noise = _filter(rng.standard_normal(len(t)), 1200, 9000) * np.exp(-t / (0.09 if clap else 0.06))
    body = 0.0 if clap else np.sin(2 * np.pi * 185 * t) * np.exp(-t / 0.04) * 0.6
    return (noise * 0.8 + body)


def hat(rng: np.random.Generator) -> np.ndarray:
    t = _t(0.06)
    return _filter(rng.standard_normal(len(t)), 7000) * np.exp(-t / 0.015)


def tone(midi: float, sec: float, harmonics=(1.0, 0.5, 0.25), attack=0.01, decay=0.4, detune=0.0) -> np.ndarray:
    t = _t(sec)
    f = _hz(midi)
    x = sum(a * np.sin(2 * np.pi * f * (k + 1) * (1 + detune) * t) for k, a in enumerate(harmonics))
    return x * _env(len(t), attack, decay)


# ---------------------------------------------------------------- 배경음
def render_bgm(style: str, seed: int, duration: float) -> np.ndarray:
    st = STYLES[style]
    rng = np.random.default_rng(seed)
    root = 48 + NOTE[st["keys"][seed % len(st["keys"])]]  # 조성은 시드로 고른다 → 편마다 조금씩 다름
    bars = int(np.ceil(duration / BAR)) + 1
    buf = np.zeros((int((bars * BAR + 1) * SR), 2))
    k, sn, ht = kick(), snare(rng, clap=style == "bright"), hat(rng)
    arp_order = rng.permutation(4)

    for b in range(bars):
        t0 = b * BAR
        chord = st["prog"][b % len(st["prog"])]
        intro = b == 0  # 첫 마디(후킹)는 드럼을 가볍게 → 1마디 뒤 '쿵' 하고 본격 시작
        for beat in st["kick"]:
            _add(buf, k, t0 + beat * BEAT, 0.9 if not intro else 0.5)
        if not intro:
            for beat in st["snare"]:
                _add(buf, sn, t0 + beat * BEAT, 0.35, 0.05)
        steps = st["hat"]
        step = BAR / steps
        for i in range(steps):
            at = t0 + i * step + (st["swing"] * step if i % 2 else 0)
            _add(buf, ht, at, (0.10 if i % 2 else 0.06) * (0.5 if intro else 1), 0.3)
        # 베이스: 마디 첫 박과 셋째 박
        for beat, n in ((0, chord[0]), (2, chord[0] if b % 2 else chord[0] + 7)):
            _add(buf, tone(root - 12 + n, BEAT * 1.8, (1.0, 0.35), 0.005, 0.35), t0 + beat * BEAT, 0.32)
        # 패드: 코드 전체를 길게
        if st["pad"]:
            pad = sum(tone(root + 12 + n, BAR, (1.0, 0.3, 0.12), 0.25, 3.0, d)
                      for n in chord for d in (-0.003, 0.003))
            _add(buf, pad / len(chord), t0, st["pad"], 0.0)
        # 아르페지오(플럭) / 벨 멜로디
        if st["pluck"]:
            for i in range(8):
                n = chord[arp_order[i % 4] % len(chord)] + (12 if i >= 4 else 0)
                _add(buf, tone(root + 12 + n, 0.4, (1.0, 0.6, 0.3, 0.15), 0.003, 0.12),
                      t0 + i * BEAT / 2, st["pluck"], -0.35 if i % 2 else 0.35)
        if st["bell"]:
            for i in rng.choice(8, size=4, replace=False):
                n = chord[int(rng.integers(len(chord)))] + 24
                _add(buf, tone(root + n, 0.9, (1.0, 0.0, 0.35, 0.0, 0.12), 0.002, 0.35),
                      t0 + i * BEAT / 2, st["bell"], 0.4 if i % 2 else -0.4)

    if st["crackle"]:
        n = len(buf)
        pops = (rng.random(n) > 0.9993) * rng.standard_normal(n)
        buf += (_filter(rng.standard_normal(n), 300, 3000) * 0.15 + pops)[:, None] * st["crackle"]
    for ch in range(2):
        buf[:, ch] = _filter(buf[:, ch], 30, st["bright"])
    out = buf[: int(duration * SR)]
    # 마지막 1.2초 페이드아웃
    fade = int(1.2 * SR)
    out[-fade:] *= np.linspace(1, 0, fade)[:, None]
    return out / (np.abs(out).max() + 1e-9) * 0.5


# ---------------------------------------------------------------- 효과음
def sfx(name: str, rng: np.random.Generator) -> np.ndarray:
    if name == "whoosh":  # 장면 전환
        t = _t(0.38)
        env = np.sin(np.pi * np.clip(t / 0.38, 0, 1)) ** 2
        return _filter(rng.standard_normal(len(t)), 600, 5000) * env * 0.6
    if name == "pop":  # 형광펜
        t = _t(0.09)
        f = 700 + 900 * (t / 0.09)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.03)
    if name == "tick":  # 체크박스
        t = _t(0.05)
        return (np.sin(2 * np.pi * 2100 * t) * 0.7 + _filter(rng.standard_normal(len(t)), 2000) * 0.4) * np.exp(-t / 0.01)
    if name == "key":  # 키보드 딸깍
        t = _t(0.06)
        return (_filter(rng.standard_normal(len(t)), 2500, 7000) * np.exp(-t / 0.006)
                + np.sin(2 * np.pi * 380 * t) * np.exp(-t / 0.012) * 0.5)
    if name == "ding":  # 숫자 완성
        return tone(91, 0.7, (1.0, 0.0, 0.3, 0.0, 0.1), 0.002, 0.25) * 0.6
    if name == "roll":  # 카운트업 '드르륵'
        out = np.zeros(int(0.75 * SR))
        for i, at in enumerate(np.cumsum(np.linspace(0.04, 0.11, 10))):
            s = sfx("tick", rng) * (0.25 + 0.04 * i)
            j = int(at * SR)
            out[j:j + len(s)] += s[: len(out) - j]
        return out
    if name == "stamp":  # CTA 도장
        t = _t(0.35)
        return (np.sin(2 * np.pi * 68 * t) * np.exp(-t / 0.09)
                + _filter(rng.standard_normal(len(t)), 100, 2500) * np.exp(-t / 0.03) * 0.7)
    if name == "impact":  # 후킹 첫 타격
        t = _t(0.8)
        return (np.sin(2 * np.pi * np.cumsum(40 + 60 * np.exp(-t / 0.05)) / SR) * np.exp(-t / 0.25)
                + _filter(rng.standard_normal(len(t)), 200, 4000) * np.exp(-t / 0.04) * 0.5)
    raise ValueError(name)


def _highlights(scene: dict) -> int:
    texts = scene.get("lines", []) + scene.get("title", []) + [scene.get("sub", ""), scene.get("pre", "")]
    texts += scene.get("items", [])
    return sum(t.count("[") for t in texts)


def sfx_events(scenes: list[dict]) -> list[tuple[float, str, float]]:
    """(시각, 효과음 이름, 볼륨) 목록. render.html 시간표와 맞춘다."""
    ev: list[tuple[float, str, float]] = []
    hl0, hld = EVENT_TIMES["highlight"]
    for i, (s, (t0, _)) in enumerate(zip(scenes, timeline(scenes))):
        if i == 0:
            ev.append((0.0, "impact", 0.55))
        else:
            ev.append((t0 - 0.30, "whoosh", 0.3))
        for k in range(_highlights(s)):
            ev.append((t0 + hl0 + k * hld, "pop", 0.35))
        if s["type"] == "number":
            ev += [(t0 + 0.15, "roll", 0.5), (t0 + EVENT_TIMES["count_end"], "ding", 0.45)]
        if s["type"] == "check":
            c0, cd = EVENT_TIMES["check"]
            ev += [(t0 + c0 + k * cd, "tick", 0.6) for k in range(len(s.get("items", [])))]
        if s["type"] == "keys":
            k0, kd = EVENT_TIMES["key"]
            ev += [(t0 + k0 + k * kd, "key", 0.8) for k in range(len(s.get("keys", [])))]
        if s["type"] == "cta":
            ev.append((t0 + EVENT_TIMES["stamp"], "stamp", 0.9))
    return ev


def mix(scenes: list[dict], style: str, seed: int, bgm_gain: float = 0.55) -> np.ndarray:
    total = sum(s["dur"] for s in scenes)
    out = render_bgm(style, seed, total) * bgm_gain
    rng = np.random.default_rng(seed + 1)
    cache: dict[str, np.ndarray] = {}
    for at, name, gain in sfx_events(scenes):
        if name not in cache:
            cache[name] = sfx(name, rng)
        _add(out, cache[name], at, gain * 0.5, 0.15 if name == "pop" else 0.0)
    peak = np.abs(out).max()
    return out / peak * 0.89 if peak > 0.89 else out


def write_wav(path: Path, x: np.ndarray) -> None:
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def episode_seed(channel: dict, ep: str) -> int:
    """채널 기본 시드 + 편 번호 → 편마다 조성·멜로디가 달라진다 (같은 곡 반복 방지)."""
    return int(channel["bgm"]["seed"]) + zlib.crc32(ep.encode()) % 1000


def build_episode_audio(ch: str, ep: str) -> Path:
    channel = load_channel(ch)
    scenes = load_script(ch, ep)["scenes"]
    path = episode_dir(ch, ep) / "audio.wav"
    write_wav(path, mix(scenes, channel["bgm"]["style"], episode_seed(channel, ep)))
    return path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("channel", nargs="?")
    ap.add_argument("ep", nargs="?")
    ap.add_argument("--demo", nargs=2, metavar=("STYLE", "OUT"), help="BGM만 30초 만들어 듣기")
    a = ap.parse_args(argv)
    if a.demo:
        write_wav(Path(a.demo[1]), render_bgm(a.demo[0], 1, 30.0))
        print(f"{a.demo[1]} ({a.demo[0]}, 30초)")
        return 0
    if not (a.channel and a.ep):
        ap.error("채널과 편을 주세요 (예: money ep01)")
    path = build_episode_audio(a.channel, a.ep)
    print(f"{path.relative_to(path.parents[4])} 생성")
    return 0


if __name__ == "__main__":
    sys.exit(main())
