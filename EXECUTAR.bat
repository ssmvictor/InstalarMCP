@echo off
setlocal

REM Descobre o diretório onde o script BAT está localizado
set "SCRIPT_DIR=%~dp0"

REM Entra no diretório do projeto para garantir imports corretos
pushd "%SCRIPT_DIR%"

REM Instala as dependências do projeto antes de executar
if exist requirements.txt (
    echo Instalando dependencias do requirements.txt...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Erro ao instalar dependencias. Verifique o Python/pip e a conexao.
        popd
        endlocal
        exit /b 1
    )
)

REM Executa a interface gráfica do MCP Manager
python mcp_gui.py

set "APP_EXIT_CODE=%ERRORLEVEL%"

REM Retorna ao diretório original
popd

endlocal
exit /b %APP_EXIT_CODE%
