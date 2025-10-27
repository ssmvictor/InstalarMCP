#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo de uso do ConfigManager para gerenciar configuracoes do usuario.
"""

from pathlib import Path

from src.core.config_manager import ConfigManager, ConfigManagerError
from src.core.mcp_manager import MCPManager


def example_basic_usage():
    """Exemplo basico de uso do ConfigManager."""
    print("=== Exemplo Basico do ConfigManager ===\n")

    # Criar instancia do ConfigManager
    config = ConfigManager()

    # Verificar se ha configuracao existente
    if config.has_config():
        user_path = config.get_user_path()
        print(f"Caminho do usuario configurado: {user_path}")
    else:
        print("Nenhuma configuracao de usuario encontrada.")

        # Configurar um caminho de exemplo
        example_path = str(Path.home())  # Usa o diretorio home do usuario atual
        try:
            success = config.set_user_path(example_path)
            if success:
                print(f"Caminho configurado: {example_path}")
        except ConfigManagerError as e:
            print(f"Erro ao configurar caminho: {e}")

    print(f"Arquivo de configuracao: {config.config_path}")
    print()


def example_with_mcp_manager():
    """Exemplo de integracao com MCPManager."""
    print("=== Exemplo de Integracao com MCPManager ===\n")

    # O MCPManager agora usa automaticamente o ConfigManager
    # se nenhum caminho for fornecido
    try:
        with MCPManager() as manager:
            print(f"MCPManager usando o caminho: {manager.settings_path}")

            # Listar MCPs existentes
            mcps = manager.get_mcps()
            print(f"Encontrados {len(mcps)} MCPs configurados:")
            for name, details in mcps.items():
                status = "Ativado" if details.get("enabled") else "Desativado"
                print(f"  - {name}: {status}")

    except Exception as e:
        print(f"Erro ao usar MCPManager: {e}")

    print()


def example_error_handling():
    """Exemplo de tratamento de erros."""
    print("=== Exemplo de Tratamento de Erros ===\n")

    config = ConfigManager()

    # Tentar configurar um caminho invalido
    try:
        config.set_user_path("/caminho/que/nao/existe")
    except ConfigManagerError as e:
        print(f"Erro esperado ao configurar caminho invalido: {e}")

    # Tentar configurar um arquivo em vez de diretorio
    try:
        config.set_user_path(__file__)  # Este arquivo existe, mas nao e um diretorio
    except ConfigManagerError as e:
        print(f"Erro esperado ao configurar arquivo como diretorio: {e}")

    print()


def main():
    """Funcao principal com exemplos de uso."""
    print("Exemplos de Uso do ConfigManager\n")
    print("=" * 50)

    # Exemplo basico
    example_basic_usage()

    # Exemplo com MCPManager
    example_with_mcp_manager()

    # Exemplo de tratamento de erros
    example_error_handling()

    print("Exemplos concluidos!")


if __name__ == "__main__":
    main()
