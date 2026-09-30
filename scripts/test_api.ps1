$root = Split-Path -Parent $PSScriptRoot
$baseUrl = "http://127.0.0.1:8000"
$sample = "$root/examples/complex_transaction.json"

Write-Host "=== GET /transactions (authenticated) ==="
curl.exe -i -u admin:password "$baseUrl/transactions/76662021700"

Write-Host "`n=== GET /transactions (unauthorized) ==="
curl.exe -i "$baseUrl/transactions"

Write-Host "`n=== POST /transactions ==="
curl.exe -i -u admin:password `
    -X POST "$baseUrl/transactions" `
    -H "Content-Type: application/json" `
    --data-binary "@$sample"

Write-Host "`n=== PUT /transactions/13947830000 ==="
curl.exe -i -u admin:password `
    -X PUT "$baseUrl/transactions/13947830000" `
    -H "Content-Type: application/json" `
    --data-binary "@$sample"

Write-Host "`n=== DELETE /transactions/13947830000 ==="
curl.exe -i -u admin:password -X DELETE "$baseUrl/transactions/13947830000"
