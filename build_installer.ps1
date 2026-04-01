# тение версии из version.py
$versionFile = "version.py"
if (Test-Path $versionFile) {
    $content = Get-Content $versionFile -Raw
    if ($content -match 'VERSION\s*=\s*"([^"]+)"') {
        $version = $matches[1]
        Write-Host "ерсия: $version"
    } else {
        Write-Host "е удалось извлечь версию из $versionFile"
        exit 1
    }
} else {
    Write-Host "айл $versionFile не найден"
    exit 1
}

# енерация .iss файла из шаблона
$templateFile = "build_installer.iss.template"
if (-not (Test-Path $templateFile)) {
    Write-Host "айл шаблона $templateFile не найден"
    exit 1
}
$template = Get-Content $templateFile -Raw
$issContent = $template -replace '{#AppVersion}', $version
$issContent | Out-File -FilePath "build_installer.iss" -Encoding UTF8
Write-Host "Создан файл build_installer.iss с версией $version"

# уть к компилятору Inno Setup
$isccPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $isccPath)) {
    $isccPath = "C:\Program Files\Inno Setup 6\ISCC.exe"
}
if (Test-Path $isccPath) {
    Write-Host "омпиляция установщика..."
    & $isccPath "build_installer.iss"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "становщик успешно создан: museum_setup-$version.exe"
    } else {
        Write-Host "шибка компиляции, код: $LASTEXITCODE"
        exit $LASTEXITCODE
    }
} else {
    Write-Host "Inno Setup не найден. кажите правильный путь к ISCC.exe"
    exit 1
}
