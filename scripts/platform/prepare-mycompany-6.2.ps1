[CmdletBinding()]
param(
    [string]$CacheDirectory = (Join-Path $env:LOCALAPPDATA "Rubrova\platforms\mycompany-6.2")
)
$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($CacheDirectory)) {
    throw "No se pudo determinar la carpeta de descargas."
}
[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
New-Item -ItemType Directory -Force -Path $CacheDirectory | Out-Null

$artifacts = @(
    @{
        Name = "mycompany-6.2-x64.exe"
        Url = "https://download.lsfusion.org/solutions/mycompany-6.2-x64.exe"
        Sha256 = "0167322fea03e269abfae2a140ab4df5205f07633d2520a3d78e381346fbce75"
    },
    @{
        Name = "mycompany-6.2.jar"
        Url = "https://download.lsfusion.org/solutions/mycompany-6.2.jar"
        Sha256 = "fe5a9bda49295f2292ae229a30c9461a16c137fc350a0aa944df7812a1e2f392"
    }
)

foreach ($artifact in $artifacts) {
    $destination = Join-Path $CacheDirectory $artifact.Name
    $temporary = "$destination.download"
    if (Test-Path -LiteralPath $destination) {
        $existingHash = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($existingHash -eq $artifact.Sha256) {
            Write-Host "VERIFICADO $($artifact.Name) SHA-256=$existingHash"
            continue
        }
        throw "El archivo existente $destination no coincide con el SHA-256 esperado. No se sobrescribió."
    }
    try {
        Invoke-WebRequest -Uri $artifact.Url -OutFile $temporary -UseBasicParsing
        $actualHash = (Get-FileHash -LiteralPath $temporary -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actualHash -ne $artifact.Sha256) {
            throw "Hash incorrecto para $($artifact.Name). Esperado $($artifact.Sha256), recibido $actualHash."
        }
        Move-Item -LiteralPath $temporary -Destination $destination
        Write-Host "VERIFICADO $($artifact.Name) SHA-256=$actualHash"
    }
    catch {
        if (Test-Path -LiteralPath $temporary) { Remove-Item -LiteralPath $temporary -Force }
        throw
    }
}
Write-Host "Artefactos verificados en: $CacheDirectory"
Write-Host "El instalador NO se ejecutó. Cambiá la contraseña inicial de administrador antes de habilitar acceso por LAN."
