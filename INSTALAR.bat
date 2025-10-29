@echo off
setlocal

REM ================================================
REM  MCP Manager - Instalador de Dependencias
REM  Execute apenas uma vez apos baixar o projeto.
REM  Depois, use EXECUTAR.bat para iniciar a aplicacao.
REM ================================================

set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%"

echo ================================================
echo  MCP Manager - Instalacao de Dependencias
echo ================================================
echo.
echo Este script instala as dependencias necessarias do projeto.
echo Execute apenas uma vez. Para iniciar a aplicacao, use EXECUTAR.bat.
echo.

REM Pausa opcional: use "--no-pause" para desativar ao final
if /I "%~1"=="--no-pause" set "NOPAUSE=1"

REM Verifica Python e prepara fallback para launcher 'py'
set "PY_CMD="
where python >nul 2>&1
if errorlevel 1 (
    where py >nul 2>&1
    if errorlevel 1 (
        echo [ERRO] Python nao encontrado no PATH e launcher 'py' indisponivel.
        echo Instale o Python 3 e reinicie o terminal.
        echo Alternativa: apos instalar, execute novamente este script.
        set "EXIT_CODE=1"
        goto :END
    ) else (
        echo [INFO] Python nao encontrado no PATH. Usando launcher: py -3
        set "PY_CMD=py -3"
    )
) else (
    set "PY_CMD=python"
)

REM Verifica pip
%PY_CMD% -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] pip nao encontrado ou Python sem pip configurado.
    echo Tente: python -m ensurepip --upgrade
    echo Ou   : python -m pip install --upgrade pip
    set "EXIT_CODE=1"
    goto :END
)

REM Verifica arquivo requirements.txt
if not exist requirements.txt (
    echo [AVISO] Arquivo requirements.txt nao encontrado em: "%CD%"
    echo Nao ha dependencias a instalar.
    set "EXIT_CODE=0"
    goto :END
)

echo Instalando dependencias a partir de requirements.txt ...
%PY_CMD% -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias. Verifique sua conexao e permissoes.
    set "EXIT_CODE=1"
    goto :END
)

echo.
echo ✅ Dependencias instaladas com sucesso.
echo Para executar a aplicacao, use: EXECUTAR.bat
set "EXIT_CODE=0"

:END
echo.
if not defined NOPAUSE pause
popd
endlocal & exit /b %EXIT_CODE%
