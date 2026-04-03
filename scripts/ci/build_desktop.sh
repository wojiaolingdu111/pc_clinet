#!/usr/bin/env bash
set -euo pipefail

# Unified desktop packaging script for CI runners.
# Usage:
#   scripts/ci/build_desktop.sh nsis,msi
#   scripts/ci/build_desktop.sh dmg,app

BUNDLES="${1:-all}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

cd "$ROOT_DIR"

echo "[1/5] Install frontend dependencies"
pnpm install --frozen-lockfile

echo "[2/5] Install Python dependencies for sidecar"
python -m pip install --upgrade pip
python -m pip install -r python-backend/requirements.txt pyinstaller

echo "[3/5] Build Python sidecar"
(
  cd python-backend
  python -m PyInstaller aitoreder-backend.spec --clean --distpath ../src-tauri/binaries
)

echo "[4/5] Verify sidecar resources"
ls -la src-tauri/binaries
ls -la src-tauri/binaries/aitoreder-backend

echo "[5/5] Build Tauri bundles: ${BUNDLES}"
pnpm exec tauri build --bundles "$BUNDLES"

echo "Done. Bundles are in src-tauri/target/release/bundle"
