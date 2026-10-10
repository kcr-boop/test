# 琴译 · 开发约定

本仓库只服务于「琴译：AI 古琴打谱小程序」。产品说明见 `docs/product-spec.md`，视觉规范见 `docs/design.md`。

## 结构

- `engine/`：纯 Python 编配引擎，无第三方依赖。音高一律用 MIDI 音号；弦序在引擎内部 0 起，API 输出 1 起。
- `server/`：FastAPI，依赖 `engine`（`pip install -r server/requirements-dev.txt` 需在 `server/` 目录内执行）。
- `miniprogram/`：原生微信小程序；颜色只用 `app.wxss` 里的 CSS 变量，不写裸色值。

## 检查

```bash
pytest engine
(cd server && pytest)
```

改动编配规则时，同步更新 `engine/tests/` 和 `docs/architecture.md` 中的代价说明。

## 文案

- 界面与白话指法用简体中文，指法说法遵循“名指按七徽，勾三弦”的格式。
- 不提供曲库、不做公开分享：涉及上传内容的功能都只处理用户自己的文件。
