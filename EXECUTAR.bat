@echo off
setlocal

REM Descobre o diretório onde o script BAT está localizado
set "SCRIPT_DIR=%~dp0"

REM Entra no diretório do projeto para garantir imports corretos
pushd "%SCRIPT_DIR%"

REM Executa a interface gráfica do MCP Manager
python mcp_gui.py

REM Retorna ao diretório original
popd

endlocal
