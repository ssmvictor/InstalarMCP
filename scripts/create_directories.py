#!/usr/bin/env python3
"""
Script para criar os diretórios necessários para o projeto MCP.
Garante que todos os diretórios solicitados existam.
"""

import os

# Lista de diretórios que precisam existir
directories = [
    "c:/git/Python/ferramentas/mcp/src/",
    "c:/git/Python/ferramentas/mcp/src/core/",
    "c:/git/Python/ferramentas/mcp/src/gui/",
    "c:/git/Python/ferramentas/mcp/scripts/",
    "c:/git/Python/ferramentas/mcp/examples/",
    "c:/git/Python/ferramentas/mcp/tests/",
    "c:/git/Python/ferramentas/mcp/docs/"
]

def create_directories():
    """Cria todos os diretórios necessários se eles não existirem."""
    print("Verificando e criando diretorios necessarios...")
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"[OK] Diretorio verificado/criado: {directory}")
        except Exception as e:
            print(f"[ERRO] Erro ao criar diretorio {directory}: {e}")
    
    print("\nVerificacao concluida!")

if __name__ == "__main__":
    create_directories()