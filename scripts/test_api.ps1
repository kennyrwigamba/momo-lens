$baseUrl = "http://127.0.0.1:8000"
$username = "admin"
$password = "change_this_password"

Write-Host "=== GET: Authenticated request ==="
curl.exe -i -u "${username}:${password}" `
    "$baseUrl/transactions"

Write-Host "`n=== GET: Unauthorized request ==="
curl.exe -i `
    "$baseUrl/transactions"

Write-Host "`n=== POST: Create transaction ==="
curl.exe -i -u "${username}:${password}" `
    -X POST "$baseUrl/transactions" `
    -H "Content-Type: application/json" `
    --data-binary "@test_transaction.json"

Write-Host "`n=== PUT: Update transaction ==="
curl.exe -i -u "${username}:${password}" `
    -X PUT "$baseUrl/transactions/TEST001" `
    -H "Content-Type: application/json" `
    --data-binary "@test_transaction_updated.json"

Write-Host "`n=== DELETE: Delete transaction ==="
curl.exe -i -u "${username}:${password}" `
    -X DELETE "$baseUrl/transactions/TEST001"
