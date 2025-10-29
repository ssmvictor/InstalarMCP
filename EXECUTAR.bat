@echo off
setlocal

REM Wrapper simples para reduzir falsos positivos e delegar a l¢gica ao Python
set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%"

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
        set "PYTHON_CMD=py -3"
    )
) else (
    set "PYTHON_CMD=python"
)

%PYTHON_CMD% executar.py
set "APP_EXIT_CODE=%ERRORLEVEL%"

popd
endlocal
exit /b %APP_EXIT_CODE%
