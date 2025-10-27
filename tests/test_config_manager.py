#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes simples para o ConfigManager.
"""

import unittest
import tempfile
import os
import json
from pathlib import Path
import sys

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.config_manager import ConfigManager, ConfigManagerError


class TestConfigManager(unittest.TestCase):
    """Testes para a classe ConfigManager."""
    
    def setUp(self):
        """Configuração inicial para cada teste."""
        # Criar um diretório temporário para os testes
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
        self.config_manager = ConfigManager(str(self.config_path))
    
    def tearDown(self):
        """Limpeza após cada teste."""
        # Remover arquivos de teste
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_with_default_path(self):
        """Testa inicialização com caminho padrão."""
        config = ConfigManager()
        self.assertIsInstance(config.config_path, Path)
        self.assertEqual(config.config_path.name, "mcp_config.json")
    
    def test_init_with_custom_path(self):
        """Testa inicialização com caminho personalizado."""
        custom_path = Path(self.temp_dir) / "custom_config.json"
        config = ConfigManager(str(custom_path))
        self.assertEqual(config.config_path, custom_path)
    
    def test_get_user_path_no_config(self):
        """Testa get_user_path quando não há configuração."""
        result = self.config_manager.get_user_path()
        self.assertIsNone(result)
    
    def test_set_user_path_valid(self):
        """Testa set_user_path com um caminho válido."""
        # Usar o diretório temporário como caminho válido
        success = self.config_manager.set_user_path(self.temp_dir)
        self.assertTrue(success)
        
        # Verificar se o caminho foi salvo
        result = self.config_manager.get_user_path()
        # O ConfigManager normaliza os caminhos para usar barras forward
        expected_path = str(Path(self.temp_dir)).replace("\\", "/")
        self.assertEqual(result, expected_path)
        
        # Verificar se o arquivo de configuração foi criado
        self.assertTrue(self.config_path.exists())
        
        # Verificar conteúdo do arquivo
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            # O ConfigManager normaliza os caminhos para usar barras forward
            expected_path = str(Path(self.temp_dir)).replace("\\", "/")
            self.assertEqual(config_data["user_base_path"], expected_path)
    
    def test_set_user_path_invalid(self):
        """Testa set_user_path com um caminho inválido."""
        with self.assertRaises(ConfigManagerError):
            self.config_manager.set_user_path("/caminho/que/nao/existe")
    
    def test_set_user_path_not_directory(self):
        """Testa set_user_path com um arquivo em vez de diretório."""
        # Criar um arquivo temporário
        temp_file = Path(self.temp_dir) / "temp_file.txt"
        temp_file.write_text("teste")
        
        with self.assertRaises(ConfigManagerError):
            self.config_manager.set_user_path(str(temp_file))
    
    def test_set_user_path_empty_string(self):
        """Testa set_user_path com string vazia."""
        with self.assertRaises(ConfigManagerError):
            self.config_manager.set_user_path("")
    
    def test_has_config_no_file(self):
        """Testa has_config quando não há arquivo de configuração."""
        result = self.config_manager.has_config()
        self.assertFalse(result)
    
    def test_has_config_with_file(self):
        """Testa has_config com arquivo de configuração válido."""
        # Configurar um caminho válido
        self.config_manager.set_user_path(self.temp_dir)
        
        result = self.config_manager.has_config()
        self.assertTrue(result)
    
    def test_has_config_with_invalid_content(self):
        """Testa has_config com arquivo de configuração inválido."""
        # Criar arquivo com conteúdo inválido
        with open(self.config_path, 'w', encoding='utf-8') as f:
            f.write('{"other_key": "value"}')
        
        result = self.config_manager.has_config()
        self.assertFalse(result)
    
    def test_load_config_no_file(self):
        """Testa _load_config quando não há arquivo."""
        result = self.config_manager._load_config()
        self.assertEqual(result, {})
    
    def test_load_config_with_file(self):
        """Testa _load_config com arquivo existente."""
        # Criar arquivo de configuração
        test_data = {"user_base_path": "/test/path", "other_key": "value"}
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        result = self.config_manager._load_config()
        self.assertEqual(result, test_data)
    
    def test_save_config(self):
        """Testa _save_config."""
        test_data = {"user_base_path": "/test/path", "other_key": "value"}
        self.config_manager._save_config(test_data)
        
        # Verificar se o arquivo foi criado
        self.assertTrue(self.config_path.exists())
        
        # Verificar conteúdo
        with open(self.config_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            self.assertEqual(saved_data, test_data)


if __name__ == "__main__":
    # Executar os testes
    unittest.main(verbosity=2)
