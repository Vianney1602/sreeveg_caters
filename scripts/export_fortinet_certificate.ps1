param(
    [string]$OutputPath = "$PSScriptRoot\fortinet-root.cer",
    [switch]$RegisterScheduledTask,
    [string]$TaskName = 'SreevegCaters-ExportFortinetCert'
)

$ErrorActionPreference = 'Stop'

function Get-FortinetCertificates {
    $stores = @(
        'Cert:\CurrentUser\Root',
        'Cert:\LocalMachine\Root'
    )

    $matches = foreach ($store in $stores) {
        if (-not (Test-Path $store)) {
            continue
        }

        try {
            Get-ChildItem $store | Where-Object {
                $_.Subject -match 'Fortinet' -or $_.Issuer -match 'Fortinet'
            }
        } catch {
            Write-Warning "Unable to read certificate store $($store): $($_.Exception.Message)"
        }
    }

    $matches |
        Sort-Object -Property NotAfter -Descending |
        Group-Object Thumbprint |
        ForEach-Object { $_.Group | Select-Object -First 1 }
}

function Export-LatestFortinetCertificate {
    param(
        [string]$DestinationPath
    )

    $certs = Get-FortinetCertificates

    if (-not $certs) {
        throw 'No Fortinet certificate was found in the current user or local machine Root store.'
    }

    $selected = $certs | Select-Object -First 1
    $destination = [System.IO.Path]::GetFullPath($DestinationPath)
    $destinationDir = Split-Path -Parent $destination

    if ($destinationDir -and -not (Test-Path $destinationDir)) {
        New-Item -ItemType Directory -Path $destinationDir | Out-Null
    }

    Export-Certificate -Cert $selected -FilePath $destination -Force | Out-Null

    [pscustomobject]@{
        Subject    = $selected.Subject
        Issuer     = $selected.Issuer
        Thumbprint = $selected.Thumbprint
        NotBefore  = $selected.NotBefore
        NotAfter   = $selected.NotAfter
        OutputPath = $destination
    }
}

function Register-FortinetCertificateTask {
    param(
        [string]$ScriptPath,
        [string]$DestinationPath,
        [string]$Name
    )

    $escapedScriptPath = $ScriptPath.Replace('"', '""')
    $escapedDestinationPath = $DestinationPath.Replace('"', '""')

    $action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$escapedScriptPath`" -OutputPath `"$escapedDestinationPath`""
    $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 3:00AM
    $principal = New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel LeastPrivilege
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

    Register-ScheduledTask -TaskName $Name -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
}

$export = Export-LatestFortinetCertificate -DestinationPath $OutputPath
Write-Host "Exported Fortinet certificate to $($export.OutputPath)"
Write-Host "Subject   : $($export.Subject)"
Write-Host "Issuer    : $($export.Issuer)"
Write-Host "Thumbprint: $($export.Thumbprint)"
Write-Host "Valid     : $($export.NotBefore) -> $($export.NotAfter)"

if ($RegisterScheduledTask) {
    Register-FortinetCertificateTask -ScriptPath $PSCommandPath -DestinationPath $OutputPath -Name $TaskName
    Write-Host "Scheduled task registered: $TaskName"
}
