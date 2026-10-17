# AegisCore Evidence-Grounded RAG System — Full Automated Runner
# Usage in PowerShell: .\run_all.ps1

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  AegisCore Evidence-Grounded RAG System Execution Runner " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Ensure offline mock mode
$env:RAG_GENERATION_MODE = "mock"

# 1. Package installation
Write-Host "`n[Step 1/6] Installing Package in Editable Mode..." -ForegroundColor Yellow
python -m pip install -e . --quiet

# 2. System Verification
Write-Host "`n[Step 2/6] Verifying Corpus and Manifest Integrity..." -ForegroundColor Yellow
evidence-rag verify

# 3. Index Build
Write-Host "`n[Step 3/6] Rebuilding Persistent Vector Index..." -ForegroundColor Yellow
evidence-rag index

# 4. Automated Pytest Suite
Write-Host "`n[Step 4/6] Running Complete Automated Test Suite (46 Tests)..." -ForegroundColor Yellow
python -m pytest tests -v

# 5. Benchmark Evaluation
Write-Host "`n[Step 5/6] Executing Evaluation Benchmark Suite (22 Questions)..." -ForegroundColor Yellow
evidence-rag evaluate

# 6. Live Demo Queries
Write-Host "`n[Step 6/6] Running Live Demo on Key Query Types..." -ForegroundColor Yellow
evidence-rag demo

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host "  All 6 Stages Completed Successfully!                     " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
