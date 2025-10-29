#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Manager - Instalação de Dependências

Este script instala as dependências listadas em `requirements.txt` usando o pip
da própria instalação do Python em execução. Execute-o preferencialmente uma
única vez, antes de iniciar a aplicação.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _print_banner() -> None:
    print("\n===============================================")
    print("MCP Manager - Instalação de Dependências")
    print("===============================================\n")
    print("[INFO] Este script irá instalar as dependências necessárias do projeto.")
    print("[INFO] Normalmente você só precisa executá-lo uma vez.\n")


def _check_python() -> bool:
    major, minor = sys.version_info[:2]
    if (major, minor) < (3, 7):
        print(
            f"[ERRO] Python 3.7 ou superior é necessário. Versão atual: {major}.{minor}"
        )
        return False
    return True


def _check_pip() -> bool:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as exc:
        print(f"[ERRO] Falha ao verificar o pip: {exc}")
        return False

    if result.returncode != 0:
        print("[ERRO] Pip não encontrado ou indisponível.")
        print("[AVISO] Tente instalar/atualizar com: python -m ensurepip --upgrade")
        return False

    return True


def _requirements_path() -> Path:
    return (Path(__file__).parent / "requirements.txt").resolve()


def _install_requirements(req_path: Path) -> int:
    print(f"[INFO] Instalando dependências de: {req_path}")
    cmd = [sys.executable, "-m", "pip", "install", "-r", str(req_path)]
    proc = subprocess.run(cmd)
    return proc.returncode


def main() -> int:
    try:
        _print_banner()

        if not _check_python():
            return 1

        if not _check_pip():
            return 1

        req = _requirements_path()
        if not req.exists():
            print("[AVISO] Arquivo requirements.txt não encontrado. Nada a instalar.")
            print("[INFO] Você pode iniciar a aplicação com `executar.py` ou `EXECUTAR.bat`.")
            return 0

        code = _install_requirements(req)
        if code == 0:
            print("[INFO] ✅ Dependências instaladas com sucesso!")
            print("[INFO] Você pode executar a aplicação com `executar.py` ou `EXECUTAR.bat`.")
            return 0
        else:
            print("[ERRO] A instalação de dependências falhou. Verifique as mensagens acima.")
            return code or 1

    except KeyboardInterrupt:
        print("\n[AVISO] Operação cancelada pelo usuário (Ctrl+C).")
        return 130
    except Exception as exc:
        print(f"[ERRO] Ocorreu um erro inesperado: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
