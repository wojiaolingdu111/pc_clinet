param(
    [string]$Bundles = "all"
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Resolve-Path (Join-Path $ScriptDir "../..")
Set-Location $RootDir

Write-Host "[1/5] Install frontend dependencies"
pnpm install --frozen-lockfile

Write-Host "[2/5] Install Python dependencies for sidecar"
python -m pip install --upgrade pip
python -m pip install -r python-backend/requirements.txt pyinstaller

Write-Host "[3/5] Build Python sidecar"
Push-Location python-backend
python -m PyInstaller aitoreder-backend.spec --clean
Pop-Location

Write-Host "[4/5] Copy sidecar to Tauri resources"
python -c "import pathlib, shutil; src=pathlib.Path('python-backend/dist/aitoreder-backend'); dest=pathlib.Path('src-tauri/binaries/aitoreder-backend'); dest.mkdir(parents=True, exist_ok=True); shutil.copytree(src, dest, dirs_exist_ok=True)"

Write-Host "[5/5] Build Tauri bundles: $Bundles"
pnpm exec tauri build --bundles $Bundles

Write-Host "Done. Bundles are in src-tauri/target/release/bundle"
