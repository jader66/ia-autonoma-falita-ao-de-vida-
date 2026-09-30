@echo off
setlocal EnableExtensions
title Gerador de EXE Unico - Assistente
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Execute setup.bat primeiro.
    pause
    exit /b 1
)

echo Instalando PyInstaller...
.venv\Scripts\python.exe -m pip install --upgrade pyinstaller
if errorlevel 1 goto :error

echo.
echo Preparando modelo de voz...
if not exist "models\vosk-model-small-pt-0.3\am" (
    if not exist "models" mkdir "models"
    if not exist "models\vosk-model-small-pt-0.3.zip" (
        powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri 'https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip' -OutFile 'models\vosk-model-small-pt-0.3.zip'"
        if errorlevel 1 goto :error
    )
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -Force 'models\vosk-model-small-pt-0.3.zip' 'models'"
    if errorlevel 1 goto :error
    del /q "models\vosk-model-small-pt-0.3.zip"
)

echo.
echo Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Gerando UM UNICO EXECUTAVEL...
.venv\Scripts\python.exe -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --windowed ^
    --name Assistente ^
    --collect-all vosk ^
    --collect-all sounddevice ^
    --hidden-import pyttsx3.drivers ^
    --hidden-import pyttsx3.drivers.sapi5 ^
    --add-data "models\vosk-model-small-pt-0.3;models\vosk-model-small-pt-0.3" ^
    app.py

if errorlevel 1 goto :error

echo.
echo ============================================
echo EXE UNICO GERADO COM SUCESSO
echo ============================================
echo.
echo dist\Assistente.exe
echo.
echo Este e o arquivo que o usuario final precisa.
echo Nao precisa de Python, .venv ou outros arquivos.
echo.
pause
exit /b 0

:error
echo.
echo ============================================
echo ERRO AO GERAR O EXE
echo ============================================
pause
exit /b 1
