@echo off
setlocal EnableExtensions
title Setup - Assistente

cd /d "%~dp0"

echo ============================================
echo        SETUP DO ASSISTENTE
echo ============================================
echo.

where py >nul 2>&1
if %errorlevel%==0 (
    set "PY=py -3.11"
    goto :python_ok
)

where python >nul 2>&1
if %errorlevel%==0 (
    set "PY=python"
    goto :python_ok
)

echo Python nao foi encontrado.
echo.
echo Tentando instalar Python 3.11 pelo WinGet...
where winget >nul 2>&1
if %errorlevel%==0 (
    winget install --id Python.Python.3.11 -e --source winget --accept-source-agreements --accept-package-agreements
)

where py >nul 2>&1
if %errorlevel%==0 (
    set "PY=py -3.11"
    goto :python_ok
)

where python >nul 2>&1
if %errorlevel%==0 (
    set "PY=python"
    goto :python_ok
)

echo.
echo Nao foi possivel instalar o Python automaticamente.
echo Instale o Python 3.11 e execute este arquivo novamente.
pause
exit /b 1

:python_ok
echo Python encontrado: %PY%
echo.

if not exist ".venv\Scripts\python.exe" (
    echo Criando ambiente virtual...
    %PY% -m venv .venv
    if errorlevel 1 goto :error
)

echo Atualizando ferramentas...
.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
if errorlevel 1 goto :error

echo.
echo Instalando dependencias...
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo.
echo ============================================
echo Setup concluido.
echo ============================================
echo.
echo Para iniciar: iniciar.bat
echo Para gerar EXE: gerar_exe.bat
echo.
pause
exit /b 0

:error
echo.
echo ============================================
echo ERRO DURANTE O SETUP
echo ============================================
echo Verifique a mensagem acima e tente novamente.
pause
exit /b 1
