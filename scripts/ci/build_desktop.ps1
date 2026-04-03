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
python -m PyInstaller aitoreder-backend.spec --clean --distpath ../src-tauri/binaries
Pop-Location

Write-Host "[4/5] Verify sidecar resources"
Get-ChildItem src-tauri/binaries | Format-Table -AutoSize
Get-ChildItem src-tauri/binaries/aitoreder-backend | Format-Table -AutoSize

Write-Host "[5/5] Build Tauri bundles: $Bundles"
pnpm exec tauri build --bundles $Bundles

Write-Host "Done. Bundles are in src-tauri/target/release/bundle"
