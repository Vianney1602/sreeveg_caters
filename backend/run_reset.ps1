Invoke-RestMethod -Uri 'http://localhost:8000/api/users/admin/reset-password' -Method Post -ContentType 'application/json' -Body '{"otp":"605795","new_password":"NewAdmin@2026"}' | ConvertTo-Json
