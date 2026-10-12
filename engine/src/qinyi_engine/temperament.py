"""纯律徽位计算。

徽位用“距岳山的弦长比例”描述：一徽最靠近岳山，十三徽最靠近龙龈。
左手按在比例 f 处时，岳山一侧振动的弦长为 f，音高比散音高 1/f 倍。
"""

from __future__ import annotations

import math
from fractions import Fraction

# 一至十三徽距岳山的弦长比例
HUI_FRACTIONS: tuple[Fraction, ...] = (
    Fraction(1, 8),
    Fraction(1, 6),
    Fraction(1, 5),
    Fraction(1, 4),
    Fraction(1, 3),
    Fraction(2, 5),
    Fraction(1, 2),
    Fraction(3, 5),
    Fraction(2, 3),
    Fraction(3, 4),
    Fraction(4, 5),
    Fraction(5, 6),
    Fraction(7, 8),
)

# 距徽位在此音分以内时吸附到该徽，否则记为徽分
SNAP_CENTS = 20.0

CN_DIGITS = "〇一二三四五六七八九十"


def cents(ratio: float) -> float:
    return 1200.0 * math.log2(ratio)


def hui_fraction(hui: int) -> Fraction:
    if not 1 <= hui <= 13:
        raise ValueError(f"徽位应为 1–13，收到 {hui}")
    return HUI_FRACTIONS[hui - 1]


def pressed_ratio(hui: int) -> Fraction:
    """按在某一徽上的音高比（相对散音）。"""
    return 1 / hui_fraction(hui)


def harmonic_ratio(hui: int) -> int:
    """在某一徽点泛音得到的音高比（相对散音），即比例的分母。"""
    return hui_fraction(hui).denominator


def fraction_to_position(f: float) -> float:
    """把弦长比例换算成徽分位置，如 7.6 表示七徽到八徽之间的十分之六。

    十三徽以外（靠近龙龈）按十三徽到弦端（比例 1）之间计算，记作 13.x。
    """
    points = [float(x) for x in HUI_FRACTIONS] + [1.0]
    if f < points[0] or f > 1.0:
        raise ValueError(f"比例 {f} 超出一徽至龙龈的范围")
    for i in range(13):
        lo, hi = points[i], points[i + 1]
        if lo <= f <= hi:
            return (i + 1) + (f - lo) / (hi - lo)
    raise AssertionError("unreachable")


def position_for_semitones(semitones: float) -> float | None:
    """给定相对散音的音程（半音，十二平均），返回按音徽分位置。

    距某徽纯律音高 SNAP_CENTS 以内时吸附为整数徽位；其余四舍五入到 0.1 徽分。
    超出一徽（三个八度）时返回 None。
    """
    if semitones <= 0:
        return None
    target_cents = semitones * 100.0
    for hui in range(1, 14):
        if abs(cents(float(pressed_ratio(hui))) - target_cents) <= SNAP_CENTS:
            return float(hui)
    f = 2.0 ** (-semitones / 12.0)
    if f < float(HUI_FRACTIONS[0]):
        return None
    return round(fraction_to_position(f), 1)


def format_position(pos: float) -> str:
    """7.0 → 七徽；7.6 → 七徽六分；13.4 → 十三徽四分。"""
    hui = int(pos)
    fen = int(round((pos - hui) * 10))
    if fen == 10:
        hui, fen = hui + 1, 0
    name = _cn_number(hui) + "徽"
    return name if fen == 0 else name + CN_DIGITS[fen] + "分"


def short_position(pos: float) -> str:
    """减字谱上部的简写：七、七六、十三。"""
    hui = int(pos)
    fen = int(round((pos - hui) * 10))
    if fen == 10:
        hui, fen = hui + 1, 0
    return _cn_number(hui) + ("" if fen == 0 else CN_DIGITS[fen])


def _cn_number(n: int) -> str:
    if n <= 10:
        return CN_DIGITS[n]
    return "十" + CN_DIGITS[n - 10]
