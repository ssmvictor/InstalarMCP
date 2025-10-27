#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demonstracao da integracao entre ConfigManager e MCPManager.
"""

from pathlib import Path

from src.core.config_manager import ConfigManager, ConfigManagerError
from src.core.mcp_manager import MCPManager, MCPManagerError


def demo_config_manager():
    """Demonstra as funcionalidades do ConfigManager."""
    print("=== Demonstracao do ConfigManager ===\n")

    config = ConfigManager()

    if config.has_config():
        current_path = config.get_user_path()
        print(f"Caminho atual do usuario: {current_path}")
    else:
        print("Nenhuma configuracao de usuario encontrada.")

        user_home = str(Path.home())
        try:
            success = config.set_user_path(user_home)
            if success:
                print(f"Caminho configurado: {user_home}")
        except ConfigManagerError as e:
            print(f"Erro ao configurar caminho: {e}")

    print(f"Arquivo de configuracao: {config.config_path}")
    print()


def demo_mcp_manager_integration():
    """Demonstra a integracao com MCPManager."""
    print("=== Demonstracao da Integracao com MCPManager ===\n")

    try:
        with MCPManager() as manager:
            print(f"MCPManager usando o caminho: {manager.settings_path}")

            mcps = manager.get_mcps()
            print(f"\nEncontrados {len(mcps)} MCPs configurados:")

            if mcps:
                for name, details in mcps.items():
                    status = "Ativado" if details.get("enabled") else "Desativado"
                    print(f"  - {name}: {status}")
                    print(f"    Comando: {details.get('command', '')}")
                    print(f"    Args: {', '.join(details.get('args', []))}")
            else:
                print("  Nenhum MCP configurado.")

            templates = manager.get_templates()
            print(f"\nTemplates disponiveis: {list(templates.keys())}")

    except MCPManagerError as e:
        print(f"Erro ao usar MCPManager: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

    print()


def demo_add_example_mcp():
    """Demonstra como adicionar um MCP de exemplo."""
    print("=== Demonstracao de Adicao de MCP ===\n")

    try:
        with MCPManager() as manager:
            mcps = manager.get_mcps()
            if "exemplo-demo" in mcps:
                print("MCP de exemplo ja existe. Removendo para demonstracao...")
                manager.remove_mcp("exemplo-demo")

            print("Adicionando MCP de exemplo...")
            manager.add_mcp(
                name="exemplo-demo",
                command="echo",
                args=["Hello", "from", "MCP", "Manager"],
            )

            manager.toggle_allowed("exemplo-demo", True)

            mcps = manager.get_mcps()
            if "exemplo-demo" in mcps:
                print("MCP de exemplo adicionado com sucesso!")
                details = mcps["exemplo-demo"]
                print("  Nome: exemplo-demo")
                print(f"  Comando: {details.get('command')}")
                print(f"  Args: {details.get('args')}")
                print(
                    f"  Status: {'Ativado' if details.get('enabled') else 'Desativado'}"
                )

    except MCPManagerError as e:
        print(f"Erro ao adicionar MCP: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

    print()


def main():
    """Funcao principal da demonstracao."""
    print("Demonstracao da Integracao entre ConfigManager e MCPManager\n")
    print("=" * 60)

    demo_config_manager()
    demo_mcp_manager_integration()
    demo_add_example_mcp()

    print("Demonstracao concluida!")
    print("\nPara configurar um caminho personalizado, execute:")
    print("python -m scripts.setup_user_path")
    print("\nPara executar a interface grafica, execute:")
    print("python mcp_gui.py")


if __name__ == "__main__":
    main()
