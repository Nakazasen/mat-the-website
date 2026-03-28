$ErrorActionPreference = "Stop"

Write-Host "Running mojibake scan on staged files..." -ForegroundColor Cyan
py -3 scripts/check_mojibake.py --staged
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host "Pre-commit mojibake scan passed." -ForegroundColor Green
