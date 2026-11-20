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
$moduleSource = Join-Path $repositoryRoot "extensions\lsfusion\RubrovaCustom.lsf"
$bundleSource = Join-Path $repositoryRoot "extensions\lsfusion\MyCompanyResourceBundle_es_AR.properties"

foreach ($file in @($moduleSource, $bundleSource)) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
        throw "Falta el archivo requerido: $file"
    }
}

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$settingsBackup = "$SettingsPath.rubrova-backup.$stamp"
Copy-Item -LiteralPath $SettingsPath -Destination $settingsBackup
$moduleBackup = Join-Path $ModuleDirectory "RubrovaCustom.lsf.rubrova-backup.$stamp"
$bundleBackup = Join-Path $ModuleDirectory "MyCompanyResourceBundle_es_AR.properties.rubrova-backup.$stamp"

if (Test-Path -LiteralPath (Join-Path $ModuleDirectory "RubrovaCustom.lsf")) {
    Copy-Item -LiteralPath (Join-Path $ModuleDirectory "RubrovaCustom.lsf") -Destination $moduleBackup
}
if (Test-Path -LiteralPath (Join-Path $ModuleDirectory "MyCompanyResourceBundle_es_AR.properties")) {
    Copy-Item -LiteralPath (Join-Path $ModuleDirectory "MyCompanyResourceBundle_es_AR.properties") -Destination $bundleBackup
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
    $pattern = '(?m)^\s*logics\.topModule\s*=.*$'
    if ([regex]::IsMatch($settings, $pattern)) {
        $settings = [regex]::Replace($settings, $pattern, "logics.topModule = RubrovaCustom")
    } else {
        $settings = $settings.TrimEnd() + [Environment]::NewLine + "logics.topModule = RubrovaCustom" + [Environment]::NewLine
    }

    [IO.File]::WriteAllText($SettingsPath, $settings, $utf8NoBom)
    Copy-Item -LiteralPath $moduleSource -Destination (Join-Path $ModuleDirectory "RubrovaCustom.lsf") -Force
    Copy-Item -LiteralPath $bundleSource -Destination (Join-Path $ModuleDirectory "MyCompanyResourceBundle_es_AR.properties") -Force

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
    if (Test-Path -LiteralPath $moduleBackup) {
        Copy-Item -LiteralPath $moduleBackup -Destination (Join-Path $ModuleDirectory "RubrovaCustom.lsf") -Force
    } elseif (Test-Path -LiteralPath (Join-Path $ModuleDirectory "RubrovaCustom.lsf")) {
        Remove-Item -LiteralPath (Join-Path $ModuleDirectory "RubrovaCustom.lsf") -Force
    }
    if (Test-Path -LiteralPath $bundleBackup) {
        Copy-Item -LiteralPath $bundleBackup -Destination (Join-Path $ModuleDirectory "MyCompanyResourceBundle_es_AR.properties") -Force
    } elseif (Test-Path -LiteralPath (Join-Path $ModuleDirectory "MyCompanyResourceBundle_es_AR.properties")) {
        Remove-Item -LiteralPath (Join-Path $ModuleDirectory "MyCompanyResourceBundle_es_AR.properties") -Force
    }
    if ($wasRunning -and (Get-Service -Name $ServiceName).Status -ne "Running") {
        Start-Service -Name $ServiceName
    }
    throw
}

Write-Host "Extensión Rubrova instalada en: $ModuleDirectory"
Write-Host "Configuración: logics.topModule = RubrovaCustom"
Write-Host "Backup de settings: $settingsBackup"
Write-Host "La confirmación final requiere revisar el log del servidor e ingresar en el navegador."
