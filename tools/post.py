"""업로드 문구 초안(post.md)을 만든다. 본문·해시태그는 /post 스킬에서 Claude가 다듬는다.

    python -m tools.post ep01 --month 12 --tags 연말정산 직장인 카드공제 체크카드

캡션 규칙: 첫 줄 = 후킹 문장 그대로, 둘째 줄 = '저장해두고 ○월에 다시 보기',
해시태그 5개 = 넓은 것 2 + 주제 2 + 채널 고유 1(#월급사용설명서).
"""
from __future__ import annotations

import argparse
import sys

from tools.common import episode_dir, load_script, plain

CHANNEL_TAG = "#월급사용설명서"


def hook_sentence(data: dict) -> str:
    return " ".join(plain(x) for x in data["scenes"][0]["lines"])


def build(data: dict, month: str, tags: list[str]) -> str:
    tags = [t if t.startswith("#") else f"#{t}" for t in tags][:4]
    tags += ["#TODO"] * (4 - len(tags))
    return "\n".join([
        f"# 업로드 문구 — {data['id']} {data['title']}",
        "",
        "## 캡션",
        hook_sentence(data),
        f"저장해두고 {month}월에 다시 보기",
        "",
        "(본문 2~3줄: 영상 핵심 숫자 + 지금 할 일 1개)",
        "",
        " ".join(tags + [CHANNEL_TAG]),
        "",
        "## 커버 문구",
        data["title"],
        "",
        "## 예약",
        "| 플랫폼 | 날짜 | 시간 | 완료 |",
        "|---|---|---|---|",
        "| 인스타 릴스 (Meta Business Suite) |  |  | ☐ |",
        "| 틱톡 (TikTok Studio, 예약 후 수정 불가) |  |  | ☐ |",
        "| 유튜브 쇼츠 (YouTube Studio) |  |  | ☐ |",
        "",
    ])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ep")
    ap.add_argument("--month", default="○", help="다시 볼 달 (예: 12)")
    ap.add_argument("--tags", nargs="*", default=[], help="넓은 것 2 + 주제 2 (# 없이)")
    ap.add_argument("--force", action="store_true", help="이미 있는 post.md 덮어쓰기")
    a = ap.parse_args(argv)
    path = episode_dir(a.ep) / "post.md"
    if path.exists() and not a.force:
        print(f"{path.name} 이 이미 있습니다 (--force 로 덮어쓰기)")
        return 1
    path.write_text(build(load_script(a.ep), a.month, a.tags), encoding="utf-8")
    print(f"episodes/{path.parent.name}/post.md 작성")
    return 0


if __name__ == "__main__":
    sys.exit(main())
