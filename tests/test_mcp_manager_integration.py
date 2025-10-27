#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes de integração entre MCPManager e ConfigManager.
"""

import unittest
import tempfile
import shutil
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.mcp_manager import MCPManager, MCPManagerError
from src.core.config_manager import ConfigManager, ConfigManagerError


class TestMCPManagerIntegration(unittest.TestCase):
    """Testes de integração entre MCPManager e ConfigManager."""

    def setUp(self):
        """Configura ambiente de teste."""
        # Criar diretórios temporários
        self.temp_dir = tempfile.mkdtemp()
        self.user_dir = Path(self.temp_dir) / "user"
        self.user_dir.mkdir()
        
        # Criar arquivo de configuração temporário com nome único
        self.config_file = Path(self.temp_dir) / f"mcp_config_{id(self)}.json"
        
        # Criar diretório .gemini no diretório do usuário
        self.gemini_dir = self.user_dir / ".gemini"
        self.gemini_dir.mkdir()
        
        # Arquivo settings.json
        self.settings_file = self.gemini_dir / "settings.json"
        
        # Configurar ConfigManager para usar nosso arquivo temporário
        self.config_manager = ConfigManager(str(self.config_file))
        
        # Criar estrutura inicial do settings.json
        initial_settings = {
            "ide": {"hasSeenNudge": True, "enabled": True},
            "mcp": {"allowed": []},
            "mcpServers": {},
            "security": {"auth": {"selectedType": "oauth-personal"}},
            "ui": {"theme": "Default"}
        }
        
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(initial_settings, f, indent=2)

    def tearDown(self):
        """Limpa ambiente de teste."""
        shutil.rmtree(self.temp_dir)

    def test_mcp_manager_with_config_manager(self):
        """Testa MCPManager usando ConfigManager para obter o caminho."""
        # Configurar o caminho do usuário no ConfigManager
        self.config_manager.set_user_path(str(self.user_dir))
        
        # Criar MCPManager especificando o arquivo de configuração temporário
        with patch('src.core.mcp_manager.ConfigManager') as mock_config_manager:
            mock_instance = MagicMock()
            mock_instance.get_user_path.return_value = str(self.user_dir)
            mock_instance.get_cli_type.return_value = "gemini"
            mock_config_manager.return_value = mock_instance
            
            manager = MCPManager()
        
        # Verificar se o caminho foi configurado corretamente
        expected_path = self.user_dir / ".gemini" / "settings.json"
        self.assertEqual(manager.settings_path, expected_path)

    def test_mcp_manager_fallback_to_home(self):
        """Testa MCPManager fallback para Path.home() quando não há configuração."""
        # Criar MCPManager sem configuração (não deve encontrar ConfigManager)
        with patch('src.core.mcp_manager.ConfigManager') as mock_config_manager:
            mock_instance = MagicMock()
            mock_instance.get_user_path.return_value = None
            mock_instance.get_cli_type.return_value = "gemini"
            mock_config_manager.return_value = mock_instance
            
            manager = MCPManager()
            
            # Verificar se usa Path.home() como fallback
            expected_path = Path.home() / ".gemini" / "settings.json"
            self.assertEqual(manager.settings_path, expected_path)

    def test_mcp_manager_path_normalization(self):
        """Testa normalização de caminho no MCPManager."""
        # Configurar caminho com ~ (home) no ConfigManager
        self.config_manager.set_user_path(str(self.user_dir))
        
        # Mock para simular caminho com ~
        with patch('src.core.mcp_manager.ConfigManager') as mock_config_manager:
            mock_instance = MagicMock()
            # Simular caminho com ~ que precisa ser expandido
            mock_instance.get_user_path.return_value = str(self.user_dir).replace(str(Path.home()), "~")
            mock_instance.get_cli_type.return_value = "gemini"
            mock_config_manager.return_value = mock_instance
            
            manager = MCPManager()
            
            # Verificar se o caminho foi normalizado corretamente
            expected_path = self.user_dir / ".gemini" / "settings.json"
            self.assertEqual(manager.settings_path, expected_path)

    def test_mcp_operations_with_integration(self):
        """Testa operações MCP com integração ConfigManager."""
        # Configurar o caminho do usuário
        self.config_manager.set_user_path(str(self.user_dir))
        
        # Criar MCPManager com mock para usar nosso diretório temporário
        with patch('src.core.mcp_manager.ConfigManager') as mock_config_manager:
            mock_instance = MagicMock()
            mock_instance.get_user_path.return_value = str(self.user_dir)
            mock_instance.get_cli_type.return_value = "gemini"
            mock_config_manager.return_value = mock_instance
            
            manager = MCPManager()
        
        # Adicionar um MCP
        manager.add_mcp("test-mcp", "python", ["-m", "test"])
        
        # Verificar se foi adicionado
        mcps = manager.get_mcps()
        self.assertIn("test-mcp", mcps)
        self.assertEqual(mcps["test-mcp"]["command"], "python")
        self.assertEqual(mcps["test-mcp"]["args"], ["-m", "test"])
        
        # Ativar o MCP
        manager.toggle_allowed("test-mcp", True)
        
        # Verificar se foi ativado
        mcps = manager.get_mcps()
        self.assertTrue(mcps["test-mcp"]["enabled"])
        
        # Remover o MCP
        manager.remove_mcp("test-mcp")
        
        # Verificar se foi removido
        mcps = manager.get_mcps()
        self.assertNotIn("test-mcp", mcps)


    def test_refresh_settings_path(self):
        """Testa o método refresh_settings_path."""
        # Configurar o caminho do usuário
        self.config_manager.set_user_path(str(self.user_dir))
        
        # Mudar o caminho do usuário
        new_user_dir = Path(self.temp_dir) / "new_user"
        new_user_dir.mkdir()
        new_gemini_dir = new_user_dir / ".gemini"
        new_gemini_dir.mkdir()
        
        # Criar novo settings.json
        new_settings_file = new_gemini_dir / "settings.json"
        initial_settings = {
            "ide": {"hasSeenNudge": True, "enabled": True},
            "mcp": {"allowed": []},
            "mcpServers": {},
            "security": {"auth": {"selectedType": "oauth-personal"}},
            "ui": {"theme": "Default"}
        }
        with open(new_settings_file, 'w', encoding='utf-8') as f:
            json.dump(initial_settings, f, indent=2)
        
        # Criar MCPManager com mock para usar nosso diretório temporário
        with patch('src.core.mcp_manager.ConfigManager') as mock_config_manager:
            mock_instance = MagicMock()
            mock_instance.get_user_path.return_value = str(self.user_dir)
            mock_instance.get_cli_type.return_value = "gemini"
            mock_config_manager.return_value = mock_instance
            
            manager = MCPManager()
            
            # Adicionar um MCP
            manager.add_mcp("refresh-test", "python", ["-m", "test"])
            
            # Configurar novo caminho no ConfigManager
            self.config_manager.set_user_path(str(new_user_dir))
            
            # Atualizar o mock para retornar o novo caminho
            mock_instance.get_user_path.return_value = str(new_user_dir)
            mock_instance.get_cli_type.return_value = "gemini"
            
            # Atualizar o caminho no MCPManager
            manager.refresh_settings_path()
            
            # Verificar se o caminho foi atualizado
            expected_path = new_user_dir / ".gemini" / "settings.json"
            self.assertEqual(manager.settings_path, expected_path)
            
            # Verificar se o cache foi limpo
            self.assertIsNone(manager._settings_cache)

    def test_error_handling_with_invalid_config(self):
        """Testa tratamento de erros com configuração inválida."""
        # Mock para simular erro no ConfigManager
        with patch('src.core.mcp_manager.ConfigManager') as mock_config_manager:
            mock_instance = MagicMock()
            mock_instance.get_user_path.side_effect = ConfigManagerError("Erro de configuração")
            mock_instance.get_cli_type.return_value = "gemini"
            mock_config_manager.return_value = mock_instance
            
            # MCPManager deve fazer fallback para Path.home()
            manager = MCPManager()
            expected_path = Path.home() / ".gemini" / "settings.json"
            self.assertEqual(manager.settings_path, expected_path)


if __name__ == "__main__":
    unittest.main()
