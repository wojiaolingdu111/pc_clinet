PNPM ?= pnpm
PYTHON ?= python
PIP ?= $(PYTHON) -m pip

.DEFAULT_GOAL := help

.PHONY: help install install-frontend install-backend backend-dev dev dev-all build tauri-dev tauri-build clean

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
	@echo "  make tauri-build        构建 Tauri 桌面应用"
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

clean:
	node -e "require('fs').rmSync('dist', { recursive: true, force: true })"
