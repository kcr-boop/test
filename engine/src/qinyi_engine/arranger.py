"""古琴编配引擎：为旋律中的每个音选定弦、徽位与散按泛，并配置左右手指法。

整首曲当作一条路径：每个音有若干候选弹法，相邻两音之间的转移代价反映左手移动、
换弦和弹法切换的难度，用 Viterbi 求总代价最小的一条。水平与风格只改变约束和代价权重。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from .temperament import (
    SNAP_CENTS,
    cents,
    format_position,
    harmonic_ratio,
    position_for_semitones,
    short_position,
)
from .tuning import STRING_NAMES, ZHENG_DIAO, Tuning


class Technique(str, Enum):
    OPEN = "san"  # 散音
    PRESSED = "an"  # 按音
    HARMONIC = "fan"  # 泛音


class Level(str, Enum):
    BEGINNER = "beginner"  # 入门：只用散音与七徽以下的按音
    ADVANCED = "advanced"  # 进阶：按音、泛音与走手音


class Style(str, Enum):
    POP = "pop"  # 流行
    GUYUN = "guyun"  # 古韵


@dataclass(frozen=True)
class Note:
    pitch: int  # MIDI 音号
    duration: float = 1.0  # 拍


@dataclass(frozen=True)
class Candidate:
    string: int  # 0 = 一弦
    technique: Technique
    position: float | None = None  # 徽分位置；散音为 None


@dataclass(frozen=True)
class Weights:
    pressed: float = 1.0
    harmonic: float = 1.5
    high_register: float = 0.6  # 四徽以上每徽的额外代价
    string_jump: float = 0.35
    hand_move: float = 0.5
    switch: float = 0.4
    slide_bonus: float = 0.0  # 同弦按音相连改为走手音时减去的代价


STYLE_WEIGHTS = {
    Style.POP: Weights(),
    Style.GUYUN: Weights(harmonic=0.8, slide_bonus=1.2, switch=0.2),
}

BEGINNER_MIN_POSITION = 7.0
MAX_SLIDE_SEMITONES = 4

LEFT_ABBR = {"大指": "大", "食指": "亻", "中指": "中", "名指": "夕"}
RIGHT_ABBR = {"勾": "勹", "挑": "乚", "抹": "木"}


class ArrangementError(ValueError):
    def __init__(self, index: int, pitch: int):
        super().__init__(f"第 {index + 1} 个音（MIDI {pitch}）在当前定弦和水平下无法弹奏")
        self.index = index
        self.pitch = pitch


@dataclass(frozen=True)
class Placement:
    note: Note
    string: int
    technique: Technique
    position: float | None
    left_finger: str | None
    right_finger: str | None  # 走手音为 None
    slide: str | None = None  # "上" / "下"

    @property
    def string_name(self) -> str:
        return STRING_NAMES[self.string]

    def jianzi(self) -> dict[str, str]:
        """减字的三个部件：上部（左手 + 徽位）、右手指法、弦序。"""
        if self.slide:
            return {"top": self.slide + short_position(self.position), "right": "", "string": ""}
        if self.technique is Technique.OPEN:
            top = "艹"
        elif self.technique is Technique.HARMONIC:
            top = "泛" + LEFT_ABBR[self.left_finger] + short_position(self.position)
        else:
            top = LEFT_ABBR[self.left_finger] + short_position(self.position)
        return {"top": top, "right": RIGHT_ABBR[self.right_finger], "string": self.string_name}

    def explain(self) -> str:
        """白话说明，如“名指按七徽，勾三弦”。"""
        if self.slide:
            return f"{self.left_finger}不离弦，{self.slide}至{format_position(self.position)}（走手音，右手不弹）"
        pluck = f"{self.right_finger}{self.string_name}弦"
        if self.technique is Technique.OPEN:
            return f"散音，{pluck}"
        if self.technique is Technique.HARMONIC:
            return f"泛音，{self.left_finger}点{format_position(self.position)}，{pluck}"
        return f"{self.left_finger}按{format_position(self.position)}，{pluck}"


def candidates(pitch: int, tuning: Tuning = ZHENG_DIAO, level: Level = Level.ADVANCED) -> list[Candidate]:
    out: list[Candidate] = []
    for s, open_pitch in enumerate(tuning.open_pitches):
        interval = pitch - open_pitch
        if interval == 0:
            out.append(Candidate(s, Technique.OPEN))
            continue
        pos = position_for_semitones(interval)
        if pos is not None and (level is Level.ADVANCED or pos >= BEGINNER_MIN_POSITION):
            out.append(Candidate(s, Technique.PRESSED, pos))
        if level is Level.ADVANCED and interval > 0:
            for hui in range(1, 14):
                if abs(cents(harmonic_ratio(hui)) - interval * 100) <= SNAP_CENTS:
                    out.append(Candidate(s, Technique.HARMONIC, float(hui)))
    return out


def _emission(c: Candidate, w: Weights) -> float:
    if c.technique is Technique.OPEN:
        return 0.0
    if c.technique is Technique.HARMONIC:
        return w.harmonic
    return w.pressed + max(0.0, 4.0 - c.position) * w.high_register


def _can_slide(a: Candidate, b: Candidate, pa: int, pb: int, level: Level) -> bool:
    return (
        level is Level.ADVANCED
        and a.technique is Technique.PRESSED
        and b.technique is Technique.PRESSED
        and a.string == b.string
        and 0 < abs(pa - pb) <= MAX_SLIDE_SEMITONES
    )


def _transition(a: Candidate, b: Candidate, pa: int, pb: int, w: Weights, level: Level) -> float:
    cost = w.string_jump * abs(a.string - b.string)
    if a.position is not None and b.position is not None:
        cost += w.hand_move * abs(a.position - b.position)
    if a.technique is not b.technique:
        cost += w.switch
    if _can_slide(a, b, pa, pb, level):
        cost -= w.slide_bonus
    return cost


def _viterbi(
    notes: Sequence[Note], tuning: Tuning, level: Level, w: Weights
) -> tuple[float, list[Candidate]]:
    layers = []
    for i, n in enumerate(notes):
        cs = candidates(n.pitch, tuning, level)
        if not cs:
            raise ArrangementError(i, n.pitch)
        layers.append(cs)

    cost = [_emission(c, w) for c in layers[0]]
    back: list[list[int]] = []
    for i in range(1, len(layers)):
        pa, pb = notes[i - 1].pitch, notes[i].pitch
        new_cost, ptr = [], []
        for b in layers[i]:
            best_j = min(
                range(len(layers[i - 1])),
                key=lambda j: cost[j] + _transition(layers[i - 1][j], b, pa, pb, w, level),
            )
            ptr.append(best_j)
            new_cost.append(
                cost[best_j] + _transition(layers[i - 1][best_j], b, pa, pb, w, level) + _emission(b, w)
            )
        cost, back = new_cost, back + [ptr]

    k = min(range(len(cost)), key=cost.__getitem__)
    total = cost[k]
    path = [layers[-1][k]]
    for i in range(len(layers) - 1, 0, -1):
        k = back[i - 1][k]
        path.append(layers[i - 1][k])
    path.reverse()
    return total, path


def _left_finger(c: Candidate) -> str | None:
    if c.technique is Technique.OPEN:
        return None
    if c.technique is Technique.HARMONIC:
        return "大指"
    return "名指" if c.position >= 7.0 else "大指"


def arrange(
    notes: Sequence[Note],
    tuning: Tuning = ZHENG_DIAO,
    level: Level = Level.BEGINNER,
    style: Style = Style.POP,
) -> list[Placement]:
    if not notes:
        return []
    w = STYLE_WEIGHTS[style]
    _, path = _viterbi(notes, tuning, level, w)

    out: list[Placement] = []
    last_pluck: Placement | None = None
    for i, (n, c) in enumerate(zip(notes, path)):
        prev = path[i - 1] if i else None
        if prev is not None and w.slide_bonus > 0 and _can_slide(prev, c, notes[i - 1].pitch, n.pitch, level):
            slide = "上" if n.pitch > notes[i - 1].pitch else "下"
            out.append(Placement(n, c.string, c.technique, c.position, out[-1].left_finger, None, slide))
            continue
        if last_pluck is not None and last_pluck.string == c.string and last_pluck.right_finger == "抹":
            right = "挑"
        elif c.string >= 5:
            right = "抹"
        else:
            right = "勾"
        p = Placement(n, c.string, c.technique, c.position, _left_finger(c), right)
        out.append(p)
        last_pluck = p
    return out


def choose_transposition(
    notes: Sequence[Note],
    tuning: Tuning = ZHENG_DIAO,
    level: Level = Level.BEGINNER,
    style: Style = Style.POP,
    max_shift: int = 12,
) -> int:
    """在 ±max_shift 半音内找使整首编配总代价最小的移调；同代价取移动最小者。"""
    w = STYLE_WEIGHTS[style]
    best: tuple[float, int, int] | None = None
    for shift in range(-max_shift, max_shift + 1):
        shifted = [Note(n.pitch + shift, n.duration) for n in notes]
        try:
            total, _ = _viterbi(shifted, tuning, level, w)
        except ArrangementError:
            continue
        key = (round(total, 6), abs(shift), shift)
        if best is None or key < best:
            best = key
    if best is None:
        raise ArrangementError(0, notes[0].pitch if notes else 0)
    return best[2]
