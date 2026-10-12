"""사람이 최종 영상을 본 뒤 '올려도 된다'고 승인한다. 승인된 편만 자동 업로드 대상이 된다.

    python -m tools.approve why ep01            # 검사 통과하면 승인
    python -m tools.approve why ep01 --revoke   # 승인 취소 (자동 업로드 대기열에서 빠짐)

승인 조건: 대본 규칙 오류 0 · 사실 확인 표 전부 ✅ · final.mp4 있음 · post.md 세 플랫폼 문구 완성
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys

from tools import factcheck, publish, validate
from tools.common import COUPANG_NOTICE, episode_dir, load_channel, load_script, save_json


def problems(ch: str, ep: str) -> list[str]:
    out = []
    data = load_script(ch, ep)
    errors, _ = validate.check(data, load_channel(ch))
    out += [f"대본: {e}" for e in errors]
    d = episode_dir(ch, ep)
    fc = d / "factcheck.md"
    if not fc.exists():
        out.append("사실 확인 표 없음")
    else:
        scope = load_channel(ch).get("factcheck_scope", "numbers")
        md = fc.read_text(encoding="utf-8")
        missing = [c for c in factcheck.claims(data, scope) if c not in factcheck.parse_rows(md)]
        out += [f"사실 확인: 장면 {s:02d} 표에 없음" for s, _ in missing]
        out += [f"사실 확인: {p}" for p in factcheck.problems(md)]
    if not (d / "final.mp4").exists():
        out.append("final.mp4 없음")
    if not (d / "post.md").exists():
        out.append("post.md 없음")
    else:
        caps = publish.parse_post((d / "post.md").read_text(encoding="utf-8"))
        for p in publish.publish_conf(load_channel(ch))["platforms"]:
            if p not in caps or publish.unfinished(json.dumps(caps[p], ensure_ascii=False)):
                out.append(f"post.md: {p} 문구 미완성")
            elif data.get("sponsor"):
                text = json.dumps(caps[p], ensure_ascii=False)
                if "[광고]" not in text and "[협찬]" not in text:
                    out.append(f"post.md: {p} 문구 첫머리에 [광고]/[협찬] 표시 없음")
                if data["sponsor"].get("link_type") == "coupang" and COUPANG_NOTICE not in text:
                    out.append(f"post.md: {p} 에 쿠팡 파트너스 필수 문구 없음")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("channel")
    ap.add_argument("ep")
    ap.add_argument("--revoke", action="store_true")
    a = ap.parse_args(argv)
    path = episode_dir(a.channel, a.ep) / "script.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if a.revoke:
        data["status"] = "draft"
        data.pop("approved_at", None)
        save_json(path, data)
        print(f"[{a.channel}/{a.ep}] 승인 취소")
        return 0
    probs = problems(a.channel, a.ep)
    if probs:
        print(f"[{a.channel}/{a.ep}] 승인할 수 없음 ({len(probs)}건)")
        for p in probs[:20]:
            print("  ✗", p)
        return 1
    data["status"] = "approved"
    data["approved_at"] = dt.datetime.now(publish.KST).isoformat(timespec="minutes")
    save_json(path, data)
    print(f"[{a.channel}/{a.ep}] 승인 — 다음 자동 업로드 차례에 올라갑니다")
    return 0


if __name__ == "__main__":
    sys.exit(main())
