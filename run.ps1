$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

function Stop-ProjectProcesses {
    $targets = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object {
            $_.Name -match '^python(\.exe)?$' -and (
                $_.CommandLine -match 'app\.main:app' -or
                $_.CommandLine -match 'spawn_main\(parent_pid=' -or
                $_.CommandLine -match 'run\.ps1' -or
                $_.CommandLine -match 'uvicorn app\.main:app'
            )
        }

    foreach ($proc in $targets) {
        Write-Host "Stopping project process (PID $($proc.ProcessId))..."
        Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
    }

    $deadline = (Get-Date).AddSeconds(10)
    do {
        $active = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
            Where-Object {
                $_.Name -match '^python(\.exe)?$' -and (
                    $_.CommandLine -match 'app\.main:app' -or
                    $_.CommandLine -match 'spawn_main\(parent_pid=' -or
                    $_.CommandLine -match 'uvicorn app\.main:app'
                )
            }

        if (-not $active) {
            break
        }

        Start-Sleep -Milliseconds 250
    } while ((Get-Date) -lt $deadline)
}

Stop-ProjectProcesses

$listenerPids = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty OwningProcess -Unique

if ($listenerPids) {
    foreach ($procId in $listenerPids) {
        Write-Host "Stopping process still listening on port 8000 (PID $procId)..."
        Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
    }

    $deadline = (Get-Date).AddSeconds(10)
    while ((Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue) -and (Get-Date) -lt $deadline) {
        Start-Sleep -Milliseconds 250
    }
}

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
}

if (-not (Test-Path $python)) {
    throw "Virtual environment not found. Expected .venv\Scripts\python.exe or venv\Scripts\python.exe"
}

Write-Host "Starting Analytics Service on http://26.52.94.169:8000/"
& $python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
