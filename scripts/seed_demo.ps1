Write-Host "Seeding AICTE Complaint Monitoring & Coordination Portal database..." -ForegroundColor Cyan
& ".\backend\.venv\Scripts\python.exe" ".\backend\seed.py"
Write-Host "Seeding complete!" -ForegroundColor Green
