#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes para a funcionalidade de operações em lote da GUI
"""

import unittest
import sys
import os
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.mcp_manager import MCPManager, MCPManagerError


class TestGUIBatch(unittest.TestCase):
    """Testes para operações em lote da GUI do MCPManager"""

    def setUp(self):
        """Configura ambiente de teste."""
        self.manager = MCPManager()

    def test_gui_batch_logic(self):
        """Testa a lógica de operações em lote que seria usada pela GUI."""
        # Garantir que temos pelo menos 2 MCPs
        mcps = self.manager.get_mcps()
        if len(mcps) < 2:
            # Instalar templates para teste
            templates_to_install = ["context7", "chrome-devtools"]
            
            for template in templates_to_install:
                try:
                    if not self.manager.is_template_installed(template):
                        self.manager.install_from_template(template, enable=False)
                except Exception:
                    pass  # Ignorar erros na instalação de templates
            
            mcps = self.manager.get_mcps()
        
        mcp_names = list(mcps.keys())
        if len(mcp_names) < 2:
            self.skipTest("É necessário pelo menos 2 MCPs para o teste")
        
        # Salvar estados originais
        original_states = {name: mcps[name]['enabled'] for name in mcp_names}
        
        try:
            # Simular cliques do usuário (acumulando mudanças)
            names_to_enable = []
            names_to_disable = []
            
            # Simular clique no primeiro MCP (alternar estado)
            first_mcp = mcp_names[0]
            if original_states[first_mcp]:
                names_to_disable.append(first_mcp)
            else:
                names_to_enable.append(first_mcp)
            
            # Simular clique no segundo MCP (alternar estado)
            second_mcp = mcp_names[1]
            if original_states[second_mcp]:
                names_to_disable.append(second_mcp)
            else:
                names_to_enable.append(second_mcp)
            
            # Verificar se há mudanças pendentes
            pending_changes = len(names_to_enable) > 0 or len(names_to_disable) > 0
            self.assertTrue(pending_changes, "Deveria haver mudanças pendentes")
            
            # Simular clique no botão "Salvar" (aplicar mudanças em lote)
            result = self.manager.set_allowed_many(names_to_enable, names_to_disable)
            self.assertTrue(result, "Operação em lote deveria ter sucesso")
            
            # Verificar estados finais
            updated_mcps = self.manager.get_mcps()
            final_states = {name: updated_mcps[name]['enabled'] for name in mcp_names}
            
            # Verificar se as mudanças foram aplicadas corretamente
            for name in names_to_enable:
                self.assertTrue(final_states[name], 
                               f"MCP '{name}' deveria estar habilitado")
            
            for name in names_to_disable:
                self.assertFalse(final_states[name], 
                                f"MCP '{name}' deveria estar desabilitado")
        
        finally:
            # Restaurar estados originais
            restore_enable = [name for name, enabled in original_states.items() if enabled]
            restore_disable = [name for name, enabled in original_states.items() if not enabled]
            self.manager.set_allowed_many(restore_enable, restore_disable)

    def test_no_pending_changes(self):
        """Testa comportamento quando não há mudanças pendentes."""
        mcps = self.manager.get_mcps()
        if len(mcps) < 1:
            self.skipTest("É necessário pelo menos 1 MCP para o teste")
        
        # Tentar aplicar operação em lote sem mudanças
        result = self.manager.set_allowed_many([], [])
        self.assertTrue(result, "Operação sem mudanças deveria ter sucesso")


if __name__ == "__main__":
    unittest.main()