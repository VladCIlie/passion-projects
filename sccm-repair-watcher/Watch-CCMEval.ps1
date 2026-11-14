# Watches the SCCM client evaluation log and, when a known WMI failure
# signature appears in the penultimate line, runs an automatic two-stage
# client repair (full repair, then WMI repair).
#
# Requires: Repair-SCCMClient.ps1 in the same directory.

$logPath   = 'C:\Windows\CCM\Logs\CCMEval.log'
$targetText = '<![LOG[Failed to get MDM_ConfigSetting instance, 0x80041013]LOG]!>'

Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Starting watcher..." -ForegroundColor Cyan
Write-Host "Checking log file: $logPath" -ForegroundColor Gray

if (-not (Test-Path $logPath)) {
    Write-Host "Log file not found: $logPath" -ForegroundColor Red
    Read-Host 'Press Enter to close'
    exit 1
}

$lastTwoLines = Get-Content -Path $logPath -Tail 2

if ($lastTwoLines.Count -lt 2) {
    Write-Host 'Log file does not contain enough lines.' -ForegroundColor Yellow
    Read-Host 'Press Enter to close'
    exit 1
}

$penultimateLine = $lastTwoLines[0]

Write-Host 'Penultimate line found:' -ForegroundColor Gray
Write-Host $penultimateLine -ForegroundColor DarkGray

$matchDetected = ($null -ne $penultimateLine) -and $penultimateLine.Contains($targetText)

if ($matchDetected) {
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Match detected." -ForegroundColor Green
    Write-Host 'Running full client repair...' -ForegroundColor Magenta

    Set-Location -Path $PSScriptRoot
    & .\Repair-SCCMClient.ps1 Full

    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Full repair finished. Running WMI repair." -ForegroundColor Gray

    Set-Location -Path $PSScriptRoot
    & .\Repair-SCCMClient.ps1 WMI

    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Repair sequence finished." -ForegroundColor Green
}
else {
    Write-Host 'No match found. Repair was not triggered.' -ForegroundColor Yellow
}

Read-Host 'Done. Press Enter to close'
