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

## 在 Debian 打包 Windows 和 macOS

在 Debian 本机可以打包 Linux 安装包，但通常不能直接产出 macOS 安装包；Windows 安装包也建议在 Windows 环境构建。

本仓库已提供 GitHub Actions 工作流：[.github/workflows/build-desktop.yml](.github/workflows/build-desktop.yml)

- `windows-latest` 产出：`nsis` + `msi`
- `macos-latest` 产出：`dmg` + `app`
- 同时会在对应系统内构建 Python sidecar（PyInstaller）并打入 Tauri 资源目录

使用方式：

1. 推送代码到 GitHub。
2. 打开 Actions，运行 `Build Desktop Installers`（支持手动触发 `workflow_dispatch`）。
3. 在每个 job 的 Artifacts 下载安装包。

自动发布方式：

1. 在本地创建并推送版本标签（例如 `v0.1.0`）。
2. 工作流会自动构建 Win/Mac 安装包。
3. 构建产物会自动上传到同名 GitHub Release 附件。

如果你要发布给最终用户，还需要后续补充签名与公证流程（尤其是 macOS）。

### Debian 一键发版

如果你已配置好远端（至少 `origin`），可直接使用：

```bash
make release VERSION=1.0.1
```

该命令会调用 [scripts/release.sh](scripts/release.sh)：

1. 推送当前分支到 `origin`
2. 创建并推送标签 `vVERSION`
3. 如果存在 `github` 远端，再额外推送到 `github`

这样就能在 Debian 端完成发版触发，不需要本机构建 Win/Mac。

## Gitee 方案（不依赖 GitHub）

可以，只要你的 Gitee 流水线具备原生 runner：

- Windows runner: 构建 `nsis` 和 `msi`
- macOS runner: 构建 `dmg` 和 `app`

仓库已提供通用构建脚本：[scripts/ci/build_desktop.sh](scripts/ci/build_desktop.sh)
Windows PowerShell 版本脚本：[scripts/ci/build_desktop.ps1](scripts/ci/build_desktop.ps1)
并提供可直接使用的 Gitee 工作流模板：[.gitee/workflows/build-desktop.yml](.gitee/workflows/build-desktop.yml)
以及 Gitee 镜像到 GitHub 的完整步骤：[docs/gitee-github-mirror.md](docs/gitee-github-mirror.md)

在不同 runner 上调用：

```bash
# Windows runner
pwsh -File scripts/ci/build_desktop.ps1 -Bundles "nsis,msi"

# macOS runner
bash scripts/ci/build_desktop.sh dmg,app
```

构建完成后，从以下目录收集产物并上传到你的 Gitee 制品库或发布页：

- `src-tauri/target/release/bundle/`

提示：Windows runner 推荐直接用 PowerShell 脚本；macOS runner 使用 Bash 脚本。

## 后续接入 Coqui TTS

当前 python-backend/services/tts_service.py 只是写出一个简易 wav 预览音，方便先打通目录、返回结构和播放器。后续替换为真实 Coqui TTS 时，建议保持 generate 的输入输出字段不变。
