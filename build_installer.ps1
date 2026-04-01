# Чтение версии из version.py
$versionFile = "version.py"
if (Test-Path $versionFile) {
    $content = Get-Content $versionFile -Raw
    if ($content -match 'VERSION\s*=\s*"([^"]+)"') {
        $version = $matches[1]
        Write-Host "Версия: $version"
    } else {
        Write-Host "Не удалось извлечь версию из $versionFile"
        exit 1
    }
} else {
    Write-Host "Файл $versionFile не найден"
    exit 1
}

# Генерация .iss файла из шаблона
$template = Get-Content "build_installer.iss.template" -Raw
$issContent = $template -replace '{#AppVersion}', $version
$issContent | Out-File -FilePath "build_installer.iss" -Encoding UTF8
Write-Host "Создан файл build_installer.iss с версией $version"

# Путь к компилятору Inno Setup (проверяем оба стандартных пути)
$isccPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $isccPath)) {
    $isccPath = "C:\Program Files\Inno Setup 6\ISCC.exe"
}
if (Test-Path $isccPath) {
    Write-Host "Компиляция установщика..."
    & $isccPath "build_installer.iss"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Установщик успешно создан: museum_setup-$version.exe"
    } else {
        Write-Host "Ошибка компиляции, код: $LASTEXITCODE"
    }
} else {
    Write-Host "Inno Setup не найден. Укажите правильный путь к ISCC.exe"
}