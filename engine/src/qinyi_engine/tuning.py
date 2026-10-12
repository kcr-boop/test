"""古琴定弦。音高用 MIDI 音号表示。"""

from __future__ import annotations

from dataclasses import dataclass

STRING_NAMES = ("一", "二", "三", "四", "五", "六", "七")


@dataclass(frozen=True)
class Tuning:
    name: str
    open_pitches: tuple[int, ...]  # 一弦到七弦
    gong: int  # 宫音（简谱 1）的音级，0=C

    def __post_init__(self) -> None:
        if len(self.open_pitches) != 7:
            raise ValueError("古琴定弦需要七根弦")


# 正调：C D F G A c d，宫音为 F（简谱 5 6 1 2 3 5 6）
ZHENG_DIAO = Tuning(name="正调", open_pitches=(36, 38, 41, 43, 45, 48, 50), gong=5)

TUNINGS = {"zheng": ZHENG_DIAO}
