#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes para as operações em lote do MCPManager
"""

import unittest
import sys
import os
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.mcp_manager import MCPManager, MCPManagerError
from src.core.config_manager import ConfigManager


class TestBatchOperations(unittest.TestCase):
    """Testes para operações em lote do MCPManager"""

    def setUp(self):
        """Configura ambiente de teste."""
        self.manager = MCPManager()

    def test_set_allowed_many(self):
        """Testa o método set_allowed_many"""
        # Obter MCPs existentes
        mcps = self.manager.get_mcps()
        
        # Instalar templates se não houver MCPs suficientes
        if len(mcps) < 2:
            templates_to_install = ["context7", "chrome-devtools"]
            
            for template in templates_to_install:
                try:
                    if not self.manager.is_template_installed(template):
                        self.manager.install_from_template(template, enable=False)
                except Exception:
                    pass  # Ignorar erros na instalação de templates
            
            # Recarregar MCPs após instalação
            mcps = self.manager.get_mcps()
        
        # Obter nomes dos MCPs para teste
        mcp_names = list(mcps.keys())
        if len(mcp_names) < 2:
            self.skipTest("É necessário pelo menos 2 MCPs para o teste")
        
        # Salvar estados originais
        original_states = {name: mcps[name]['enabled'] for name in mcp_names}
        
        try:
            # Habilitar o primeiro, desabilitar o segundo
            names_to_enable = [mcp_names[0]]
            names_to_disable = [mcp_names[1]] if len(mcp_names) > 1 else []
            
            # Aplicar mudanças em lote
            result = self.manager.set_allowed_many(names_to_enable, names_to_disable)
            self.assertTrue(result)
            
            # Verificar estados após a operação
            updated_mcps = self.manager.get_mcps()
            updated_states = {name: updated_mcps[name]['enabled'] for name in mcp_names}
            
            # Verificar se as mudanças foram aplicadas corretamente
            for name in names_to_enable:
                self.assertTrue(updated_mcps[name]['enabled'], 
                               f"MCP '{name}' deveria estar habilitado")
            
            for name in names_to_disable:
                self.assertFalse(updated_mcps[name]['enabled'], 
                                f"MCP '{name}' deveria estar desabilitado")
        
        finally:
            # Restaurar estados originais
            restore_enable = [name for name, enabled in original_states.items() if enabled]
            restore_disable = [name for name, enabled in original_states.items() if not enabled]
            self.manager.set_allowed_many(restore_enable, restore_disable)

    def test_error_handling(self):
        """Testa o tratamento de erros"""
        # Tentar habilitar/desabilitar MCPs que não existem
        with self.assertRaises(MCPManagerError):
            self.manager.set_allowed_many(["mcp_inexistente_1"], ["mcp_inexistente_2"])


if __name__ == "__main__":
    unittest.main()