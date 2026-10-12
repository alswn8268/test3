"""여러 채널·여러 편을 한 번에: 검사 → 미리보기 → 장면 클립 → 조립(BGM·효과음).

    python -m tools.batch --all                 # 모든 채널, 모든 편 (사실 확인 통과한 편만)
    python -m tools.batch shortcut spelling     # 고른 채널만
    python -m tools.batch money --eps ep02 ep03 # 고른 편만
    python -m tools.batch --all --draft         # 사실 확인 전 '초안'까지 렌더 (업로드 금지)
    python -m tools.batch --all --jobs 3        # 채널 3개를 동시에 (CPU 코어 수에 맞추기)

일요일 밤에 걸어두고 자는 용도. 결과 요약은 마지막에 표로 나온다.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from tools.common import ROOT, list_channels, list_episodes


def run(cmd: list[str]) -> tuple[bool, str]:
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
    return p.returncode == 0, (p.stdout + p.stderr).strip()


def one(ch: str, ep: str, draft: bool) -> tuple[str, str, str]:
    py = [sys.executable, "-m"]
    ok, out = run(py + ["tools.validate", ch, ep])
    if not ok:
        return ch, ep, "대본 오류 → " + out.splitlines()[-1]
    ok, out = run(py + ["tools.factcheck", ch, ep, "--check"])
    if not ok and not draft:
        return ch, ep, "사실 확인 미완료 (건너뜀)"
    fact = "확인 완료" if ok else "초안(사실 확인 전)"
    ok, out = run(["node", "render/capture.mjs", ch, ep, "--stills"])
    warns = sum("WARN" in line for line in out.splitlines())
    if not ok:
        return ch, ep, "미리보기 실패 → " + out[-200:]
    ok, out = run(["node", "render/capture.mjs", ch, ep])
    if not ok:
        return ch, ep, "클립 실패 → " + out[-200:]
    ok, out = run(py + ["tools.assemble", ch, ep])
    if not ok:
        return ch, ep, "조립 실패 → " + out[-200:]
    _, gate = run(py + ["tools.motion_gate", f"channels/{ch}/episodes/{ep}/final.mp4"])
    light = gate[1:3] if gate.startswith("[") else "?"
    return ch, ep, f"완성 · {fact} · 움직임 {light}" + (f" · 화면 넘침 {warns}건" if warns else "")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("channels", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--eps", nargs="*")
    ap.add_argument("--draft", action="store_true", help="사실 확인 전이어도 렌더 (업로드 금지)")
    ap.add_argument("--jobs", type=int, default=1, help="동시에 돌릴 채널 수")
    a = ap.parse_args(argv)
    chans = list_channels() if a.all else a.channels
    if not chans:
        ap.error("채널을 주거나 --all")

    def channel_job(ch: str) -> list[tuple[str, str, str]]:
        res = []
        for ep in a.eps or list_episodes(ch):
            r = one(ch, ep, a.draft)
            print(f"[{r[0]}/{r[1]}] {r[2]}", flush=True)
            res.append(r)
        return res

    with ThreadPoolExecutor(max_workers=max(1, a.jobs)) as pool:
        results = [r for rs in pool.map(channel_job, chans) for r in rs]

    print("\n| 채널 | 편 | 결과 |\n|---|---|---|")
    for ch, ep, msg in results:
        print(f"| {ch} | {ep} | {msg} |")
    return 0 if all(m.startswith("완성") or "건너뜀" in m for _, _, m in results) else 1


if __name__ == "__main__":
    sys.exit(main())
