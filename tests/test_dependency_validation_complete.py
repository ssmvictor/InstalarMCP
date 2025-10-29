#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes completos para a funcionalidade de validação de dependências
"""

import unittest
import sys
import os
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.mcp_manager import MCPManager, MCPManagerError, MCP_TEMPLATES


class TestDependencyValidationComplete(unittest.TestCase):
    """Testes completos para validação de dependências do MCPManager"""

    def setUp(self):
        """Configura ambiente de teste."""
        self.manager = MCPManager()
        # Salvar templates originais para restaurar depois
        self.original_templates = MCP_TEMPLATES.copy()

    def tearDown(self):
        """Limpa ambiente de teste."""
        # Restaurar templates originais
        MCP_TEMPLATES.clear()
        MCP_TEMPLATES.update(self.original_templates)

    def test_with_mock_template(self):
        """Testa validação de dependências com um template mock."""
        # Adicionar um template mock com comando inexistente
        MCP_TEMPLATES['test-mock'] = {
            "name": "test-mock",
            "command": "comando_inexistente_12345",
            "args": ["--test"],
            "description": "Template de teste com comando inexistente"
        }
        
        # Verificar dependências
        missing = self.manager.get_missing_dependencies('test-mock')
        self.assertIn('comando_inexistente_12345', missing, 
                     "Comando inexistente deveria estar na lista de dependências ausentes")
        
        # Tentar instalar sem ignorar verificação de dependências (deve falhar)
        with self.assertRaises(MCPManagerError):
            self.manager.install_from_template('test-mock', enable=False)
        
        # Tentar instalar ignorando verificação de dependências (deve sucesso)
        self.manager.install_from_template('test-mock', enable=False, skip_dependency_check=True)
        
        # Remover a instalação de teste
        self.manager.remove_mcp('test-mock')

    def test_gui_integration(self):
        """Testa a lógica de integração com GUI."""
        # Simular diferentes cenários
        test_scenarios = [
            {
                'name': 'context7',
                'expected_deps': ['npx'],
                'description': 'Template que requer npx'
            },
            {
                'name': 'excel-data-manager', 
                'expected_deps': ['uvx'],
                'description': 'Template que requer uvx'
            }
        ]
        
        for scenario in test_scenarios:
            with self.subTest(scenario=scenario):
                # Verificar se o template existe
                templates = self.manager.get_templates()
                if scenario['name'] not in templates:
                    self.skipTest(f"Template '{scenario['name']}' não encontrado")
                
                # Verificar dependências
                missing = self.manager.get_missing_dependencies(scenario['name'])
                
                # Verificar se as dependências esperadas estão na lista de ausentes
                for dep in scenario['expected_deps']:
                    if dep in missing:
                        # Simular lógica da GUI para criar mensagem de instrução
                        dep_list = ", ".join(missing)
                        install_instructions = []
                        
                        for missing_dep in missing:
                            if missing_dep == "npx":
                                install_instructions.append("• npx: Instale Node.js (https://nodejs.org/)")
                            elif missing_dep == "uvx":
                                install_instructions.append("• uvx: Instale Python e uv (pip install uv)")
                            else:
                                install_instructions.append(f"• {missing_dep}: Verifique instalação")
                        
                        # Verificar que as instruções foram criadas
                        self.assertGreater(len(install_instructions), 0, 
                                         "Deveria haver instruções de instalação")
                        
                        # Verificar que a mensagem contém informações relevantes
                        message = f"Dependências ausentes para o template '{scenario['name']}':\n\n"
                        message += f"Comandos não encontrados: {dep_list}\n\n"
                        message += "Para instalar:\n"
                        message += "\n".join(install_instructions)
                        
                        self.assertIn(scenario['name'], message)
                        self.assertIn(dep_list, message)
                        self.assertIn("Para instalar:", message)
                    else:
                        # Se a dependência não está ausente, verificamos se está disponível
                        available = self.manager.check_command_availability(dep)
                        self.assertTrue(available, f"Dependência '{dep}' deveria estar disponível")


if __name__ == "__main__":
    unittest.main()