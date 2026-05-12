$body = @{
    test_case_id = 1
    headless = $true
    timeout = 30
    retry_count = 3
    screenshot_quality = 80
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/api/v2/execute" -Method Post -Body $body -ContentType "application/json"
