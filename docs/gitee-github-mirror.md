# Gitee Mirror to GitHub

目标：代码主仓库放在 Gitee，使用 GitHub Actions 免费构建 Windows/macOS 安装包。

## 1. 准备 GitHub 仓库

1. 在 GitHub 新建同名仓库（建议私有）。
2. 确认仓库中存在工作流文件：[.github/workflows/build-desktop.yml](../.github/workflows/build-desktop.yml)。

## 2. 在 Gitee 配置镜像推送

在 Gitee 仓库页面配置“仓库镜像”或“同步到外部仓库”：

1. 目标仓库地址填 GitHub 仓库 URL。
2. 认证方式使用 GitHub PAT（建议仅授予 `repo` 所需权限）。
3. 开启自动同步分支和标签。

如果你习惯命令行，也可以在本地双远端推送：

```bash
git remote add github <你的 GitHub 仓库地址>
git push github <你的分支>
git push github --tags
```

## 3. 触发构建

工作流触发条件在 [.github/workflows/build-desktop.yml](../.github/workflows/build-desktop.yml)：

- 手动触发：`workflow_dispatch`
- 标签触发：`v*`

推荐发布流程：

```bash
git tag v1.0.0
git push origin v1.0.0
```

如果已配置 Gitee 自动镜像，标签会同步到 GitHub 并触发构建。

## 4. 产物位置

1. GitHub Actions 运行页面的 Artifacts。
2. 对 `v*` 标签，还会自动上传到同名 GitHub Release 附件。

## 5. 常见问题

1. 标签已推送但未触发构建：

- 检查 GitHub 是否收到标签（`v*`）
- 检查镜像是否启用“同步标签”

2. 工作流无权限上传 Release：

- 检查 `permissions.contents` 是否为 `write`

3. macOS 包缺失：

- `tauri` 常输出 `.dmg` 与 `.app.tar.gz`，已在工作流上传模式中覆盖
