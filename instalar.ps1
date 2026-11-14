[CmdletBinding()]
param(
    [string]$RepositoryUrl = "https://github.com/UTVAM-Software/2026-III-VoxCentraAI.git",
    [string]$Branch = "main",
    [string]$InstallPath = (Join-Path $env:LOCALAPPDATA "VoxCentraAI-preproduccion"),
    [string]$SourcePath = "",
    [ValidateRange(1, 65535)]
    [int]$Port = 8000,
    [switch]$NoStart
)

$ErrorActionPreference = "Stop"

function Invoke-Checked {
    param([string]$FilePath, [string[]]$Arguments)
    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Falló el comando: $([IO.Path]::GetFileName($FilePath)). Revisa el mensaje anterior."
    }
}

function Set-EnvLine {
    param([string]$Content, [string]$Name, [string]$Value)
    $lines = [System.Collections.Generic.List[string]]::new()
    $found = $false
    $prefix = $Name + "="
    foreach ($line in ($Content -split "\r?\n")) {
        if ($line.StartsWith($prefix)) {
            if (-not $found) {
                $lines.Add($prefix + $Value)
                $found = $true
            }
        } else {
            $lines.Add($line)
        }
    }
    if (-not $found) {
        $lines.Add($prefix + $Value)
    }
    return [string]::Join([Environment]::NewLine, $lines)
}

Write-Host "Revisando Python..."
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCommand) {
    throw "No encontré Python. Instala Python 3.12 o posterior."
}
$pythonExe = $pythonCommand.Source
$pythonVersion = & $pythonExe -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
if ([version]$pythonVersion -lt [version]"3.12") {
    throw "Se requiere Python 3.12 o posterior. Se encontró Python $pythonVersion."
}

$destination = [IO.Path]::GetFullPath($InstallPath)
if (-not (Test-Path -LiteralPath $destination)) {
    New-Item -ItemType Directory -Path $destination -Force | Out-Null
}
$venvPath = Join-Path $destination ".venv"
if (-not (Test-Path -LiteralPath (Join-Path $venvPath "Scripts\python.exe"))) {
    Write-Host "Creando el entorno virtual..."
    Invoke-Checked -FilePath $pythonExe -Arguments @("-m", "venv", $venvPath)
}

$sourceDirectory = Join-Path $destination "source"
if ($SourcePath) {
    if (-not (Test-Path -LiteralPath $SourcePath)) {
        throw "No existe la carpeta indicada en -SourcePath."
    }
    $sourceResolved = (Resolve-Path -LiteralPath $SourcePath).Path
    if (-not (Test-Path -LiteralPath (Join-Path $sourceResolved "manage.py"))) {
        throw "La carpeta de origen no parece contener VoxCentraAI."
    }
    if (-not (Test-Path -LiteralPath (Join-Path $sourceDirectory "manage.py"))) {
        if (Test-Path -LiteralPath $sourceDirectory) {
            if ((Get-ChildItem -Force -LiteralPath $sourceDirectory | Measure-Object).Count -gt 0) {
                throw "La carpeta source ya contiene archivos. Elige otra ruta de instalación."
            }
        } else {
            New-Item -ItemType Directory -Path $sourceDirectory -Force | Out-Null
        }
        Write-Host "Copiando el código fuente local..."
        $copyLog = Join-Path $env:TEMP "voxcentra-copy-$PID.log"
        & robocopy.exe $sourceResolved $sourceDirectory /E /XD .git .venv venv __pycache__ staticfiles .local-logs /XF .env db.sqlite3 /NFL /NDL /NJH /NJS /NP "/LOG:$copyLog" | Out-Null
        $copyResult = $LASTEXITCODE
        if ($copyResult -ge 8) {
            throw "No se pudo copiar el proyecto. Revisa el registro temporal del instalador."
        }
        Remove-Item -LiteralPath $copyLog -Force -ErrorAction SilentlyContinue
        $sourceEnv = Join-Path $sourceResolved ".env"
        if (Test-Path -LiteralPath $sourceEnv) {
            Copy-Item -LiteralPath $sourceEnv -Destination (Join-Path $sourceDirectory ".env") -Force
        }
    } else {
        Write-Host "La carpeta source ya contiene una instalación; la conservé."
    }
} elseif (-not (Test-Path -LiteralPath (Join-Path $sourceDirectory "manage.py"))) {
    $gitCommand = Get-Command git -ErrorAction SilentlyContinue
    if (-not $gitCommand) {
        throw "No encontré Git. Instálalo o usa -SourcePath con una copia local."
    }
    Write-Host "Descargando el código fuente desde GitHub..."
    Invoke-Checked -FilePath $gitCommand.Source -Arguments @("clone", "--depth", "1", "--branch", $Branch, $RepositoryUrl, $sourceDirectory)
} else {
    Write-Host "Usando el código fuente ya instalado."
}

if (-not (Test-Path -LiteralPath (Join-Path $sourceDirectory "requirements.txt"))) {
    throw "No encontré requirements.txt en la carpeta source."
}

Write-Host "Configurando la base local y las variables..."
$envPath = Join-Path $sourceDirectory ".env"
if (-not (Test-Path -LiteralPath $envPath)) {
    $examplePath = Join-Path $sourceDirectory ".env.example"
    if (-not (Test-Path -LiteralPath $examplePath)) {
        throw "Falta .env.example. No se creó una configuración incompleta."
    }
    Copy-Item -LiteralPath $examplePath -Destination $envPath
}
$envText = [System.IO.File]::ReadAllText($envPath)
$secretMatch = [regex]::Match($envText, "(?m)^DJANGO_SECRET_KEY=(.*)$")
$secret = ""
if ($secretMatch.Success) {
    $secret = $secretMatch.Groups[1].Value.Trim().Trim('"').Trim("'")
}
if ($secret.Length -lt 50) {
    $secret = (& $pythonExe -c "import secrets; print(secrets.token_urlsafe(64))").Trim()
}
$dbPath = (Join-Path $sourceDirectory "db.sqlite3").Replace("\", "/")
$envText = Set-EnvLine -Content $envText -Name "DJANGO_ENV" -Value "local"
$envText = Set-EnvLine -Content $envText -Name "DJANGO_DEBUG" -Value "False"
$envText = Set-EnvLine -Content $envText -Name "DJANGO_SECRET_KEY" -Value $secret
$envText = Set-EnvLine -Content $envText -Name "DJANGO_ALLOWED_HOSTS" -Value "127.0.0.1,localhost"
$envText = Set-EnvLine -Content $envText -Name "DJANGO_CSRF_TRUSTED_ORIGINS" -Value "http://127.0.0.1:$Port,http://localhost:$Port"
$envText = Set-EnvLine -Content $envText -Name "DJANGO_LOCAL_PORT" -Value "$Port"
$envText = Set-EnvLine -Content $envText -Name "DJANGO_DB_NAME" -Value ('"' + $dbPath + '"')
[System.IO.File]::WriteAllText($envPath, $envText.Trim() + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))

Write-Host "Instalando herramientas, base y cuentas..."
$venvPython = Join-Path $venvPath "Scripts\python.exe"
Invoke-Checked -FilePath $venvPython -Arguments @("-m", "pip", "install", "-r", (Join-Path $sourceDirectory "requirements.txt"))
$databasePath = Join-Path $sourceDirectory "db.sqlite3"
$freshDatabase = -not (Test-Path -LiteralPath $databasePath)
Push-Location $sourceDirectory
try {
    Invoke-Checked -FilePath $venvPython -Arguments @("manage.py", "migrate", "--noinput")
    if ($freshDatabase) {
        $fixture = Join-Path $sourceDirectory "documentacion\voxcentra_seed.json"
        if (-not (Test-Path -LiteralPath $fixture)) {
            throw "La instalación nueva requiere documentacion/voxcentra_seed.json."
        }
        Invoke-Checked -FilePath $venvPython -Arguments @("manage.py", "loaddata", "documentacion/voxcentra_seed.json")
    } else {
        Write-Host "La base ya tenía datos; conservé las cuentas y los registros."
    }
    Invoke-Checked -FilePath $venvPython -Arguments @("manage.py", "collectstatic", "--noinput")
    Invoke-Checked -FilePath $venvPython -Arguments @("manage.py", "check")
} finally {
    Pop-Location
}

Copy-Item -LiteralPath (Join-Path $sourceDirectory "detener-local.ps1") -Destination (Join-Path $destination "detener-local.ps1") -Force

if (-not $NoStart) {
    Write-Host "Activando el servicio web local..."
    $listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if ($listener) {
        throw "El puerto $Port ya está ocupado. Vuelve a ejecutar con -Port 8010 (o elige otro puerto)."
    }
    $logDirectory = Join-Path $destination ".local-logs"
    New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
    $stdoutLog = Join-Path $logDirectory "daphne.stdout.log"
    $stderrLog = Join-Path $logDirectory "daphne.stderr.log"
    $pidFile = Join-Path $logDirectory "daphne.pid"
    $daphneExe = Join-Path $venvPath "Scripts\daphne.exe"
    if (-not (Test-Path -LiteralPath $daphneExe)) {
        throw "No se instaló Daphne. Revisa requirements.txt."
    }
    $process = Start-Process -FilePath $daphneExe -ArgumentList "-b 127.0.0.1 -p $Port voxcentra.asgi:application" -WorkingDirectory $sourceDirectory -WindowStyle Hidden -RedirectStandardOutput $stdoutLog -RedirectStandardError $stderrLog -PassThru
    Set-Content -LiteralPath $pidFile -Value $process.Id -Encoding ascii
    $ready = $false
    for ($attempt = 0; $attempt -lt 40; $attempt++) {
        Start-Sleep -Milliseconds 500
        if ($process.HasExited) {
            Remove-Item -LiteralPath $pidFile -Force -ErrorAction SilentlyContinue
            throw "Daphne se cerró al iniciar. Revisa el registro local en $stderrLog."
        }
        $client = [System.Net.Sockets.TcpClient]::new()
        try {
            $client.Connect("127.0.0.1", $Port)
            $ready = $client.Connected
        } catch {
            $ready = $false
        } finally {
            $client.Dispose()
        }
        if ($ready) { break }
    }
    if (-not $ready) {
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath $pidFile -Force -ErrorAction SilentlyContinue
        throw "El servicio no respondió en el puerto $Port. Revisa el registro local en $stderrLog."
    }
    Write-Host "Servidor activo solo en esta computadora: http://127.0.0.1:$Port/ (PID $($process.Id))."
    Write-Host "Para detenerlo: .\detener-local.ps1"
} else {
    Write-Host "Instalación lista; omití iniciar el servicio por -NoStart."
}

Write-Host "Entorno local listo en: $destination"
