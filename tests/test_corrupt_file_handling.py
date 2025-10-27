#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes específicos para as melhorias no tratamento de arquivos corrompidos.
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


class TestCorruptFileHandling(unittest.TestCase):
    """Testes para as melhorias no tratamento de arquivos corrompidos."""

    def setUp(self):
        """Configura ambiente de teste."""
        # Criar diretórios temporários
        self.temp_dir = tempfile.mkdtemp()
        self.gemini_dir = Path(self.temp_dir) / ".gemini"
        self.gemini_dir.mkdir()
        
        # Arquivo settings.json
        self.settings_file = self.gemini_dir / "settings.json"

    def tearDown(self):
        """Limpa ambiente de teste."""
        shutil.rmtree(self.temp_dir)

    def test_corrupt_file_with_multiple_attempts(self):
        """Testa tratamento de arquivo corrompido com múltiplas tentativas de renomeamento."""
        # Criar arquivo JSON corrompido
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            f.write("{ invalid json content")
        
        # Criar MCPManager
        manager = MCPManager(str(self.settings_file))
        
        # Tentar carregar configurações (deve renomear arquivo corrompido)
        settings = manager.load_settings()
        
        # Verificar se criou estrutura padrão
        self.assertIn('mcp', settings)
        self.assertIn('mcpServers', settings)
        
        # Verificar se arquivo corrompido foi renomeado
        corrupt_files = list(self.gemini_dir.glob("settings.json.corrupt.*"))
        self.assertEqual(len(corrupt_files), 1)
        
        # O arquivo original não é recriado automaticamente, apenas o cache é atualizado
        # Verificar se o cache foi atualizado com estrutura padrão
        self.assertIn('mcp', settings)
        self.assertIn('mcpServers', settings)

    def test_corrupt_file_with_existing_corrupt_files(self):
        """Testa tratamento de arquivo corrompido quando já existem arquivos corrompidos."""
        # Criar arquivos corrompidos existentes
        for i in range(3):
            corrupt_file = self.gemini_dir / f"settings.json.corrupt.20230101_120000_{i}"
            with open(corrupt_file, 'w', encoding='utf-8') as f:
                f.write(f"corrupt content {i}")
        
        # Criar arquivo JSON corrompido
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            f.write("{ invalid json content")
        
        # Criar MCPManager
        manager = MCPManager(str(self.settings_file))
        
        # Tentar carregar configurações (deve renomear arquivo corrompido)
        settings = manager.load_settings()
        
        # Verificar se criou estrutura padrão
        self.assertIn('mcp', settings)
        
        # Verificar se arquivo corrompido foi renomeado com sufixo único
        corrupt_files = list(self.gemini_dir.glob("settings.json.corrupt.*"))
        self.assertEqual(len(corrupt_files), 4)  # 3 existentes + 1 novo
        
        # Verificar se há um novo arquivo corrompido (com timestamp atual)
        # O UUID só é adicionado em tentativas subsequentes, não na primeira
        # Procuramos por arquivos que não seguem o padrão dos existentes
        new_corrupt_files = [f for f in corrupt_files if not f.name.startswith("settings.json.corrupt.20230101_120000_")]
        self.assertEqual(len(new_corrupt_files), 1)

    def test_path_resolve_fallback_on_windows(self):
        """Testa fallback de Path.resolve() no Windows."""
        # Criar um caminho que pode causar problemas com resolve()
        user_path = "//?/C:/NonExistent/Path"
        
        # Mock para simular erro no resolve()
        with patch('pathlib.Path.resolve') as mock_resolve:
            mock_resolve.side_effect = OSError("Permission denied")
            
            # Criar MCPManager
            with patch('src.core.mcp_manager.ConfigManager') as mock_config_manager:
                mock_instance = MagicMock()
                mock_instance.get_user_path.return_value = user_path
                mock_instance.get_cli_type.return_value = "gemini"
                mock_config_manager.return_value = mock_instance
                
                manager = MCPManager()
                
                # Verificar se usou expanduser() apenas (sem resolve)
                # O caminho deve ser o mesmo, mas sem ter sido processado por resolve()
                expected_path = Path(user_path).expanduser() / ".gemini" / "settings.json"
                self.assertEqual(manager.settings_path, expected_path)


if __name__ == "__main__":
    unittest.main()
