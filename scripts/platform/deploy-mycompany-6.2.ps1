[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SettingsPath,

    [string]$ModuleDirectory = (Join-Path $env:ProgramFiles "lsFusion 6\Server\lib"),

    [string]$ServiceName = "lsFusion 6 Server"
)

$ErrorActionPreference = "Stop"

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw "Abrí PowerShell como administrador para instalar la extensión."
}

if (-not (Test-Path -LiteralPath $SettingsPath -PathType Leaf)) {
    throw "No existe el archivo settings.properties indicado: $SettingsPath"
}
if (-not (Test-Path -LiteralPath $ModuleDirectory -PathType Container)) {
    throw "No existe la carpeta de módulos: $ModuleDirectory"
}

$service = Get-Service -Name $ServiceName -ErrorAction Stop
$scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$repositoryRoot = [IO.Path]::GetFullPath((Join-Path $scriptDirectory "..\.."))
$moduleNames = @(
    "RubrovaCustom.lsf",
    "RubrovaPOSLocalization.lsf",
    "RubrovaIntegrationResilience.lsf",
    "RubrovaPaymentTerminals.lsf",
    "RubrovaReplenishmentExport.lsf",
    "MyCompanyResourceBundle_es_AR.properties"
)
$sourceDirectory = Join-Path $repositoryRoot "extensions\lsfusion"
foreach ($name in $moduleNames) {
    $source = Join-Path $sourceDirectory $name
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
        throw "Falta el archivo requerido: $source"
    }
}

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$settingsBackup = "$SettingsPath.rubrova-backup.$stamp"
Copy-Item -LiteralPath $SettingsPath -Destination $settingsBackup

$backups = @{}
foreach ($name in $moduleNames) {
    $destination = Join-Path $ModuleDirectory $name
    if (Test-Path -LiteralPath $destination) {
        $backup = "$destination.rubrova-backup.$stamp"
        Copy-Item -LiteralPath $destination -Destination $backup
        $backups[$name] = $backup
    }
}

$wasRunning = $service.Status -eq "Running"
if ($wasRunning) {
    Stop-Service -Name $ServiceName
    (Get-Service -Name $ServiceName).WaitForStatus(
        [System.ServiceProcess.ServiceControllerStatus]::Stopped,
        [TimeSpan]::FromSeconds(45)
    )
}

try {
    $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
    $settings = [IO.File]::ReadAllText($SettingsPath)
    $settingValues = [ordered]@{
        "logics.topModule" = "RubrovaCustom"
        "user.setLanguage" = "es"
        "user.setCountry" = "AR"
    }

    $lines = [System.Collections.Generic.List[string]]::new()
    foreach ($line in ($settings -split "\r?\n")) {
        $lines.Add($line)
    }
    while ($lines.Count -gt 0 -and $lines[$lines.Count - 1] -eq "") {
        $lines.RemoveAt($lines.Count - 1)
    }

    foreach ($entry in $settingValues.GetEnumerator()) {
        $linePattern = '^\s*' + [regex]::Escape($entry.Key) + '\s*='
        $matchingIndexes = @()
        for ($lineIndex = 0; $lineIndex -lt $lines.Count; $lineIndex++) {
            if ($lines[$lineIndex] -match $linePattern) {
                $matchingIndexes += $lineIndex
            }
        }
        $replacement = $entry.Key + " = " + $entry.Value
        if ($matchingIndexes.Count -gt 0) {
            $lines[$matchingIndexes[0]] = $replacement
            for ($duplicateIndex = $matchingIndexes.Count - 1; $duplicateIndex -gt 0; $duplicateIndex--) {
                $lines.RemoveAt($matchingIndexes[$duplicateIndex])
            }
        } else {
            $lines.Add($replacement)
        }
    }

    $settings = ($lines -join [Environment]::NewLine) + [Environment]::NewLine
    [IO.File]::WriteAllText($SettingsPath, $settings, $utf8NoBom)

    foreach ($name in $moduleNames) {
        Copy-Item -LiteralPath (Join-Path $sourceDirectory $name) -Destination (Join-Path $ModuleDirectory $name) -Force
    }

    if ($wasRunning) {
        Start-Service -Name $ServiceName
        (Get-Service -Name $ServiceName).WaitForStatus(
            [System.ServiceProcess.ServiceControllerStatus]::Running,
            [TimeSpan]::FromSeconds(60)
        )
    }
}
catch {
    Copy-Item -LiteralPath $settingsBackup -Destination $SettingsPath -Force
    foreach ($name in $moduleNames) {
        $destination = Join-Path $ModuleDirectory $name
        if ($backups.ContainsKey($name)) {
            Copy-Item -LiteralPath $backups[$name] -Destination $destination -Force
        } elseif (Test-Path -LiteralPath $destination) {
            Remove-Item -LiteralPath $destination -Force
        }
    }
    if ($wasRunning -and (Get-Service -Name $ServiceName).Status -ne "Running") {
        Start-Service -Name $ServiceName
    }
    throw
}

Write-Host "Extensión modular de Rubrova instalada en: $ModuleDirectory"
Write-Host "Punto de entrada: RubrovaCustom"
Write-Host "Idioma y país predeterminados: español (Argentina)"
Write-Host "Backup de settings: $settingsBackup"
Write-Host "La confirmación final requiere revisar el log del servidor e ingresar en el navegador."
