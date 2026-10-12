import pytest

from qinyi_engine.temperament import (
    format_position,
    harmonic_ratio,
    position_for_semitones,
    pressed_ratio,
    short_position,
)


def test_hui_ratios():
    assert pressed_ratio(7) == 2
    assert pressed_ratio(9) == pytest.approx(1.5)
    assert pressed_ratio(10) == pytest.approx(4 / 3)
    assert harmonic_ratio(7) == 2
    assert harmonic_ratio(4) == harmonic_ratio(10) == 4
    assert harmonic_ratio(1) == harmonic_ratio(13) == 8


@pytest.mark.parametrize(
    "semitones, hui",
    [(12, 7.0), (7, 9.0), (5, 10.0), (4, 11.0), (9, 8.0), (24, 4.0), (19, 5.0)],
)
def test_snaps_to_hui_within_20_cents(semitones, hui):
    assert position_for_semitones(semitones) == hui


def test_between_hui_becomes_hui_fen():
    pos = position_for_semitones(2)  # 大二度：十三徽外
    assert 13.0 < pos < 14.0
    pos = position_for_semitones(10)  # 小七度：七徽与八徽之间
    assert 7.0 < pos < 8.0


def test_out_of_range():
    assert position_for_semitones(0) is None
    assert position_for_semitones(37) is None


def test_format():
    assert format_position(7.0) == "七徽"
    assert format_position(7.6) == "七徽六分"
    assert format_position(13.4) == "十三徽四分"
    assert short_position(7.6) == "七六"
    assert short_position(10.0) == "十"
