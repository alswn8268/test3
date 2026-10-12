"""장면 클립을 이어 붙여 final.mp4 와 자막 파일 captions.srt 를 만든다 (ffmpeg 대체 경로).

    python -m tools.assemble ep01                       # 클립만 이어 붙이기
    python -m tools.assemble ep01 --bgm assets/bgm/a.mp3  # 직접 만든 배경음 깔기

FilmCraft MCP 로 조립하는 것이 기본이고, 이 스크립트는 FilmCraft 가 실패할 때 쓰는 대체 경로다.
인기 사운드는 영상에 넣지 않고 업로드할 때 앱 안에서 얹는다 (음소거 방지).
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from tools.common import episode_dir, load_script, timeline


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


def ffmpeg_cmd(clips: list[Path], out: Path, list_file: Path, bgm: Path | None, total: float) -> list[str]:
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(list_file)]
    if bgm is None:
        # 무음 오디오 트랙을 넣어 둔다 (일부 플랫폼은 오디오 없는 영상을 싫어함)
        cmd += ["-f", "lavfi", "-t", f"{total}", "-i", "anullsrc=r=48000:cl=stereo"]
        audio = ["-map", "0:v", "-map", "1:a"]
    else:
        cmd += ["-stream_loop", "-1", "-i", str(bgm)]
        fade = max(total - 1.0, 0)
        cmd += ["-filter_complex", f"[1:a]atrim=0:{total},afade=t=out:st={fade}:d=1,loudnorm=I=-16:TP=-1.5:LRA=11[a]"]
        audio = ["-map", "0:v", "-map", "[a]"]
    return cmd + audio + ["-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{total}",
                          "-movflags", "+faststart", str(out)]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ep")
    ap.add_argument("--bgm", type=Path, help="직접 만든(저작권 문제 없는) 배경음 파일")
    a = ap.parse_args(argv)

    d = episode_dir(a.ep)
    data = load_script(a.ep)
    scenes = data["scenes"]
    clips = [d / "clips" / f"s{i:02d}.mp4" for i in range(1, len(scenes) + 1)]
    missing = [c.name for c in clips if not c.exists()]
    if missing:
        print(f"클립이 없습니다: {', '.join(missing)} → 먼저 `node render/capture.mjs {d.name}`")
        return 1
    if not shutil.which("ffmpeg"):
        print("ffmpeg 가 설치되어 있지 않습니다.")
        return 1

    (d / "captions.srt").write_text(build_srt(scenes), encoding="utf-8")
    total = sum(s["dur"] for s in scenes)
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.writelines(f"file '{c.resolve()}'\n" for c in clips)
        list_file = Path(f.name)
    try:
        subprocess.run(ffmpeg_cmd(clips, d / "final.mp4", list_file, a.bgm, total), check=True)
    finally:
        list_file.unlink(missing_ok=True)
    print(f"완성: episodes/{d.name}/final.mp4 ({total:g}초), captions.srt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
