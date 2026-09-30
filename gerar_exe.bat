@echo off
setlocal EnableExtensions
title Gerador de EXE - Assistente

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Execute setup.bat primeiro.
    pause
    exit /b 1
)

echo Instalando PyInstaller...
.venv\Scripts\python.exe -m pip install pyinstaller
if errorlevel 1 goto :error

echo.
echo Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Gerando executavel...
.venv\Scripts\python.exe -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --windowed ^
    --name Assistente ^
    --add-data "voice.py;." ^
    app.py

if errorlevel 1 goto :error

echo.
echo ============================================
echo EXE GERADO COM SUCESSO
echo ============================================
echo.
echo Arquivo:
echo dist\Assistente\Assistente.exe
echo.
echo Observacao: o modelo de voz e baixado na primeira
echo inicializacao quando a funcao de voz for usada.
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
