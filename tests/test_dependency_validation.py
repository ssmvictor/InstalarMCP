#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes para a funcionalidade de validação de dependências
"""

import unittest
import sys
import os
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.mcp_manager import MCPManager, MCPManagerError


class TestDependencyValidation(unittest.TestCase):
    """Testes para validação de dependências do MCPManager"""

    def setUp(self):
        """Configura ambiente de teste."""
        self.manager = MCPManager()

    def test_command_availability(self):
        """Testa o método check_command_availability."""
        # Testar com comandos comuns que devem existir
        common_commands = ['python', 'cmd', 'echo']
        for cmd in common_commands:
            available = self.manager.check_command_availability(cmd)
            self.assertTrue(available, f"Comando '{cmd}' deveria estar disponível")
        
        # Testar com comandos que podem não existir
        uncommon_commands = ['nonexistent_command_12345']
        for cmd in uncommon_commands:
            available = self.manager.check_command_availability(cmd)
            self.assertFalse(available, f"Comando '{cmd}' não deveria estar disponível")

    def test_missing_dependencies(self):
        """Testa o método get_missing_dependencies."""
        # Testar com todos os templates disponíveis
        templates = self.manager.get_templates()
        
        for template_name in templates:
            try:
                missing = self.manager.get_missing_dependencies(template_name)
                # Verificar que o método retorna uma lista
                self.assertIsInstance(missing, list, 
                                    f"get_missing_dependencies deveria retornar uma lista para '{template_name}'")
            except MCPManagerError as e:
                # Alguns templates podem ter erros na configuração
                self.fail(f"Erro ao verificar template '{template_name}': {e}")

    def test_template_installation_with_validation(self):
        """Testa instalação de templates com validação de dependências."""
        # Testar com templates que podem ter dependências ausentes
        test_templates = ['context7', 'chrome-devtools']
        
        for template_name in test_templates:
            with self.subTest(template=template_name):
                # Verificar se o template existe
                templates = self.manager.get_templates()
                if template_name not in templates:
                    self.skipTest(f"Template '{template_name}' não encontrado")
                
                # Verificar se já está instalado
                if self.manager.is_template_installed(template_name):
                    self.skipTest(f"Template '{template_name}' já está instalado")
                
                # Verificar dependências
                missing = self.manager.get_missing_dependencies(template_name)
                
                if missing:
                    # Tentar instalar sem ignorar verificação de dependências (deve falhar)
                    with self.assertRaises(MCPManagerError):
                        self.manager.install_from_template(template_name, enable=False)
                    
                    # Tentar instalar ignorando verificação de dependências (deve sucesso)
                    self.manager.install_from_template(template_name, enable=False, skip_dependency_check=True)
                    
                    # Remover a instalação de teste
                    template = templates[template_name]
                    self.manager.remove_mcp(template['name'])
                else:
                    # Tentar instalar (deve sucesso)
                    self.manager.install_from_template(template_name, enable=False)
                    
                    # Remover a instalação de teste
                    template = templates[template_name]
                    self.manager.remove_mcp(template['name'])


if __name__ == "__main__":
    unittest.main()