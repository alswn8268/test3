"""자동 업로드 — 플랫폼 **공식 API** 로만 올린다 (브라우저 자동 클릭·비공식 도구는 계정 정지 위험이라 쓰지 않음).

    python -m tools.publish --list-due                 # 오늘 올릴 차례인 (채널, 편) 목록
    python -m tools.publish --due --dry-run            # 무엇을 어디에 올릴지 미리 보기 (기본: 실제 업로드 안 함)
    python -m tools.publish --due --live               # 실제 업로드 (GitHub Actions 가 매일 한 번 실행)
    python -m tools.publish why ep01 --platform youtube --live   # 한 편만 바로

올릴 수 있는 편 = 사람이 승인한 편만:  `python -m tools.approve <채널> <편>`
  (대본 규칙 · 사실 확인 ✅ · final.mp4 · 플랫폼별 문구가 모두 끝나야 승인된다)

주기: channel.json 의 publish.every_days (기본 2일). 마지막 업로드 후 그 날짜가 지나면 다음 승인 편을 올린다.
기록: channels/<채널>/published.csv (같은 편을 두 번 올리지 않게)

인증 정보는 저장소에 넣지 않고 환경 변수(GitHub Secrets)로만 받는다:
  공통   YT_CLIENT_ID, YT_CLIENT_SECRET, TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET
  채널별 YT_REFRESH_TOKEN_<채널>, TIKTOK_REFRESH_TOKEN_<채널>, IG_USER_ID_<채널>, IG_ACCESS_TOKEN_<채널>
         (<채널> 은 대문자: MONEY, SHORTCUT, SPELLING, WHY)
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from tools.common import (
    channel_dir,
    episode_dir,
    list_channels,
    list_episodes,
    load_channel,
    load_script,
)

PLATFORMS = ("youtube", "tiktok", "instagram")
LOG_FIELDS = ["ep", "platform", "published_at", "remote_id", "status"]
KST = dt.timezone(dt.timedelta(hours=9))


# ---------------------------------------------------------------- 기록 · 차례 계산
def log_path(ch: str) -> Path:
    return channel_dir(ch) / "published.csv"


def read_log(ch: str) -> list[dict]:
    p = log_path(ch)
    if not p.exists():
        return []
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def append_log(ch: str, row: dict) -> None:
    p = log_path(ch)
    new = not p.exists()
    with open(p, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        if new:
            w.writeheader()
        w.writerow(row)


def publish_conf(channel: dict) -> dict:
    conf = {"every_days": 2, "platforms": list(PLATFORMS), "tiktok_mode": "inbox", "privacy": "public"}
    conf.update(channel.get("publish", {}))
    return conf


def done_platforms(log: list[dict], ep: str) -> set[str]:
    return {r["platform"] for r in log if r["ep"] == ep and r["status"] in ("published", "sent_to_inbox")}


def next_episode(ch: str) -> str | None:
    """승인됐고 아직 모든 플랫폼에 올라가지 않은 가장 앞 번호 편."""
    conf, log = publish_conf(load_channel(ch)), read_log(ch)
    for ep in list_episodes(ch):
        data = load_script(ch, ep)
        if data.get("status") != "approved" or data.get("sponsor"):
            continue
        if set(conf["platforms"]) - done_platforms(log, ep):
            return ep
    return None


def is_due(ch: str, now: dt.datetime) -> bool:
    log = [r for r in read_log(ch) if r["status"] in ("published", "sent_to_inbox")]
    if not log:
        return True
    last = max(dt.datetime.fromisoformat(r["published_at"]) for r in log)
    # 1시간 여유: 매일 같은 시각에 돌 때 몇 분 차이로 하루 밀리지 않게
    return now - last >= dt.timedelta(days=publish_conf(load_channel(ch))["every_days"]) - dt.timedelta(hours=1)


def due_list(now: dt.datetime) -> list[tuple[str, str]]:
    out = []
    for ch in list_channels():
        ep = next_episode(ch)
        if ep and is_due(ch, now):
            out.append((ch, ep))
    return out


# ---------------------------------------------------------------- post.md → 플랫폼별 문구
def parse_post(md: str) -> dict:
    """post.md 의 '## 틱톡' · '## 유튜브 쇼츠' · '## 인스타그램 릴스' 구역을 읽는다."""
    sec: dict[str, list[str]] = {}
    cur = None
    names = (("틱톡", "tiktok"), ("유튜브", "youtube"), ("인스타", "instagram"))
    for line in md.splitlines():
        if line.startswith("## "):
            cur = next((v for k, v in names if line[3:].startswith(k)), None)
            if cur:
                sec[cur] = []
            continue
        if cur:
            sec[cur].append(line)
    out = {}
    for p, lines in sec.items():
        text = "\n".join(lines).strip()
        if p == "youtube":
            m = re.search(r"^제목:\s*(.+)$", text, re.MULTILINE)
            desc = text.split("설명:", 1)[1].strip() if "설명:" in text else ""
            out[p] = {"title": (m.group(1).strip() if m else ""), "description": desc}
        else:
            out[p] = {"caption": text}
    return out


def unfinished(text: str) -> bool:
    return any(x in text for x in ("TODO", "(본문"))


def captions(ch: str, ep: str) -> dict:
    p = episode_dir(ch, ep) / "post.md"
    if not p.exists():
        raise SystemExit(f"{ch}/{ep}: post.md 없음 → `/post {ch} {ep}`")
    return parse_post(p.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- HTTP (표준 라이브러리만)
def http(method: str, url: str, data: bytes | None = None, headers: dict | None = None, timeout: int = 300):
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
        return r.status, dict(r.headers), (json.loads(body) if body and body[:1] in (b"{", b"[") else body)


def form(d: dict) -> bytes:
    return urllib.parse.urlencode(d).encode()


def env(name: str, ch: str | None = None) -> str:
    key = f"{name}_{ch.upper()}" if ch else name
    v = os.environ.get(key, "")
    if not v:
        raise RuntimeError(f"환경 변수 {key} 가 없습니다 (GitHub Secrets 에 등록)")
    return v


# ---------------------------------------------------------------- 유튜브 (YouTube Data API v3, 재개 가능 업로드)
def upload_youtube(ch: str, video: Path, cap: dict, privacy: str) -> str:
    _, _, tok = http("POST", "https://oauth2.googleapis.com/token", form({
        "client_id": env("YT_CLIENT_ID"), "client_secret": env("YT_CLIENT_SECRET"),
        "refresh_token": env("YT_REFRESH_TOKEN", ch), "grant_type": "refresh_token"}))
    auth = {"Authorization": f"Bearer {tok['access_token']}"}
    meta = {"snippet": {"title": cap["title"][:100], "description": cap["description"][:4900], "categoryId": "27"},
            "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False}}
    _, headers, _ = http("POST", "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
                         json.dumps(meta).encode(), {**auth, "Content-Type": "application/json; charset=UTF-8",
                                                     "X-Upload-Content-Type": "video/mp4",
                                                     "X-Upload-Content-Length": str(video.stat().st_size)})
    loc = headers.get("Location") or headers.get("location")
    _, _, res = http("PUT", loc, video.read_bytes(), {**auth, "Content-Type": "video/mp4"})
    return res["id"]


# ---------------------------------------------------------------- 틱톡 (Content Posting API)
def upload_tiktok(ch: str, video: Path, cap: dict, mode: str) -> tuple[str, str]:
    """mode="inbox": 틱톡 앱 받은편지함에 초안으로 보냄 → 앱에서 '게시' 한 번 (심사 전에도 가능, 추천)
       mode="direct": 바로 게시 (TikTok 앱 심사 통과 전에는 '나만 보기'로만 올라감)"""
    _, _, tok = http("POST", "https://open.tiktokapis.com/v2/oauth/token/", form({
        "client_key": env("TIKTOK_CLIENT_KEY"), "client_secret": env("TIKTOK_CLIENT_SECRET"),
        "grant_type": "refresh_token", "refresh_token": env("TIKTOK_REFRESH_TOKEN", ch)}),
        {"Content-Type": "application/x-www-form-urlencoded"})
    if tok.get("refresh_token") and tok["refresh_token"] != os.environ.get(f"TIKTOK_REFRESH_TOKEN_{ch.upper()}"):
        print(f"  ! 틱톡이 새 refresh token 을 줬습니다 → Secrets 의 TIKTOK_REFRESH_TOKEN_{ch.upper()} 를 바꿔 주세요")
    auth = {"Authorization": f"Bearer {tok['access_token']}", "Content-Type": "application/json; charset=UTF-8"}
    size = video.stat().st_size
    source = {"source": "FILE_UPLOAD", "video_size": size, "chunk_size": size, "total_chunk_count": 1}
    if mode == "direct":
        _, _, info = http("POST", "https://open.tiktokapis.com/v2/post/publish/creator_info/query/", b"{}", auth)
        options = info["data"]["privacy_level_options"]
        privacy = "PUBLIC_TO_EVERYONE" if "PUBLIC_TO_EVERYONE" in options else options[0]
        body = {"post_info": {"title": cap["caption"][:2200], "privacy_level": privacy, "video_cover_timestamp_ms": 500},
                "source_info": source}
        url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
    else:
        body = {"source_info": source}
        url = "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/"
    _, _, init = http("POST", url, json.dumps(body).encode(), auth)
    http("PUT", init["data"]["upload_url"], video.read_bytes(),
         {"Content-Type": "video/mp4", "Content-Range": f"bytes 0-{size - 1}/{size}"})
    return init["data"]["publish_id"], ("published" if mode == "direct" else "sent_to_inbox")


# ---------------------------------------------------------------- 인스타그램 릴스 (Instagram Graph API, 재개 가능 업로드)
def upload_instagram(ch: str, video: Path, cap: dict) -> str:
    ver = os.environ.get("IG_GRAPH_VERSION", "v21.0")
    uid, token = env("IG_USER_ID", ch), env("IG_ACCESS_TOKEN", ch)
    # 페이스북 로그인 방식이면 graph.facebook.com, 인스타그램 로그인 방식이면 graph.instagram.com
    g = f"https://{os.environ.get('IG_GRAPH_HOST', 'graph.facebook.com')}/{ver}"
    _, _, c = http("POST", f"{g}/{uid}/media", form({"media_type": "REELS", "upload_type": "resumable",
                                                     "caption": cap["caption"][:2200], "share_to_feed": "true",
                                                     "access_token": token}))
    cid = c["id"]
    http("POST", f"https://rupload.facebook.com/ig-api-upload/{ver}/{cid}", video.read_bytes(),
         {"Authorization": f"OAuth {token}", "offset": "0", "file_size": str(video.stat().st_size)})
    for _ in range(60):  # 처리 완료까지 최대 약 10분 대기
        _, _, st = http("GET", f"{g}/{cid}?fields=status_code&access_token={urllib.parse.quote(token)}")
        if st.get("status_code") == "FINISHED":
            break
        if st.get("status_code") == "ERROR":
            raise RuntimeError(f"인스타 처리 실패: {st}")
        time.sleep(10)
    _, _, pub = http("POST", f"{g}/{uid}/media_publish", form({"creation_id": cid, "access_token": token}))
    return pub["id"]


# ---------------------------------------------------------------- 실행
def check_ready(ch: str, ep: str) -> list[str]:
    problems = []
    data = load_script(ch, ep)
    if data.get("status") != "approved":
        problems.append("승인 안 됨 → `python -m tools.approve` (사람이 최종본을 본 뒤)")
    if data.get("sponsor"):
        problems.append("협찬·광고 편 → 플랫폼 광고 표시(유료 프로모션·브랜드 콘텐츠·유료 파트너십)를 직접 켜야 해서 자동 업로드 제외")
    if not (episode_dir(ch, ep) / "final.mp4").exists():
        problems.append("final.mp4 없음 → 렌더·조립 먼저")
    return problems


def publish_one(ch: str, ep: str, platforms: list[str], live: bool, now: dt.datetime) -> list[str]:
    channel, conf = load_channel(ch), publish_conf(load_channel(ch))
    video = episode_dir(ch, ep) / "final.mp4"
    caps = captions(ch, ep)
    done = done_platforms(read_log(ch), ep)
    results = []
    for p in platforms:
        tag = f"[{ch}/{ep}] {p}"
        if p in done:
            results.append(f"{tag}: 이미 올림 (건너뜀)")
            continue
        cap = caps.get(p)
        text = json.dumps(cap, ensure_ascii=False) if cap else ""
        if not cap or unfinished(text):
            results.append(f"{tag}: post.md 의 이 플랫폼 문구가 비었거나 미완성 (건너뜀)")
            continue
        if not live:
            preview = cap.get("title") or cap.get("caption", "").splitlines()[0]
            results.append(f"{tag}: [미리보기] {video.name} → '{preview}' ({channel['name']})")
            continue
        try:
            if p == "youtube":
                rid, status = upload_youtube(ch, video, cap, conf["privacy"]), "published"
            elif p == "tiktok":
                rid, status = upload_tiktok(ch, video, cap, conf["tiktok_mode"])
            else:
                rid, status = upload_instagram(ch, video, cap), "published"
            append_log(ch, {"ep": ep, "platform": p, "published_at": now.isoformat(timespec="minutes"),
                            "remote_id": rid, "status": status})
            results.append(f"{tag}: {status} ({rid})")
        except (OSError, RuntimeError, KeyError, ValueError) as e:  # 한 플랫폼이 실패해도 나머지는 계속 (HTTP 오류는 OSError)
            append_log(ch, {"ep": ep, "platform": p, "published_at": now.isoformat(timespec="minutes"),
                            "remote_id": "", "status": f"error: {str(e)[:120]}"})
            results.append(f"{tag}: 실패 — {e}")
    return results


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("channel", nargs="?")
    ap.add_argument("ep", nargs="?")
    ap.add_argument("--due", action="store_true", help="차례가 된 채널만")
    ap.add_argument("--list-due", action="store_true", help="차례 목록만 'channel ep' 줄로 출력")
    ap.add_argument("--platform", choices=PLATFORMS, action="append")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--live", action="store_true", help="실제 업로드")
    mode.add_argument("--dry-run", action="store_true", help="미리 보기 (기본)")
    a = ap.parse_args(argv)
    now = dt.datetime.now(KST)

    if a.list_due:
        for ch, ep in due_list(now):
            print(ch, ep)
        return 0
    if a.due:
        targets = due_list(now)
    elif a.channel and a.ep:
        targets = [(a.channel, a.ep)]
    else:
        ap.error("--due 또는 <채널> <편>")
    if not targets:
        print("오늘은 올릴 차례인 편이 없습니다.")
        return 0

    failed = False
    for ch, ep in targets:
        problems = check_ready(ch, ep)
        if problems:
            print(f"[{ch}/{ep}] 올릴 수 없음: " + " / ".join(problems))
            failed = True
            continue
        platforms = a.platform or publish_conf(load_channel(ch))["platforms"]
        for line in publish_one(ch, ep, platforms, a.live, now):
            print(line)
            failed |= "실패" in line
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
