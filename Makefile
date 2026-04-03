PNPM ?= pnpm
PYTHON ?= python
PIP ?= $(PYTHON) -m pip

.DEFAULT_GOAL := help

.PHONY: help install install-frontend install-backend backend-dev dev dev-all build tauri-dev tauri-build build-windows build-linux build-mac build-sidecar clean

help:
	@echo "可用命令:"
	@echo "  make install            安装前后端依赖"
	@echo "  make install-frontend   安装前端依赖"
	@echo "  make install-backend    安装 Python 依赖"
	@echo "  make backend-dev        启动 Python 后端 (127.0.0.1:8765)"
	@echo "  make dev                启动前端开发服务 (Vite)"
	@echo "  make dev-all            同时启动 Python 后端 + 前端开发服务"
	@echo "  make build              构建前端产物"
	@echo "  make tauri-dev          启动 Tauri 开发模式"
	@echo "  make tauri-build        构建 Tauri 桌面应用（当前平台）"
	@echo "  make build-windows      打包 Windows 安装包 (NSIS .exe + .msi)"
	@echo "  make build-linux        打包 Linux 安装包 (.deb + .rpm + .AppImage)"
	@echo "  make build-mac          打包 macOS 安装包 (.dmg + .app)"
	@echo "  make build-sidecar      用 PyInstaller 编译 Python 后端为第一方 sidecar"
	@echo "                          (构建安装包前必须先运行此命令！)"
	@echo "  make clean              清理前端构建产物"

install: install-frontend install-backend

install-frontend:
	$(PNPM) install

install-backend:
	cd python-backend && $(PIP) install -r requirements.txt

backend-dev:
	cd python-backend && $(PYTHON) app.py

dev:
	$(PNPM) dev

dev-all:
	$(PNPM) dlx concurrently --names backend,frontend --prefix-colors cyan,green "cd python-backend && $(PYTHON) app.py" "$(PNPM) dev"

build:
	$(PNPM) build

tauri-dev:
	$(PNPM) tauri:dev

tauri-build:
	$(PNPM) tauri:build

build-windows:
	$(PNPM) tauri:build -- --bundles nsis,msi

build-linux:
	$(PNPM) tauri:build -- --bundles deb,rpm,appimage

build-mac:
	$(PNPM) tauri:build -- --bundles dmg,app

# 将 Python 后端编译为独立可执行文件（sidecar）
# 需要已安装：pip install pyinstaller
# 构建后自动将产物拷贝到 src-tauri/binaries/aitoreder-backend/
build-sidecar:
	cd python-backend && $(PYTHON) -m PyInstaller aitoreder-backend.spec --clean
	$(PYTHON) -c "import shutil, pathlib; dest=pathlib.Path('src-tauri/binaries/aitoreder-backend'); dest.mkdir(parents=True, exist_ok=True); shutil.copytree('python-backend/dist/aitoreder-backend', str(dest), dirs_exist_ok=True)"

clean:
	node -e "require('fs').rmSync('dist', { recursive: true, force: true })"
