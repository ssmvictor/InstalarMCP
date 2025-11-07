"""
Testes para o módulo SpecKitManager.
"""

import unittest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from pathlib import Path

# Adicionar o diretório src ao path para importar o módulo
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.speckit_manager import SpecKitManager


class TestSpecKitManager(unittest.TestCase):
    """Classe de testes para SpecKitManager."""
    
    def setUp(self):
        """Configuração inicial para cada teste."""
        # Criar um diretório temporário para os testes
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock para verificar se estamos no Windows
        self.patcher = patch('os.name', 'nt')
        self.patcher.start()
        
        # Criar uma instância do SpecKitManager
        self.manager = SpecKitManager()
    
    def tearDown(self):
        """Limpeza após cada teste."""
        # Restaurar o patch
        self.patcher.stop()
        
        # Remover o diretório temporário
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_add_to_process_path_if_missing_new_path(self):
        """Testa adicionar um novo caminho ao PATH do processo."""
        # Salvar o PATH original
        original_path = os.environ.get('PATH', '')
        
        try:
            # Criar um diretório de teste
            test_dir = os.path.join(self.temp_dir, 'test_bin')
            os.makedirs(test_dir)
            
            # Limpar o PATH para o teste
            os.environ['PATH'] = ''
            os.environ['Path'] = ''
            
            # Chamar o método privado
            result = self.manager._SpecKitManager__add_to_process_path_if_missing(test_dir, True)
            
            # Verificar se o caminho foi adicionado
            self.assertTrue(result)
            self.assertIn(test_dir, os.environ.get('PATH', ''))
            self.assertIn(test_dir, os.environ.get('Path', ''))
            
        finally:
            # Restaurar o PATH original
            os.environ['PATH'] = original_path
            if 'Path' in os.environ:
                del os.environ['Path']
    
    def test_add_to_process_path_if_missing_existing_path(self):
        """Testa tentar adicionar um caminho que já existe no PATH."""
        # Salvar o PATH original
        original_path = os.environ.get('PATH', '')
        
        try:
            # Criar um diretório de teste
            test_dir = os.path.join(self.temp_dir, 'test_bin')
            os.makedirs(test_dir)
            
            # Adicionar o caminho ao PATH
            os.environ['PATH'] = test_dir
            os.environ['Path'] = test_dir
            
            # Chamar o método privado
            result = self.manager._SpecKitManager__add_to_process_path_if_missing(test_dir, True)
            
            # Verificar que o método retornou True (caminho já existia)
            self.assertTrue(result)
            
            # Verificar que o caminho não foi duplicado
            path_components = os.environ.get('PATH', '').split(os.pathsep)
            self.assertEqual(path_components.count(test_dir), 1)
            
        finally:
            # Restaurar o PATH original
            os.environ['PATH'] = original_path
            if 'Path' in os.environ:
                del os.environ['Path']
    
    def test_add_to_process_path_if_missing_nonexistent_path(self):
        """Testa tentar adicionar um caminho que não existe."""
        # Salvar o PATH original
        original_path = os.environ.get('PATH', '')
        
        try:
            # Caminho que não existe
            nonexistent_path = os.path.join(self.temp_dir, 'nonexistent')
            
            # Limpar o PATH para o teste
            os.environ['PATH'] = ''
            os.environ['Path'] = ''
            
            # Chamar o método privado
            result = self.manager._SpecKitManager__add_to_process_path_if_missing(nonexistent_path, True)
            
            # Verificar que o método retornou False
            self.assertFalse(result)
            
            # Verificar que o caminho não foi adicionado
            self.assertNotIn(nonexistent_path, os.environ.get('PATH', ''))
            self.assertNotIn(nonexistent_path, os.environ.get('Path', ''))
            
        finally:
            # Restaurar o PATH original
            os.environ['PATH'] = original_path
            if 'Path' in os.environ:
                del os.environ['Path']
    
    def test_add_to_process_path_if_missing_insert_at_end(self):
        """Testa adicionar um caminho ao final do PATH."""
        # Salvar o PATH original
        original_path = os.environ.get('PATH', '')
        
        try:
            # Criar dois diretórios de teste
            test_dir1 = os.path.join(self.temp_dir, 'test_bin1')
            test_dir2 = os.path.join(self.temp_dir, 'test_bin2')
            os.makedirs(test_dir1)
            os.makedirs(test_dir2)
            
            # Adicionar o primeiro diretório ao PATH
            os.environ['PATH'] = test_dir1
            os.environ['Path'] = test_dir1
            
            # Chamar o método privado para adicionar o segundo diretório ao final
            result = self.manager._SpecKitManager__add_to_process_path_if_missing(test_dir2, False)
            
            # Verificar se o caminho foi adicionado
            self.assertTrue(result)
            
            # Verificar que o segundo diretório está no final do PATH
            path_components = os.environ.get('PATH', '').split(os.pathsep)
            self.assertEqual(path_components[0], test_dir1)
            self.assertEqual(path_components[1], test_dir2)
            
        finally:
            # Restaurar o PATH original
            os.environ['PATH'] = original_path
            if 'Path' in os.environ:
                del os.environ['Path']


if __name__ == '__main__':
    unittest.main()