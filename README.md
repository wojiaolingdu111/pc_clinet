# AI ToReder

本项目是一个运行在 PC 端本地的文字转语音桌面应用骨架，技术路线为 Vue 3 + Tauri v2 + Rust + Python + Coqui TTS。

## 当前实现

- Vue 3 + TypeScript 前端工作台
- Pinia 状态管理
- Tauri Rust 命令层骨架
- Python FastAPI 本地服务骨架
- 一个可运行的 mock TTS 生成器，用于在未接入真实 Coqui 模型前验证接口闭环
- 声音克隆 profile 的目录、元数据和接口骨架

## 目录结构

- src: 前端应用
- src-tauri: Tauri 与 Rust 代码
- python-backend: Python 本地服务
- assets/builtin-voices: 内置音色资源占位

## 开发环境

### 浏览器模式联调

当前机器没有 Rust 工具链时，可以先直接联调前端和 Python 服务：

1. 进入 python-backend 并启动本地服务。
2. 回到项目根目录执行 npm run dev。
3. 在浏览器中打开 Vite 输出地址，前端会直接请求 http://127.0.0.1:8765。

这种模式下已经可以验证：

- 服务健康检查
- 音色列表加载
- mock TTS 生成与播放
- 创建和删除自定义 voice profile

### 前端

1. 安装 Node.js 20+
2. 执行 npm install
3. 执行 npm run dev

### Python 服务

1. 进入 python-backend
2. 创建虚拟环境并安装依赖
3. 启动 python app.py

示例：

```bash
cd python-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Tauri 桌面壳

当前机器尚未安装 Rust 工具链，因此本仓库先写入了完整的 Rust/Tauri 骨架代码，但未在本地编译验证。

安装 Rust 后可执行：

```bash
npm install
npm run tauri:dev
```

## 后续接入 Coqui TTS

当前 python-backend/services/tts_service.py 只是写出一个简易 wav 预览音，方便先打通目录、返回结构和播放器。后续替换为真实 Coqui TTS 时，建议保持 generate 的输入输出字段不变。
