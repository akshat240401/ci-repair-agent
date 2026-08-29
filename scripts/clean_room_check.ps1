param(
    [string]$RepoUrl = "https://github.com/akshat240401/ci-repair-agent.git",
    [string]$Ref = "feat/evaluation-harness",
    [string]$WorkDir = "$env:TEMP\ci-repair-agent-clean-room",
    [switch]$RunApiSmoke
)

$ErrorActionPreference = "Stop"

function Invoke-Checked {
    param(
        [Parameter(Mandatory=$true)]
        [scriptblock]$Command,
        [Parameter(Mandatory=$true)]
        [string]$Label
    )

    & $Command

    if ($LASTEXITCODE -ne 0) {
        throw "$Label failed with exit code $LASTEXITCODE"
    }
}

Write-Host "=== CLEAN ROOM REPRODUCTION CHECK ==="

if (Test-Path $WorkDir) {
    Write-Host "Removing previous clean-room directory: $WorkDir"
    Remove-Item -Recurse -Force $WorkDir
}

Write-Host "Cloning $RepoUrl"
Invoke-Checked -Label "git clone" -Command {
    git clone $RepoUrl $WorkDir
}

Push-Location $WorkDir
try {
    Write-Host "Checking out: $Ref"
    Invoke-Checked -Label "git checkout" -Command {
        git checkout $Ref
    }

    Write-Host "Creating Python 3.11 virtual environment"
    Invoke-Checked -Label "venv creation" -Command {
        py -3.11 -m venv .venv
    }

    $python = Join-Path $WorkDir ".venv\Scripts\python.exe"

    Write-Host "Installing package from clean checkout"
    Invoke-Checked -Label "pip upgrade" -Command {
        & $python -m pip install --upgrade pip
    }

    Invoke-Checked -Label "package install" -Command {
        & $python -m pip install -e .
    }

    Invoke-Checked -Label "dev dependency install" -Command {
        & $python -m pip install -r requirements-dev.txt
    }

    Write-Host "Running deterministic test suite"
    Invoke-Checked -Label "pytest" -Command {
        & $python -m pytest -q tests
    }

    Write-Host "Inspecting benchmark"
    Invoke-Checked -Label "benchmark inspection" -Command {
        & $python -m evaluation.evaluator --mode inspect
    }

    Write-Host "Generating evidence report"
    Invoke-Checked -Label "evidence report" -Command {
        & $python -m evaluation.evidence_report
    }

    Write-Host "Generating cost report"
    Invoke-Checked -Label "cost report" -Command {
        & $python -m evaluation.submission_cost_report
    }

    Write-Host "Exporting trajectories"
    Invoke-Checked -Label "trajectory export" -Command {
        & $python -m evaluation.export_trajectories
    }

    if ($RunApiSmoke) {
        if (-not $env:OPENAI_API_KEY) {
            throw "RunApiSmoke requested but OPENAI_API_KEY is not set."
        }

        Write-Host "Running one API-backed advanced repair smoke case"
        Invoke-Checked -Label "API smoke runner" -Command {
            & $python -m evaluation.repair_loop_experiment --case case_010
        }

        $summaryPath = Join-Path $WorkDir "results\smoke\repair_loop\summary.json"
        if (-not (Test-Path $summaryPath)) {
            throw "API smoke summary was not created: $summaryPath"
        }

        $summary = Get-Content $summaryPath -Raw | ConvertFrom-Json

        if ($summary.cases -ne 1) {
            throw "API smoke expected exactly 1 case, got $($summary.cases)."
        }

        if ($summary.verified_repair_rate -ne 1.0) {
            throw (
                "API smoke did not verify the repair. " +
                "VRR=$($summary.verified_repair_rate); " +
                "unresolved=$($summary.unresolved_cases -join ',')"
            )
        }
    }

    Write-Host ""
    Write-Host "=== CLEAN ROOM CHECK PASSED ==="
    Write-Host "Checkout: $WorkDir"
}
finally {
    Pop-Location
}
