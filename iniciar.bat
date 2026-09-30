@echo off
setlocal
title Assistente

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo O projeto ainda nao foi configurado.
    echo Execute setup.bat primeiro.
    echo.
    pause
    exit /b 1
)

echo Iniciando Assistente...
.venv\Scripts\python.exe app.py

if errorlevel 1 (
    echo.
    echo O Assistente foi encerrado com erro.
    pause
)
