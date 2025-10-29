@echo off
setlocal

REM Descobre o diretório onde o script BAT está localizado
set "SCRIPT_DIR=%~dp0"

REM Entra no diretório do projeto para garantir imports corretos
pushd "%SCRIPT_DIR%"

REM Atenção: instale as dependencias antes usando INSTALAR.bat (execucao unica)

REM Verifica a disponibilidade do Python e define comando com fallback para launcher 'py'
set "PYTHON_CMD="
where python >nul 2>&1
if errorlevel 1 (
    where py >nul 2>&1
    if errorlevel 1 (
        echo [ERRO] Python nao encontrado. Instale o Python 3 ou use o launcher 'py'.
        popd
        endlocal
        exit /b 1
    ) else (
        echo [INFO] Usando launcher Python: py -3
        set "PYTHON_CMD=py -3"
    )
) else (
    set "PYTHON_CMD=python"
)

REM Executa a interface grafica do MCP Manager
%PYTHON_CMD% mcp_gui.py

set "APP_EXIT_CODE=%ERRORLEVEL%"

if not %APP_EXIT_CODE%==0 (
    echo [ERRO] Falha ao iniciar a aplicacao (codigo %APP_EXIT_CODE%).
    echo Dica: se houve erro de importacao, execute INSTALAR.bat para instalar as dependencias.
)

REM Retorna ao diretório original
popd

endlocal
exit /b %APP_EXIT_CODE%
