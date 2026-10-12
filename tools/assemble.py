"""장면 클립을 이어 붙이고 배경음·효과음을 깔아 final.mp4 와 자막 파일 captions.srt 를 만든다.

    python -m tools.assemble money ep01                          # 자체 합성 BGM + 효과음 (기본)
    python -m tools.assemble money ep01 --bgm assets/bgm/a.mp3   # 외부 무료 음원 + 효과음
    python -m tools.assemble money ep01 --silent                 # 무음 (앱에서 인기 사운드를 얹을 때)

외부 음원을 쓸 때는 assets/bgm/LICENSES.md 에 출처·라이선스를 먼저 적는다.
최종 음량은 숏폼 플랫폼 권장 수준(약 -14 LUFS, 최대 -1.5 dBTP)으로 맞춘다.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from tools import audio
from tools.common import episode_dir, load_channel, load_script, timeline


def srt_time(sec: float) -> str:
    ms = round(sec * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build_srt(scenes: list[dict]) -> str:
    """장면마다 내레이션(say)을 자막 한 덩어리로."""
    blocks = []
    for n, (s, (t0, t1)) in enumerate(zip(scenes, timeline(scenes)), 1):
        blocks.append(f"{n}\n{srt_time(t0)} --> {srt_time(t1)}\n{s['say']}\n")
    return "\n".join(blocks)


LOUDNESS = "loudnorm=I=-14:TP=-2:LRA=11,alimiter=limit=0.79:level=disabled"


def ffmpeg_cmd(list_file: Path, out: Path, total: float, mix_wav: Path | None, bgm: Path | None) -> list[str]:
    """mix_wav = 자체 합성 음원(BGM+효과음 또는 효과음만), bgm = 외부 음원(있으면 효과음 밑에 깐다)."""
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(list_file)]
    fade = max(total - 1.2, 0)
    if mix_wav is None:
        # 무음 트랙 (일부 플랫폼은 오디오 없는 영상을 싫어함)
        cmd += ["-f", "lavfi", "-t", f"{total}", "-i", "anullsrc=r=48000:cl=stereo"]
        audio_map = ["-map", "0:v", "-map", "1:a"]
    elif bgm is None:
        cmd += ["-i", str(mix_wav), "-filter_complex", f"[1:a]{LOUDNESS}[a]"]
        audio_map = ["-map", "0:v", "-map", "[a]"]
    else:
        cmd += ["-i", str(mix_wav), "-stream_loop", "-1", "-i", str(bgm), "-filter_complex",
                (f"[2:a]atrim=0:{total},afade=t=out:st={fade}:d=1.2,volume=0.55[b];"
                 f"[1:a][b]amix=inputs=2:duration=first:normalize=0,{LOUDNESS}[a]")]
        audio_map = ["-map", "0:v", "-map", "[a]"]
    return cmd + audio_map + ["-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{total}",
                              "-movflags", "+faststart", str(out)]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("channel")
    ap.add_argument("ep")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--bgm", type=Path, help="외부 무료 음원 파일 (라이선스 기록 필수)")
    g.add_argument("--silent", action="store_true", help="음악·효과음 없이")
    a = ap.parse_args(argv)

    d = episode_dir(a.channel, a.ep)
    scenes = load_script(a.channel, a.ep)["scenes"]
    clips = [d / "clips" / f"s{i:02d}.mp4" for i in range(1, len(scenes) + 1)]
    missing = [c.name for c in clips if not c.exists()]
    if missing:
        print(f"클립이 없습니다: {', '.join(missing)} → 먼저 `node render/capture.mjs {a.channel} {a.ep}`")
        return 1
    if not shutil.which("ffmpeg"):
        print("ffmpeg 가 설치되어 있지 않습니다.")
        return 1
    if a.bgm and not a.bgm.exists():
        print(f"음원 파일이 없습니다: {a.bgm}")
        return 1

    (d / "captions.srt").write_text(build_srt(scenes), encoding="utf-8")
    total = sum(s["dur"] for s in scenes)
    mix_wav = None
    if not a.silent:
        channel = load_channel(a.channel)
        mix_wav = d / "audio.wav"
        gain = 0.0 if a.bgm else 0.55  # 외부 음원을 쓰면 합성 BGM은 빼고 효과음만
        audio.write_wav(mix_wav, audio.mix(scenes, channel["bgm"]["style"], audio.episode_seed(channel, a.ep), gain))
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.writelines(f"file '{c.resolve()}'\n" for c in clips)
        list_file = Path(f.name)
    try:
        subprocess.run(ffmpeg_cmd(list_file, d / "final.mp4", total, mix_wav, a.bgm), check=True)
    finally:
        list_file.unlink(missing_ok=True)
    sound = "무음" if a.silent else (f"외부 음원 {a.bgm.name} + 효과음" if a.bgm else "자체 합성 BGM + 효과음")
    print(f"완성: channels/{a.channel}/episodes/{a.ep}/final.mp4 ({total:g}초, {sound}), captions.srt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
