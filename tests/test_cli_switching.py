#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes para a funcionalidade de troca de CLI.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.core.mcp_manager import MCPManager
from src.core.config_manager import ConfigManager


class TestCLISwitching(unittest.TestCase):
    """Testes para a funcionalidade de troca de CLI."""

    def setUp(self):
        """Configura ambiente de teste."""
        self.temp_dir = tempfile.mkdtemp()
        self.user_dir = Path(self.temp_dir) / "user"
        self.user_dir.mkdir()

        self.config_file = Path(self.temp_dir) / "mcp_config.json"

        self.gemini_dir = self.user_dir / ".gemini"
        self.gemini_dir.mkdir()

        self.qwen_dir = self.user_dir / ".qwen"
        self.qwen_dir.mkdir()

        self.config_manager = ConfigManager(str(self.config_file))

    def tearDown(self):
        """Limpa ambiente de teste."""
        shutil.rmtree(self.temp_dir)

    def test_cli_switching_to_qwen(self):
        """Testa a troca de CLI para Qwen."""
        self.config_manager.set_user_path(str(self.user_dir))
        self.config_manager.set_cli_type("qwen")

        with patch('src.core.mcp_manager.ConfigManager') as mock_config_manager:
            mock_instance = MagicMock()
            mock_instance.get_user_path.return_value = str(self.user_dir)
            mock_instance.get_cli_type.return_value = "qwen"
            mock_config_manager.return_value = mock_instance

            manager = MCPManager(config_manager=mock_instance)

        expected_path = self.user_dir / ".qwen" / "settings.json"
        self.assertEqual(manager.settings_path, expected_path)

        # Forçar a criação do arquivo de configurações
        settings = manager.load_settings()
        
        # Verificar se o tipo de autenticação está correto
        self.assertEqual(settings['security']['auth']['selectedType'], "qwen-oauth")

    def test_cli_switching_to_gemini_auth_type(self):
        """Testa o tipo de autenticação ao trocar para a CLI Gemini."""
        self.config_manager.set_user_path(str(self.user_dir))
        self.config_manager.set_cli_type("gemini")

        with patch('src.core.mcp_manager.ConfigManager') as mock_config_manager:
            mock_instance = MagicMock()
            mock_instance.get_user_path.return_value = str(self.user_dir)
            mock_instance.get_cli_type.return_value = "gemini"
            mock_config_manager.return_value = mock_instance

            manager = MCPManager(config_manager=mock_instance)

        expected_path = self.user_dir / ".gemini" / "settings.json"
        self.assertEqual(manager.settings_path, expected_path)

        # Forçar a criação do arquivo de configurações
        settings = manager.load_settings()
        
        # Verificar se o tipo de autenticação está correto
        self.assertEqual(settings['security']['auth']['selectedType'], "oauth-personal")


if __name__ == "__main__":
    unittest.main()
