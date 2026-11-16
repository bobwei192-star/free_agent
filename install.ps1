#Requires -Version 5.1
<#
.SYNOPSIS
    Free_Agent 安装器（Windows PowerShell）
.DESCRIPTION
    检查 Python、生成 fa.cmd 启动器、把启动器目录加入用户 PATH。
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\install.ps1
.EXAMPLE
    .\install.ps1 -Doctor
#>
[CmdletBinding()]
param(
    [string]$BinDir = "$HOME\.local\bin",
    [switch]$Doctor
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

function Write-Info($Message) { Write-Host "  $Message" }
function Write-Ok($Message) { Write-Host "  " -NoNewline; Write-Host "OK" -ForegroundColor Green -NoNewline; Write-Host " $Message" }
function Fail($Message) { Write-Host "  X $Message" -ForegroundColor Red; exit 1 }

Write-Host "Free_Agent installer" -ForegroundColor White
Write-Info "目录  $Root"
Write-Info "平台  Windows $([System.Environment]::OSVersion.Version) / $env:PROCESSOR_ARCHITECTURE"

# ---------------------------------------------------------------- Python
$pythonExe = $null
$pythonPrefix = @()

$pyLauncher = Get-Command py -ErrorAction SilentlyContinue
if ($pyLauncher) {
    try {
        & py -3 -c "import sys" 2>$null
        if ($LASTEXITCODE -eq 0) {
            $pythonExe = $pyLauncher.Source
            $pythonPrefix = @("-3")
        }
    } catch {
        # py 启动器存在但 Python 3 未安装
    }
}

if (-not $pythonExe) {
    foreach ($name in @("python", "python3")) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd -and $cmd.Source -notmatch "WindowsApps") {
            $pythonExe = $cmd.Source
            $pythonPrefix = @()
            break
        }
    }
}

if (-not $pythonExe) {
    Fail "未找到 Python 3.9+。先执行: winget install Python.Python.3.12"
}

& $pythonExe @pythonPrefix -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)"
if ($LASTEXITCODE -ne 0) {
    Fail "Python 版本过低（需要 3.9+）：$(& $pythonExe @pythonPrefix --version 2>&1)"
}
Write-Ok "Python  $(& $pythonExe @pythonPrefix --version 2>&1)"

# ---------------------------------------------------------------- 启动器
if (-not (Test-Path -LiteralPath $BinDir)) {
    New-Item -ItemType Directory -Path $BinDir -Force | Out-Null
}

$launcher = Join-Path $BinDir "fa.cmd"
$runCommand = if ($pythonPrefix.Count -gt 0) { "py -3" } else { '"' + $pythonExe + '"' }
$content = @(
    "@echo off",
    "setlocal",
    "set `"PYTHONPATH=$Root;%PYTHONPATH%`"",
    "$runCommand -m fa %*"
) -join "`r`n"
Set-Content -LiteralPath $launcher -Value $content -Encoding ASCII
Write-Ok "启动器  $launcher"

# ---------------------------------------------------------------- PATH
$userPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
$parts = @()
if ($userPath) { $parts = $userPath -split ";" | Where-Object { $_ } }
if ($parts -notcontains $BinDir) {
    $newPath = (@($parts) + $BinDir) -join ";"
    [System.Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    Write-Ok "已把 $BinDir 加入用户 PATH（重开终端生效）"
}
$env:Path = "$BinDir;$env:Path"
$env:PYTHONPATH = "$Root;$env:PYTHONPATH"

# ---------------------------------------------------------------- 自检
try {
    & $launcher version
} catch {
    Fail "启动器自检失败：$_"
}

Write-Host ""
Write-Host "安装完成" -ForegroundColor White
Write-Info "fa list                查看工具与安装状态"
Write-Info "fa install cli         安装全部终端 Agent"
Write-Info "fa doctor --net        体检环境与网络"
Write-Info "fa proxy               查看 PowerShell 代理写法"

if ($Doctor) {
    Write-Host ""
    & $launcher doctor --net
}
