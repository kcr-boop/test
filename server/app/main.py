"""琴译 API 服务（部署在微信云托管）。

当前提供编配接口；识谱、渲染、合成与音频编辑等耗时任务后续以异步任务接入，前端轮询进度。
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from qinyi_engine import (
    TUNINGS,
    ArrangementError,
    Level,
    Note,
    Style,
    arrange,
    choose_transposition,
)

app = FastAPI(title="琴译 API", version="0.1.0")


class NoteIn(BaseModel):
    pitch: int = Field(ge=0, le=127, description="MIDI 音号")
    duration: float = Field(default=1.0, gt=0, description="时值（拍）")


class ArrangeRequest(BaseModel):
    notes: list[NoteIn] = Field(min_length=1, max_length=4000)
    tuning: str = "zheng"
    level: Level = Level.BEGINNER
    style: Style = Style.POP
    auto_key: bool = True


class PlacementOut(BaseModel):
    pitch: int
    duration: float
    string: int = Field(description="1 = 一弦")
    technique: str
    position: float | None
    left_finger: str | None
    right_finger: str | None
    slide: str | None
    jianzi: dict[str, str]
    explain: str


class ArrangeResponse(BaseModel):
    transpose: int = Field(description="相对原曲移调的半音数")
    placements: list[PlacementOut]


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/arrange", response_model=ArrangeResponse)
def arrange_melody(req: ArrangeRequest) -> ArrangeResponse:
    tuning = TUNINGS.get(req.tuning)
    if tuning is None:
        raise HTTPException(status_code=422, detail=f"不支持的定弦：{req.tuning}")
    notes = [Note(n.pitch, n.duration) for n in req.notes]
    try:
        shift = choose_transposition(notes, tuning, req.level, req.style) if req.auto_key else 0
        notes = [Note(n.pitch + shift, n.duration) for n in notes]
        placements = arrange(notes, tuning, req.level, req.style)
    except ArrangementError as e:
        raise HTTPException(status_code=422, detail={"message": str(e), "index": e.index}) from e
    return ArrangeResponse(
        transpose=shift,
        placements=[
            PlacementOut(
                pitch=p.note.pitch,
                duration=p.note.duration,
                string=p.string + 1,
                technique=p.technique.value,
                position=p.position,
                left_finger=p.left_finger,
                right_finger=p.right_finger,
                slide=p.slide,
                jianzi=p.jianzi(),
                explain=p.explain(),
            )
            for p in placements
        ],
    )
