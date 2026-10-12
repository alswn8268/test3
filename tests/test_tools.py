import copy

import pytest
from tools import assemble, factcheck, new_episode, post, review, validate
from tools.common import EPISODES, load_script, plain, timeline

EPS = sorted(p.name for p in EPISODES.glob("ep*") if (p / "script.json").exists())


@pytest.mark.parametrize("ep", EPS)
def test_existing_episodes_have_no_errors(ep):
    errors, _ = validate.check(load_script(ep))
    assert errors == []


def test_validate_catches_broken_script():
    data = copy.deepcopy(load_script("ep01"))
    data["scenes"] = data["scenes"][:-1]  # CTA 빠짐 → 11장면, 27초
    data["scenes"][2]["say"] = ""
    errors, _ = validate.check(data)
    text = "\n".join(errors)
    assert "장면 수 11개" in text and "총 길이" in text and "cta" in text and "say" in text


def test_validate_warns_long_line_and_double_highlight():
    data = copy.deepcopy(load_script("ep01"))
    data["scenes"][1]["lines"] = ["아주아주아주아주긴한줄입니다", "[하나] [둘]"]
    _, warns = validate.check(data)
    assert any("글자" in w for w in warns) and any("강조 2개" in w for w in warns)


def test_new_episode_template_is_valid():
    errors, _ = validate.check(new_episode.template("ep99_x", "상시 · 통장 관리", "테스트"))
    assert errors == []


def test_plain_strips_markup():
    assert plain("연봉의 [25%] {0원}") == "연봉의 25% 0원"


def test_factcheck_extracts_numbers_and_skips_numbering_labels():
    claims = factcheck.claims(load_script("ep01"))
    texts = [t for _, t in claims]
    assert (1, "연봉의 25%") in claims
    assert not any(t.startswith("01  ") for t in texts)


def test_factcheck_keeps_existing_sources_and_checks():
    data = load_script("ep01")
    md = factcheck.build(data)
    assert len(factcheck.problems(md)) == len(factcheck.claims(data))
    filled = md.replace("| 01 | 연봉의 25% |  | ☐ |", "| 01 | 연봉의 25% | https://www.nts.go.kr | ✅ |")
    rebuilt = factcheck.build(data, filled)
    assert "| 연봉의 25% | https://www.nts.go.kr | ✅ |" in rebuilt
    assert len(factcheck.problems(rebuilt)) == len(factcheck.claims(data)) - 1


def test_srt_follows_scene_timeline():
    scenes = load_script("ep01")["scenes"]
    srt = assemble.build_srt(scenes)
    assert srt.startswith("1\n00:00:00,000 --> 00:00:03,000\n")
    assert "12\n00:00:27,000 --> 00:00:30,000\n" in srt
    assert timeline(scenes)[-1][1] == pytest.approx(30.0)


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


def test_post_caption_rules():
    md = post.build(load_script("ep01"), "12", ["연말정산", "직장인", "카드공제", "체크카드"])
    lines = md.splitlines()
    i = lines.index("## 캡션")
    assert lines[i + 1] == "연봉의 25% 이 숫자 모르면 카드 공제 0원"
    assert lines[i + 2] == "저장해두고 12월에 다시 보기"
    assert "#연말정산 #직장인 #카드공제 #체크카드 #월급사용설명서" in md
