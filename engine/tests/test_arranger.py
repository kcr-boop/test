import pytest

from qinyi_engine import (
    ArrangementError,
    Level,
    Note,
    Style,
    Technique,
    arrange,
    candidates,
    choose_transposition,
)

# 茉莉花开头（1=F）：3 3 5 6 1̇ 1̇ 6 5
A2, C3, D3, F3 = 45, 48, 50, 53
MOLIHUA = [Note(p) for p in (A2, A2, C3, D3, F3, F3, D3, C3)]


def test_open_string_candidate():
    cs = candidates(41)  # 三弦散音 F
    assert any(c.technique is Technique.OPEN and c.string == 2 for c in cs)


def test_beginner_has_no_harmonics_or_high_positions():
    for pitch in range(36, 75):
        for c in candidates(pitch, level=Level.BEGINNER):
            assert c.technique is not Technique.HARMONIC
            if c.technique is Technique.PRESSED:
                assert c.position >= 7.0


def test_prefers_open_strings():
    out = arrange([Note(36), Note(38), Note(41)])
    assert [p.technique for p in out] == [Technique.OPEN] * 3
    assert [p.string for p in out] == [0, 1, 2]


def test_arrange_molihua_is_playable_and_explained():
    out = arrange(MOLIHUA, level=Level.BEGINNER)
    assert len(out) == len(MOLIHUA)
    for p in out:
        assert p.explain()
        assert p.jianzi()["top"]
    f_notes = [p for p in out if p.note.pitch == F3]
    assert all(p.technique is Technique.PRESSED for p in f_notes)


def test_explain_text():
    out = arrange([Note(53)], level=Level.BEGINNER)  # 三弦七徽 = 高八度 F
    assert out[0].explain() == "名指按七徽，勾三弦"
    assert out[0].jianzi() == {"top": "夕七", "right": "勹", "string": "三"}


def test_repeated_note_alternates_mo_tiao_on_high_strings():
    out = arrange([Note(50), Note(50), Note(50)])
    assert [p.right_finger for p in out] == ["抹", "挑", "抹"]


def test_guyun_uses_slide_on_same_string():
    # 三弦七徽 F 之后同弦下行：古韵 + 进阶应走手
    # 第二个音选只能按出的降 E（D3 有七弦散音，不会走手）
    out = arrange([Note(53), Note(51)], level=Level.ADVANCED, style=Style.GUYUN)
    assert out[1].slide == "下"
    assert out[1].right_finger is None
    assert "走手音" in out[1].explain()


def test_pop_style_never_slides():
    out = arrange([Note(53), Note(51)], level=Level.ADVANCED, style=Style.POP)
    assert all(p.slide is None for p in out)


def test_unplayable_note_raises():
    with pytest.raises(ArrangementError) as e:
        arrange([Note(36), Note(20)])
    assert e.value.index == 1


def test_choose_transposition_moves_into_range():
    low = [Note(p) for p in (24, 26, 29)]  # 比一弦低一个八度
    shift = choose_transposition(low)
    assert shift == 12
