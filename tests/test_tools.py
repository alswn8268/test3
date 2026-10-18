import copy

import numpy as np
import pytest

from tools import assemble, audio, factcheck, new_episode, post, review, validate
from tools.common import (
    list_channels,
    list_episodes,
    load_channel,
    load_script,
    plain,
    timeline,
)

ALL = [(ch, ep) for ch in list_channels() for ep in list_episodes(ch)]


def test_three_channels_with_five_episodes_each():
    assert set(list_channels()) >= {"money", "shortcut", "spelling", "why"}
    for ch in ("money", "shortcut", "spelling", "why"):
        assert len(list_episodes(ch)) >= 5


@pytest.mark.parametrize("ch", ["money", "shortcut", "spelling", "why"])
def test_channel_config_is_complete(ch):
    c = load_channel(ch)
    for key in ("name", "colors", "props", "bgm", "hashtag", "accounts", "schedule"):
        assert key in c
    assert {"paper", "ink", "signal"} <= set(c["colors"]) <= {"paper", "ink", "signal", "signal_text", "board"}
    assert c["bgm"]["style"] in audio.STYLES
    assert c["hashtag"].startswith("#")


def test_channels_do_not_share_identity():
    """계정마다 이름·색·해시태그·음악이 달라야 한다 (같은 채널 복제처럼 보이지 않게)."""
    cs = [load_channel(ch) for ch in list_channels()]
    for key in (lambda c: c["name"], lambda c: c["colors"]["signal"], lambda c: c["hashtag"],
                lambda c: (c["bgm"]["style"], c["bgm"]["seed"])):
        values = [key(c) for c in cs]
        assert len(values) == len(set(values))


@pytest.mark.parametrize("ch,ep", ALL)
def test_existing_episodes_have_no_errors(ch, ep):
    errors, _ = validate.check(load_script(ch, ep))
    assert errors == []


def test_no_duplicate_titles_across_channels():
    titles = [load_script(ch, ep)["title"] for ch, ep in ALL]
    assert len(titles) == len(set(titles))


def test_validate_catches_broken_script():
    data = copy.deepcopy(load_script("money", "ep01"))
    data["scenes"] = data["scenes"][:-1]  # CTA 빠짐 → 11장면, 27초
    data["scenes"][2]["say"] = ""
    errors, _ = validate.check(data)
    text = "\n".join(errors)
    assert "장면 수 11개" in text and "총 길이" in text and "cta" in text and "say" in text


def test_validate_requires_keys_on_keys_scene():
    data = copy.deepcopy(load_script("shortcut", "ep01"))
    k = next(s for s in data["scenes"] if s["type"] == "keys")
    k["keys"] = []
    errors, _ = validate.check(data)
    assert any("'keys'" in e for e in errors)


def test_validate_warns_long_line_and_double_highlight():
    data = copy.deepcopy(load_script("money", "ep01"))
    data["scenes"][1]["lines"] = ["아주아주아주아주긴한줄입니다", "[하나] [둘]"]
    _, warns = validate.check(data)
    assert any("글자" in w for w in warns) and any("강조 2개" in w for w in warns)


def test_new_episode_template_is_valid():
    errors, _ = validate.check(new_episode.template("ep99_x", "상시 · 통장 관리", "테스트"))
    assert errors == []


def test_plain_strips_markup():
    assert plain("연봉의 [25%] {0원}") == "연봉의 25% 0원"


def test_factcheck_numbers_scope_skips_numbering_labels():
    claims = factcheck.claims(load_script("money", "ep01"))
    assert (1, "연봉의 25%") in claims
    assert not any(t.startswith("01  ") for _, t in claims)


def test_factcheck_every_scene_scope_covers_rules():
    data = load_script("spelling", "ep01")
    claims = factcheck.claims(data, "every_scene")
    assert len(claims) == 10  # 후킹·CTA 를 뺀 10장면
    assert any("돼요" in t for _, t in claims)


def test_factcheck_keeps_existing_sources_and_checks():
    data = load_script("money", "ep01")
    md = factcheck.build(data)
    assert len(factcheck.problems(md)) == len(factcheck.claims(data))
    filled = md.replace("| 01 | 연봉의 25% |  | ☐ |", "| 01 | 연봉의 25% | https://www.nts.go.kr | ✅ |")
    rebuilt = factcheck.build(data, filled)
    assert "| 연봉의 25% | https://www.nts.go.kr | ✅ |" in rebuilt
    assert len(factcheck.problems(rebuilt)) == len(factcheck.claims(data)) - 1


def test_srt_follows_scene_timeline():
    scenes = load_script("money", "ep01")["scenes"]
    srt = assemble.build_srt(scenes)
    assert srt.startswith("1\n00:00:00,000 --> 00:00:03,000\n")
    assert "12\n00:00:27,000 --> 00:00:30,000\n" in srt
    assert timeline(scenes)[-1][1] == pytest.approx(30.0)


def test_cuts_land_on_the_beat():
    """100BPM 에서 모든 컷(장면 경계)이 박자 위에 있어야 한다."""
    for ch, ep in ALL:
        for t0, _ in timeline(load_script(ch, ep)["scenes"]):
            beats = t0 / audio.BEAT
            assert abs(beats - round(beats)) < 1e-6, (ch, ep, t0)


@pytest.mark.parametrize("style", sorted(audio.STYLES))
def test_bgm_is_stereo_bounded_and_not_silent(style):
    x = audio.render_bgm(style, 3, 6.0)
    assert x.shape == (int(6.0 * audio.SR), 2)
    assert np.isfinite(x).all() and np.abs(x).max() <= 1.0
    assert np.sqrt((x ** 2).mean()) > 0.01


def test_bgm_differs_per_episode():
    c = load_channel("money")
    a = audio.episode_seed(c, "ep01")
    b = audio.episode_seed(c, "ep02")
    assert a != b
    assert not np.allclose(audio.render_bgm("lofi", a, 3.0), audio.render_bgm("lofi", b, 3.0))


def test_sfx_events_match_scene_content():
    scenes = load_script("shortcut", "ep01")["scenes"]
    ev = audio.sfx_events(scenes)
    names = [n for _, n, _ in ev]
    assert names[0] == "impact"
    assert names.count("whoosh") == len(scenes) - 1
    n_keys = sum(len(s.get("keys", [])) for s in scenes)
    assert names.count("key") == n_keys
    assert names.count("stamp") == 1
    assert all(0 <= t < 30 for t, _, _ in ev)


def test_review_grades_against_thresholds():
    row = {"ep": "ep01", "platform": "reels", "views": 1000, "viewed_3s": 750, "avg_watch_sec": 12,
           "saves": 20, "shares": 2, "profile_visits": 50, "follows": 6}
    result = {name: ok for name, _, ok, _ in review.grade(row)}
    assert result == {"3초 유지율": True, "완주율": False, "저장률": True, "공유율": False, "팔로우 전환": True}
    out = review.report([row])
    assert "3/5" in out and "후속편 후보" in out and "다음 주 고칠 것" in out


def test_review_handles_zero_views():
    row = {"ep": "ep01", "platform": "tiktok", "views": 0, "viewed_3s": 0, "avg_watch_sec": 0,
           "saves": 0, "shares": 0, "profile_visits": 0, "follows": 0}
    assert all(v is None or v == 0 for _, v, _, _ in review.grade(row))


def test_post_has_three_platform_sections():
    md = post.build(load_channel("shortcut"), load_script("shortcut", "ep01"), "○", ["엑셀", "직장인", "빠른채우기", "CtrlE"])
    lines = md.splitlines()
    for sec in ("## 틱톡", "## 유튜브 쇼츠", "## 인스타그램 릴스"):
        assert any(line.startswith(sec) for line in lines), sec
    i = next(n for n, line in enumerate(lines) if line.startswith("## 틱톡"))
    assert lines[i + 1] == "300줄 복붙 3초면 끝 Ctrl + E"
    assert lines[i + 2] == "저장해두고 다시 보기"
    assert lines[i + 3] == "#엑셀 #직장인 #빠른채우기 #CtrlE #칼퇴단축키"
    assert "제목: Ctrl+E 하나로 300줄 정리" in md
    assert "칼퇴 단축키" in lines[0]


def test_hook_rules_ban_controversy_for_curiosity_channel():
    rules = load_channel("why")["hook_rules"]
    banned = " ".join(rules["banned"])
    for word in ("정치", "종교", "건강 공포", "낚시"):
        assert word in banned


def test_signal_text_is_readable_on_paper():
    """종이 배경 위 신호색 글자가 읽히는지. 흰 글자+외곽선을 쓰는 lab 테마는 제외."""
    def lum(h):
        def f(c):
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
        return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)
    for ch in list_channels():
        c = load_channel(ch)
        if c.get("theme") == "lab":
            continue
        col = c["colors"]
        ratio = (lum(col["paper"]) + 0.05) / (lum(col.get("signal_text", col["signal"])) + 0.05)
        # 최소선 2.5:1 (노랑처럼 안 읽히는 색을 막는 용도). 권장은 큰 글자 기준 3:1
        assert ratio >= 2.5, (ch, round(ratio, 2))


@pytest.mark.parametrize("ch", ["money", "shortcut", "spelling", "why"])
def test_each_channel_has_its_own_theme(ch):
    themes = {load_channel(c)["theme"] for c in list_channels()}
    assert load_channel(ch)["theme"] in {"ledger", "sheet", "notebook", "lab"}
    assert len(themes) == len(list_channels())


def test_theme_transition_sounds_differ():
    scenes = load_script("spelling", "ep01")["scenes"]
    names = {th: {n for _, n, _ in audio.sfx_events(scenes, th)} for th in audio.TRANSITION}
    assert "page" in names["notebook"] and "scribble" in names["notebook"]
    assert "boing" in names["lab"] and "whoosh" in names["ledger"]


# ---------------------------------------------------------------- 자동 업로드
def _fake_channel(tmp_path, monkeypatch):
    import json
    import shutil

    from tools import common
    from tools import post as post_tool
    monkeypatch.setattr(common, "CHANNELS", tmp_path)
    shutil.copytree(common.ROOT / "channels" / "why", tmp_path / "why",
                    ignore=shutil.ignore_patterns("clips", "preview", "*.mp4", "*.wav", "published.csv", "post.md"))
    for ep in ("ep01", "ep02"):
        d = tmp_path / "why" / "episodes" / ep
        data = json.loads((d / "script.json").read_text(encoding="utf-8"))
        data["status"] = "approved"
        (d / "script.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        (d / "final.mp4").write_bytes(b"fake")
        md = post_tool.build(load_channel("why"), data, "○", ["상식", "과학", "베리", "딸기"])
        (d / "post.md").write_text(md.replace("(본문 1~2줄: 영상 핵심 + 지금 할 일)", "본문")
                                   .replace("(본문 2~3줄: 영상 핵심 + 지금 할 일 1개)", "본문"), encoding="utf-8")


def test_publish_parses_three_platform_captions():
    from tools import publish
    md = post.build(load_channel("why"), load_script("why", "ep01"), "○", ["상식", "과학", "베리", "딸기"])
    caps = publish.parse_post(md)
    assert set(caps) == {"tiktok", "youtube", "instagram"}
    assert caps["youtube"]["title"] == "딸기는 베리가 아닙니다"
    assert caps["tiktok"]["caption"].startswith("딸기는 베리가 아닙니다")
    assert publish.unfinished(caps["instagram"]["caption"])  # 본문 자리표시가 남아 있으면 미완성


def test_publish_every_two_days_in_order(tmp_path, monkeypatch):
    import datetime as dt

    from tools import publish
    _fake_channel(tmp_path, monkeypatch)
    calls = []
    monkeypatch.setattr(publish, "upload_youtube", lambda ch, v, c, p: calls.append(("yt", ch)) or "yt1")
    monkeypatch.setattr(publish, "upload_tiktok", lambda ch, v, c, m: (calls.append(("tt", ch)) or "tt1", "sent_to_inbox"))
    monkeypatch.setattr(publish, "upload_instagram", lambda ch, v, c: calls.append(("ig", ch)) or "ig1")
    t0 = dt.datetime(2026, 10, 13, 11, 40, tzinfo=publish.KST)

    assert publish.due_list(t0) == [("why", "ep01")]
    dry = publish.publish_one("why", "ep01", list(publish.PLATFORMS), live=False, now=t0)
    assert all("미리보기" in line for line in dry) and calls == []

    publish.publish_one("why", "ep01", list(publish.PLATFORMS), live=True, now=t0)
    assert len(calls) == 3
    assert publish.due_list(t0 + dt.timedelta(days=1)) == []                      # 하루 뒤엔 쉬고
    assert publish.due_list(t0 + dt.timedelta(days=2)) == [("why", "ep02")]       # 이틀 뒤 다음 편
    again = publish.publish_one("why", "ep01", list(publish.PLATFORMS), live=True, now=t0)
    assert all("이미 올림" in line for line in again) and len(calls) == 3         # 같은 편 두 번 안 올림


def test_unapproved_episode_is_never_published(tmp_path, monkeypatch):
    from tools import publish
    _fake_channel(tmp_path, monkeypatch)
    from tools.approve import main as approve_main
    assert approve_main(["why", "ep01", "--revoke"]) == 0
    assert publish.check_ready("why", "ep01")
    assert publish.next_episode("why") == "ep02"


# ---------------------------------------------------------------- 협찬·광고
def test_sponsored_episode_disclosure_everywhere():
    from tools.common import COUPANG_NOTICE
    data = load_script("shortcut", "ep06")
    assert data["sponsor"]["kind"] == "affiliate"
    md = post.build(load_channel("shortcut"), data, "○", ["윈도우", "직장인", "듀얼모니터", "단축키"])
    from tools import publish
    caps = publish.parse_post(md)
    for p in ("tiktok", "youtube", "instagram"):
        text = caps[p].get("caption") or caps[p]["title"] + caps[p]["description"]
        assert "[광고]" in text and COUPANG_NOTICE in md
    assert caps["youtube"]["title"].startswith("[광고]")


def test_sponsored_episode_is_not_auto_published():
    from tools import publish
    assert any("협찬" in p for p in publish.check_ready("shortcut", "ep06"))


def test_banned_sponsor_category_is_rejected():
    data = copy.deepcopy(load_script("money", "ep01"))
    data["sponsor"] = {"kind": "affiliate", "brand": "어떤 카드사", "category": "신용카드"}
    errors, _ = validate.check(data, load_channel("money"))
    assert any("금지된 협찬 분야" in e for e in errors)


def test_identity_handles_follow_platform_rules():
    import re
    rule = re.compile(r"^(?!\.)(?!.*\.\.)[a-z0-9._]{3,24}(?<!\.)$")
    handles = []
    for ch in list_channels():
        ident = load_channel(ch)["identity"]
        for h in [ident["handle"], *ident["handle_backups"]]:
            assert rule.match(h), h
            handles.append(h)
        assert len(ident["bio"]) <= 80
    assert len(handles) == len(set(handles))


# ---------------------------------------------------------------- 움직임 관문
def test_motion_gate_tells_static_from_moving(tmp_path):
    import shutil
    import subprocess
    if not shutil.which("ffmpeg"):
        pytest.skip("ffmpeg 없음")
    from tools import motion_gate
    still, moving = tmp_path / "still.mp4", tmp_path / "moving.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=360x640:rate=30:duration=3",
                    "-vf", "trim=end_frame=1,loop=89:1:0", "-pix_fmt", "yuv420p", str(still)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=360x640:rate=30:duration=3",
                    "-vf", "scroll=horizontal=0.02", "-pix_fmt", "yuv420p", str(moving)], check=True)  # 화면 전체가 움직임
    s, m = motion_gate.measure(still), motion_gate.measure(moving)
    assert s["fast_ratio"] < 0.035 and motion_gate.verdict(s)[0] == "빨강"
    assert m["fast_ratio"] >= 0.06 and motion_gate.verdict(m)[0] == "초록"


# ---------------------------------------------------------------- Claude 위임 승인
def test_claude_checkmark_needs_official_source_and_quote():
    rows = [
        "| # | 장면 | 화면 문구 | 출처 (URL) | 확인 |", "|---|---|---|---|---|",
        '| 1 | 02 | 가 | https://www.nts.go.kr/a | ✅ Claude: "근로소득자의 신용카드 사용액이 총급여의 25%를" |',
        '| 2 | 03 | 나 | https://blog.example.com/b | ✅ Claude: "어느 블로그에서 가져온 아주 긴 문장입니다" |',
        "| 3 | 04 | 다 | https://support.microsoft.com/x | ✅ Claude |",
        "| 4 | 05 | 라 | https://blog.example.com/c | ✅ |",
    ]
    md = "\n".join(rows)
    probs = factcheck.claude_problems(md, ["https://support.microsoft.com"])
    text = "\n".join(probs)
    assert "장면 02" not in text                       # 공식 + 인용 → 통과
    assert "장면 03" in text and "공식 출처가 아님" in text
    assert "장면 04" in text and "원문 인용이 없음" in text
    assert "장면 05" not in text                       # 사람이 찍은 ✅ 는 사람 책임


def test_review_uses_sends_and_swipe_rate_when_present():
    base = {"ep": "ep01", "platform": "youtube", "views": 1000, "viewed_3s": 750, "avg_watch_sec": 12,
            "saves": 20, "shares": 2, "profile_visits": 50, "follows": 6}
    without = review.grade({**base, "sends": None, "viewed_vs_swiped": None})
    assert len(without) == 5                                   # 빈 선택 칸은 미달로 세지 않음
    with_new = {n: ok for n, _, ok, _ in review.grade({**base, "sends": 9, "viewed_vs_swiped": 64.0})}
    assert with_new["보내기율"] is True and with_new["스와이프 안 함"] is False
    out = review.report([{**base, "sends": 9, "viewed_vs_swiped": 64.0}])
    assert "보내기율" in out and "4/7" in out
