# 琴译 · AI 古琴打谱小程序

把一份五线谱或简谱，变成能直接在古琴上弹的减字谱，并用古琴声音演奏给你听；再用一句话完成伴奏和录音的音频编辑。

- 产品说明：[docs/product-spec.md](docs/product-spec.md)
- 系统架构：[docs/architecture.md](docs/architecture.md)
- 视觉规范与设计稿：[docs/design.md](docs/design.md)

## 仓库结构

| 目录 | 内容 | 状态 |
| --- | --- | --- |
| `engine/` | 古琴编配引擎（Python）：纯律徽位、散按泛候选、Viterbi 最优弹法、减字部件与白话指法 | 可用，有测试 |
| `server/` | API 服务（FastAPI，部署到微信云托管）：`POST /api/arrange` | 可用，有测试 |
| `miniprogram/` | 微信小程序前端：首页导入、琴谱页、我的琴谱，`app.wxss` 内含设计令牌 | 骨架 |
| `docs/` | 产品说明、架构、设计规范 | — |

## 本地开发

```bash
python -m venv .venv && source .venv/bin/activate
cd server && pip install -r requirements-dev.txt && cd ..

pytest engine            # 编配引擎测试
(cd server && pytest)    # API 测试
(cd server && uvicorn app.main:app --reload)   # 启动 API：http://127.0.0.1:8000/docs
```

小程序：用微信开发者工具打开 `miniprogram/`，在 `app.js` 中填写云托管环境 ID。

调用示例：

```bash
curl -X POST http://127.0.0.1:8000/api/arrange \
  -H 'content-type: application/json' \
  -d '{"notes":[{"pitch":45},{"pitch":48},{"pitch":50},{"pitch":53}],"level":"beginner","style":"guyun"}'
```

## 路线图

- [x] 编配引擎：正调、入门 / 进阶、流行 / 古韵、自动选调、走手音
- [x] 编配 API
- [ ] 识谱：MusicXML / MIDI（music21）、五线谱图片（oemer）、简谱图片（多模态大模型）
- [ ] 记谱渲染：五线谱（Verovio）、减字谱合体字（guqin-jianzipu-font）、简谱 SVG
- [ ] 古琴采样合成与跟弹高亮时间轴
- [ ] 一句话音频编辑（GC-4）：指令解析 → 截取 / 分离 / 变调 / 变速 / 降噪 / 混响 / 混音
- [ ] 异步任务队列与进度轮询
- [ ] 小程序虚拟支付（道具直购）与发货幂等
- [ ] 导出：长图、PDF、MusicXML、MP3
- [ ] 以创始人翻弹谱为标准答案的逐音一致率评测
