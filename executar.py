#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Manager - Executar Aplicação

Este script verifica dependências declaradas em `requirements.txt`, oferece
instalá-las se estiverem ausentes e em seguida executa `mcp_gui.py`.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


def _print_banner() -> None:
    print("\n===============================================")
    print("MCP Manager - Executar Aplicação")
    print("===============================================\n")


def _requirements_path() -> Path:
    return (Path(__file__).parent / "requirements.txt").resolve()


def _extract_pkg_name(line: str) -> str:
    s = line.strip()
    if not s or s.startswith('#'):
        return ''
    for sep in ['==', '>=', '<=', '>', '<', '~=', '!=']:
        if sep in s:
            s = s.split(sep, 1)[0]
            break
    # Extras (e.g., package[extra])
    if '[' in s:
        s = s.split('[', 1)[0]
    return s.strip().replace('-', '_')


def verificar_dependencias():
    req = _requirements_path()
    if not req.exists():
        return True, []

    missing = []
    try:
        lines = req.read_text(encoding='utf-8').splitlines()
    except Exception:
        lines = []

    pkgs = [p for p in (_extract_pkg_name(l) for l in lines) if p]

    # Possíveis mapeamentos nome-do-pip -> nome-do-import
    special_imports = {
        'ttkthemes': 'ttkthemes',
    }

    for pkg in pkgs:
        mod = special_imports.get(pkg, pkg)
        try:
            spec = importlib.util.find_spec(mod)
        except Exception:
            spec = None
        if spec is None:
            missing.append(pkg)

    return (len(missing) == 0), missing


def instalar_dependencias() -> bool:
    print('[INFO] Instalando dependências ausentes...')
    req = _requirements_path()
    cmd = [sys.executable, '-m', 'pip', 'install', '-r', str(req)]
    proc = subprocess.run(cmd)
    if proc.returncode == 0:
        print('[INFO] ✅ Instalação concluída com sucesso.')
        return True
    else:
        print('[ERRO] Falha ao instalar dependências. Verifique as mensagens acima.')
        return False


def executar_aplicacao() -> int:
    script = (Path(__file__).parent / 'mcp_gui.py').resolve()
    if not script.exists():
        print('[ERRO] Arquivo mcp_gui.py não encontrado ao lado deste script.')
        return 1
    proc = subprocess.run([sys.executable, str(script)])
    return proc.returncode


def main() -> int:
    try:
        _print_banner()
        ok, missing = verificar_dependencias()
        if not ok:
            print('[AVISO] Dependências ausentes detectadas:')
            for m in missing:
                print(f'  - {m}')
            resp = input('Deseja instalar agora? (y/n): ').strip().lower()
            if resp in {'y', 's', 'sim', 'yes'}:
                if not instalar_dependencias():
                    return 1
            else:
                print('[AVISO] Você pode executar a instalação manual com `instalar.py`.')
                return 1

        print('[INFO] Iniciando MCP Manager...')
        return executar_aplicacao()

    except KeyboardInterrupt:
        print('\n[AVISO] Operação cancelada pelo usuário (Ctrl+C).')
        return 130
    except Exception as exc:
        print(f'[ERRO] Ocorreu um erro inesperado: {exc}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
