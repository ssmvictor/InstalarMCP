#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para configurar o caminho base do usuario para o MCP Manager.
"""

from pathlib import Path

from src.core.config_manager import ConfigManager, ConfigManagerError


def main():
    """Configura o caminho base do usuario."""
    print("=== Configuracao do Caminho Base do Usuario ===\n")

    # Criar instancia do ConfigManager
    config = ConfigManager()

    # Verificar se ja existe uma configuracao
    current_path = config.get_user_path()
    if current_path:
        print(f"Caminho atual configurado: {current_path}")
        response = input("Deseja alterar o caminho? (s/N): ").strip().lower()
        if response not in ["s", "sim"]:
            print("Configuracao mantida. Encerrando.")
            return

    # Obter o caminho do usuario
    while True:
        user_path = input(
            "\nDigite o caminho base do usuario (ex: C:/Users/SEU_NOME): "
        ).strip()

        if not user_path:
            print("Erro: O caminho nao pode estar vazio.")
            continue

        # Normalizar o caminho
        path_obj = Path(user_path)

        # Verificar se o caminho existe
        if not path_obj.exists():
            print(f"Erro: O caminho '{user_path}' nao existe.")
            continue

        # Verificar se e um diretorio
        if not path_obj.is_dir():
            print(f"Erro: '{user_path}' nao e um diretorio.")
            continue

        # Tentar configurar o caminho
        try:
            success = config.set_user_path(user_path)
            if success:
                print(f"\nCaminho configurado com sucesso: {user_path}")
                print(f"O arquivo de configuracao foi salvo em: {config.config_path}")
                break
        except ConfigManagerError as e:
            print(f"Erro ao configurar o caminho: {e}")
            response = input("Deseja tentar novamente? (S/n): ").strip().lower()
            if response in ["n", "nao"]:
                print("Configuracao cancelada. Encerrando.")
                return

    # Obter o tipo de CLI preferido
    while True:
        cli_type = input(
            "\nEscolha o CLI preferido (gemini/qwen) [gemini]: "
        ).strip().lower()

        if not cli_type:
            cli_type = "gemini"

        if cli_type in ["gemini", "qwen"]:
            try:
                config.set_cli_type(cli_type)
                print(f"CLI preferido configurado como: {cli_type}")
                break
            except ConfigManagerError as e:
                print(f"Erro ao configurar o CLI: {e}")
                break
        else:
            print("Erro: Escolha invalida. Por favor, digite 'gemini' ou 'qwen'.")

    print("\nConfiguracao concluida!")


if __name__ == "__main__":
    main()
