# Script to run DirectIA tests on Windows

param(
    [switch]$Unit,
    [switch]$Integration,
    [switch]$Verbose,
    [switch]$Coverage
)

Write-Host "DirectIA Test Suite" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan
Write-Host ""

# Check if pytest is installed
try {
    $null = Get-Command pytest -ErrorAction Stop
} catch {
    Write-Host "Error: pytest not found" -ForegroundColor Red
    Write-Host "Install with: pip install pytest pytest-cov"
    exit 1
}

# Determine test path
$TestPath = "tests/"
if ($Unit) {
    $TestPath = "tests/unit/"
    Write-Host "Running unit tests..." -ForegroundColor Yellow
} elseif ($Integration) {
    $TestPath = "tests/integration/"
    Write-Host "Running integration tests..." -ForegroundColor Yellow
} else {
    Write-Host "Running all tests..." -ForegroundColor Yellow
}

# Build pytest command
$PytestArgs = @($TestPath)

if ($Verbose) {
    $PytestArgs += "-v"
} else {
    $PytestArgs += "-q"
}

if ($Coverage) {
    $PytestArgs += "--cov=src"
    $PytestArgs += "--cov-report=html"
    $PytestArgs += "--cov-report=term"
}

$PytestArgs += "--color=yes"
$PytestArgs += "--tb=short"

# Run tests
Write-Host ""
& pytest @PytestArgs

$ExitCode = $LASTEXITCODE

Write-Host ""
if ($ExitCode -eq 0) {
    Write-Host "✅ All tests passed!" -ForegroundColor Green
} else {
    Write-Host "❌ Some tests failed" -ForegroundColor Red
}

exit $ExitCode
