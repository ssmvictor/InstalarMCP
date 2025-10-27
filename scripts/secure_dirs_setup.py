#!/usr/bin/env python3
"""
Script para criar diretórios com permissões seguras.
Ao criar, aplique permissões seguras: em POSIX 0o755; no Windows, herdar ACLs do diretório pai é suficiente.
"""
import os
import sys
import stat
from pathlib import Path


def create_secure_directory(path):
    """
    Creates a directory with secure permissions.
    On POSIX: applies 0o755 after creation
    On Windows: relies on inherited ACLs
    """
    path = Path(path)
    
    # Create directory if it doesn't exist
    path.mkdir(parents=True, exist_ok=True)
    
    # Apply secure permissions on POSIX systems
    if os.name != 'nt':  # POSIX systems (Linux, macOS, etc.)
        os.chmod(path, 0o755)
        print(f"Criado diretório com permissões 0o755: {path}")
        
        # Verify permissions
        current_perms = stat.filemode(path.stat().st_mode)
        print(f"Permissões atuais: {current_perms}")
    else:  # Windows
        print(f"Criado diretório (permissões herdadas do pai): {path}")


def main():
    # Define the target paths under the current workspace
    base_path = Path("c:/git/Python/ferramentas/mcp/")
    target_paths = [
        base_path,
        base_path / "docs",
        base_path / "examples", 
        base_path / "scripts",
        base_path / "src",
        base_path / "src" / "core",
        base_path / "src" / "gui",
        base_path / "tests"
    ]
    
    print("Criando diretórios com permissões seguras...")
    
    for target_path in target_paths:
        try:
            create_secure_directory(target_path)
        except Exception as e:
            print(f"Erro ao criar diretório {target_path}: {e}")
    
    print("Concluído!")


if __name__ == "__main__":
    main()