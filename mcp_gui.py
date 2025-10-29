#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface Gráfica para Gerenciamento de Servidores MCP (Model Context Protocol)

Este módulo fornece uma interface gráfica usando Tkinter para gerenciar
servidores MCP, permitindo selecionar o CLI (Gemini/Qwen) e configurar
os servidores disponíveis.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import logging
import sys
import os
from pathlib import Path

# Adicionar o diretório src ao path para importar os módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.config_manager import ConfigManager, ConfigManagerError
from src.core.mcp_manager import MCPManager, MCPManagerError

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCPGUI:
    """
    Classe principal da Interface Gráfica do MCP Manager
    """
    
    def __init__(self):
        """
        Inicializa a interface gráfica com tratamento de erro para o tema 'arc'
        """
        self.root = None
        self.style = None
        self.config_manager = None
        self.mcp_manager = None
        self.mcp_vars = {}
        self.pending_changes = False
        
        # Inicializar a janela principal com tratamento de erro para o tema
        self._init_window_with_theme()
        
        # Inicializar os gerenciadores
        self._init_managers()
        
        # Configurar a interface
        self._setup_ui()
        
        # Carregar dados iniciais
        self._load_initial_data()
    
    def _init_window_with_theme(self):
        """
        Inicializa a janela principal com tratamento de erro para o tema 'arc'
        """
        try:
            # Tentar usar ThemedTk com o tema 'arc'
            from ttkthemes import ThemedTk
            self.root = ThemedTk(theme="arc")
            logger.info("Tema 'arc' do ttkthemes carregado com sucesso")
            
            # Configurar o estilo
            self.style = ttk.Style()
            
            # Verificar se o tema 'arc' está realmente disponível
            available_themes = self.style.theme_names()
            if "arc" not in available_themes:
                logger.warning("Tema 'arc' não está na lista de temas disponíveis, usando tema padrão")
                self.style.theme_use("default")
            else:
                self.style.theme_use("arc")
                
        except ImportError:
            logger.warning("ttkthemes não disponível, usando Tkinter padrão")
            # Fallback para Tkinter padrão
            self.root = tk.Tk()
            self.style = ttk.Style()
            self.style.theme_use("default")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar o tema 'arc': {e}")
            # Fallback para Tkinter padrão em caso de qualquer erro
            self.root = tk.Tk()
            self.style = ttk.Style()
            
            # Tentar usar um tema padrão disponível
            try:
                available_themes = self.style.theme_names()
                if "clam" in available_themes:
                    self.style.theme_use("clam")
                elif "alt" in available_themes:
                    self.style.theme_use("alt")
                else:
                    self.style.theme_use("default")
                logger.info(f"Usando tema fallback: {self.style.theme_use()}")
            except Exception as theme_error:
                logger.error(f"Erro ao definir tema fallback: {theme_error}")
                self.style.theme_use("default")
        
        # Configurar propriedades básicas da janela
        self.root.title("MCP Manager - Gerenciador de Servidores MCP")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Configurar o fechamento da janela
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _init_managers(self):
        """
        Inicializa os gerenciadores de configuração e MCP
        """
        try:
            self.config_manager = ConfigManager()
            self.mcp_manager = MCPManager()
            logger.info("Gerenciadores inicializados com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar gerenciadores: {e}")
            messagebox.showerror(
                "Erro de Inicialização",
                f"Não foi possível inicializar os gerenciadores:\n{e}"
            )
            sys.exit(1)
    
    def _setup_ui(self):
        """
        Configura os componentes da interface gráfica
        """
        # Criar o notebook para abas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Aba de Configuração
        self._setup_config_tab()
        
        # Aba de Servidores MCP
        self._setup_mcp_tab()
        
        # Aba de Templates
        self._setup_templates_tab()
        
        # Barra de status
        self._setup_status_bar()
    
    def _setup_config_tab(self):
        """
        Configura a aba de configuração do CLI
        """
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="Configuração")
        
        # Frame principal
        main_frame = ttk.Frame(config_frame, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Título
        title_label = ttk.Label(
            main_frame,
            text="Configuração do CLI",
            font=('TkDefaultFont', 14, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Frame para seleção do CLI
        cli_frame = ttk.LabelFrame(main_frame, text="Selecionar CLI", padding="10")
        cli_frame.pack(fill='x', pady=(0, 20))
        
        # Variável para o tipo de CLI
        self.cli_var = tk.StringVar()
        
        # Radio buttons para seleção do CLI
        ttk.Radiobutton(
            cli_frame,
            text="Gemini",
            variable=self.cli_var,
            value="gemini",
            command=self._on_cli_change
        ).pack(anchor='w', pady=5)
        
        ttk.Radiobutton(
            cli_frame,
            text="Qwen",
            variable=self.cli_var,
            value="qwen",
            command=self._on_cli_change
        ).pack(anchor='w', pady=5)
        
        # Frame para caminho do usuário
        path_frame = ttk.LabelFrame(main_frame, text="Caminho do Usuário", padding="10")
        path_frame.pack(fill='x', pady=(0, 20))
        
        # Label para mostrar o caminho atual
        self.path_label = ttk.Label(path_frame, text="Carregando...")
        self.path_label.pack(anchor='w', pady=5)
        
        # Botão para alterar o caminho
        ttk.Button(
            path_frame,
            text="Alterar Caminho",
            command=self._change_user_path
        ).pack(pady=5)
        
        # Botão para salvar configurações
        ttk.Button(
            main_frame,
            text="Salvar Configurações",
            command=self._save_config
        ).pack(pady=10)
    
    def _setup_mcp_tab(self):
        """
        Configura a aba de gerenciamento de servidores MCP
        """
        mcp_frame = ttk.Frame(self.notebook)
        self.notebook.add(mcp_frame, text="Servidores MCP")
        
        # Frame principal
        main_frame = ttk.Frame(mcp_frame, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Título
        title_label = ttk.Label(
            main_frame,
            text="Servidores MCP Configurados",
            font=('TkDefaultFont', 14, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Frame para lista de MCPs
        list_frame = ttk.LabelFrame(main_frame, text="Servidores", padding="10")
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Scrollable frame para a lista de MCPs
        canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.mcp_list_frame = ttk.Frame(canvas)
        
        self.mcp_list_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.mcp_list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Frame para botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=10)
        
        ttk.Button(
            button_frame,
            text="Adicionar MCP",
            command=self._add_mcp_dialog
        ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame,
            text="Salvar Alterações",
            command=self._save_mcp_changes
        ).pack(side='left', padx=5)
        
        # Label para mostrar status das alterações
        self.changes_label = ttk.Label(button_frame, text="")
        self.changes_label.pack(side='left', padx=20)
    
    def _setup_templates_tab(self):
        """
        Configura a aba de templates de MCP
        """
        templates_frame = ttk.Frame(self.notebook)
        self.notebook.add(templates_frame, text="Templates")
        
        # Frame principal
        main_frame = ttk.Frame(templates_frame, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Título
        title_label = ttk.Label(
            main_frame,
            text="Templates Disponíveis",
            font=('TkDefaultFont', 14, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Frame para lista de templates
        list_frame = ttk.LabelFrame(main_frame, text="Templates", padding="10")
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Scrollable frame para a lista de templates
        canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.templates_list_frame = ttk.Frame(canvas)
        
        self.templates_list_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.templates_list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _setup_status_bar(self):
        """
        Configura a barra de status
        """
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill='x', side='bottom')
        
        self.status_label = ttk.Label(status_frame, text="Pronto", relief='sunken')
        self.status_label.pack(fill='x', padx=2, pady=2)
    
    def _load_initial_data(self):
        """
        Carrega os dados iniciais na interface
        """
        try:
            # Carregar configuração do CLI
            cli_type = self.config_manager.get_cli_type()
            self.cli_var.set(cli_type)
            
            # Carregar caminho do usuário
            user_path = self.config_manager.get_user_path()
            if user_path:
                self.path_label.config(text=user_path)
            else:
                self.path_label.config(text="Não configurado")
            
            # Carregar lista de MCPs
            self._refresh_mcp_list()
            
            # Carregar lista de templates
            self._refresh_templates_list()
            
            self.status_label.config(text="Dados carregados com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados iniciais: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar dados:\n{e}")
    
    def _refresh_mcp_list(self):
        """
        Atualiza a lista de MCPs na interface
        """
        # Limpar widgets existentes
        for widget in self.mcp_list_frame.winfo_children():
            widget.destroy()
        
        self.mcp_vars.clear()
        
        try:
            mcps = self.mcp_manager.get_mcps()
            
            if not mcps:
                ttk.Label(
                    self.mcp_list_frame,
                    text="Nenhum servidor MCP configurado"
                ).pack(pady=20)
                return
            
            for name, details in mcps.items():
                # Frame para cada MCP
                mcp_frame = ttk.Frame(self.mcp_list_frame)
                mcp_frame.pack(fill='x', pady=5, padx=5)
                
                # Checkbox para habilitar/desabilitar
                var = tk.BooleanVar(value=details.get('enabled', False))
                self.mcp_vars[name] = var
                
                cb = ttk.Checkbutton(
                    mcp_frame,
                    text=name,
                    variable=var,
                    command=self._on_mcp_toggle
                )
                cb.pack(side='left')
                
                # Label com detalhes do comando
                cmd_label = ttk.Label(
                    mcp_frame,
                    text=f"Comando: {details.get('command', '')}",
                    font=('TkDefaultFont', 9)
                )
                cmd_label.pack(side='left', padx=(20, 0))
                
                # Botão para remover
                ttk.Button(
                    mcp_frame,
                    text="Remover",
                    command=lambda n=name: self._remove_mcp(n)
                ).pack(side='right', padx=(5, 0))
                
                # Botão para editar
                ttk.Button(
                    mcp_frame,
                    text="Editar",
                    command=lambda n=name: self._edit_mcp(n)
                ).pack(side='right', padx=(5, 0))
        
        except Exception as e:
            logger.error(f"Erro ao atualizar lista de MCPs: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar MCPs:\n{e}")
    
    def _refresh_templates_list(self):
        """
        Atualiza a lista de templates na interface
        """
        # Limpar widgets existentes
        for widget in self.templates_list_frame.winfo_children():
            widget.destroy()
        
        try:
            templates = self.mcp_manager.get_templates()
            
            if not templates:
                ttk.Label(
                    self.templates_list_frame,
                    text="Nenhum template disponível"
                ).pack(pady=20)
                return
            
            for name, template in templates.items():
                # Frame para cada template
                template_frame = ttk.Frame(self.templates_list_frame)
                template_frame.pack(fill='x', pady=5, padx=5)
                
                # Nome do template
                name_label = ttk.Label(
                    template_frame,
                    text=name,
                    font=('TkDefaultFont', 10, 'bold')
                )
                name_label.pack(anchor='w')
                
                # Descrição
                desc_label = ttk.Label(
                    template_frame,
                    text=template.get('description', ''),
                    font=('TkDefaultFont', 9)
                )
                desc_label.pack(anchor='w', padx=(20, 0))
                
                # Comando
                cmd_label = ttk.Label(
                    template_frame,
                    text=f"Comando: {template.get('command', '')}",
                    font=('TkDefaultFont', 9)
                )
                cmd_label.pack(anchor='w', padx=(20, 0))
                
                # Frame para botões
                button_frame = ttk.Frame(template_frame)
                button_frame.pack(fill='x', pady=5)
                
                # Verificar se já está instalado
                if self.mcp_manager.is_template_installed(name):
                    ttk.Label(
                        button_frame,
                        text="Já instalado",
                        foreground='green'
                    ).pack(side='left', padx=(20, 0))
                else:
                    ttk.Button(
                        button_frame,
                        text="Instalar",
                        command=lambda n=name: self._install_template(n)
                    ).pack(side='left', padx=(20, 0))
        
        except Exception as e:
            logger.error(f"Erro ao atualizar lista de templates: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar templates:\n{e}")
    
    def _on_cli_change(self):
        """
        Manipulador para mudança do tipo de CLI
        """
        # Primeiro persistir a mudança via ConfigManager antes de refresh_settings_path()
        try:
            self.config_manager.set_cli_type(self.cli_var.get())
            
            # Após persistir, então chamar refresh_settings_path() e _refresh_mcp_list()
            self.mcp_manager.refresh_settings_path()
            self._refresh_mcp_list()
            self.status_label.config(text=f"CLI alterado para {self.cli_var.get()}")
        except ConfigManagerError as e:
            logger.error(f"Erro ao persistir tipo de CLI: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar tipo de CLI:\n{e}")
            # Reverter a seleção na interface em caso de erro
            try:
                original_cli = self.config_manager.get_cli_type()
                self.cli_var.set(original_cli)
            except Exception:
                pass
        except Exception as e:
            logger.error(f"Erro ao alterar CLI: {e}")
            messagebox.showerror("Erro", f"Erro ao alterar CLI:\n{e}")
    
    def _on_mcp_toggle(self):
        """
        Manipulador para toggle de MCP
        """
        self.pending_changes = True
        self.changes_label.config(text="Há alterações pendentes", foreground='red')
    
    def _save_config(self):
        """
        Salva as configurações do CLI
        """
        try:
            cli_type = self.cli_var.get()
            self.config_manager.set_cli_type(cli_type)
            
            # Atualizar o MCP Manager
            self.mcp_manager.refresh_settings_path()
            self._refresh_mcp_list()
            
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
            self.status_label.config(text="Configurações salvas")
            
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar configurações:\n{e}")
    
    def _save_mcp_changes(self):
        """
        Salva as alterações nos MCPs
        """
        try:
            mcps = self.mcp_manager.get_mcps()
            
            names_to_enable = []
            names_to_disable = []
            
            for name, details in mcps.items():
                current_state = details.get('enabled', False)
                new_state = self.mcp_vars.get(name, tk.BooleanVar()).get()
                
                if current_state != new_state:
                    if new_state:
                        names_to_enable.append(name)
                    else:
                        names_to_disable.append(name)
            
            if names_to_enable or names_to_disable:
                self.mcp_manager.set_allowed_many(names_to_enable, names_to_disable)
                self.pending_changes = False
                self.changes_label.config(text="")
                messagebox.showinfo("Sucesso", "Alterações salvas com sucesso!")
                self.status_label.config(text="Alterações nos MCPs salvas")
            else:
                messagebox.showinfo("Informação", "Nenhuma alteração para salvar")
        
        except Exception as e:
            logger.error(f"Erro ao salvar alterações nos MCPs: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar alterações:\n{e}")
    
    def _change_user_path(self):
        """
        Abre diálogo para alterar o caminho do usuário
        """
        from tkinter import filedialog
        
        path = filedialog.askdirectory(
            title="Selecione o diretório do usuário",
            initialdir=str(self.config_manager.get_user_path() or Path.home())
        )
        
        if path:
            try:
                self.config_manager.set_user_path(path)
                self.path_label.config(text=path)
                
                # Atualizar o MCP Manager
                self.mcp_manager.refresh_settings_path()
                self._refresh_mcp_list()
                
                messagebox.showinfo("Sucesso", "Caminho do usuário alterado com sucesso!")
                self.status_label.config(text="Caminho do usuário alterado")
                
            except Exception as e:
                logger.error(f"Erro ao alterar caminho do usuário: {e}")
                messagebox.showerror("Erro", f"Erro ao alterar caminho:\n{e}")
    
    def _add_mcp_dialog(self):
        """
        Abre diálogo para adicionar um novo MCP
        """
        dialog = tk.Toplevel(self.root)
        dialog.title("Adicionar MCP")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Nome
        ttk.Label(main_frame, text="Nome:").grid(row=0, column=0, sticky='w', pady=5)
        name_entry = ttk.Entry(main_frame, width=30)
        name_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Comando
        ttk.Label(main_frame, text="Comando:").grid(row=1, column=0, sticky='w', pady=5)
        cmd_entry = ttk.Entry(main_frame, width=30)
        cmd_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Argumentos
        ttk.Label(main_frame, text="Argumentos:").grid(row=2, column=0, sticky='w', pady=5)
        args_text = tk.Text(main_frame, width=30, height=5)
        args_text.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Frame para botões
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        def save_mcp():
            name = name_entry.get().strip()
            command = cmd_entry.get().strip()
            args_text_content = args_text.get("1.0", tk.END).strip()
            
            if not name or not command:
                messagebox.showerror("Erro", "Nome e comando são obrigatórios")
                return
            
            # Processar argumentos
            args = []
            if args_text_content:
                args = [arg.strip() for arg in args_text_content.split('\n') if arg.strip()]
            
            try:
                self.mcp_manager.add_mcp(name, command, args)
                self._refresh_mcp_list()
                dialog.destroy()
                messagebox.showinfo("Sucesso", "MCP adicionado com sucesso!")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao adicionar MCP:\n{e}")
        
        ttk.Button(button_frame, text="Salvar", command=save_mcp).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancelar", command=dialog.destroy).pack(side='left', padx=5)
    
    def _edit_mcp(self, name):
        """
        Abre diálogo para editar um MCP existente
        """
        # Obter detalhes do MCP
        details = self.mcp_manager.get_mcp_details(name)
        if not details:
            messagebox.showerror("Erro", f"MCP '{name}' não encontrado")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Editar MCP: {name}")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Nome (somente leitura)
        ttk.Label(main_frame, text="Nome:").grid(row=0, column=0, sticky='w', pady=5)
        name_label = ttk.Label(main_frame, text=name)
        name_label.grid(row=0, column=1, pady=5, padx=(10, 0), sticky='w')
        
        # Comando
        ttk.Label(main_frame, text="Comando:").grid(row=1, column=0, sticky='w', pady=5)
        cmd_entry = ttk.Entry(main_frame, width=30)
        cmd_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        cmd_entry.insert(0, details.get('command', ''))
        
        # Argumentos
        ttk.Label(main_frame, text="Argumentos:").grid(row=2, column=0, sticky='w', pady=5)
        args_text = tk.Text(main_frame, width=30, height=5)
        args_text.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Preencher argumentos
        args = details.get('args', [])
        if args:
            args_text.insert("1.0", '\n'.join(args))
        
        # Frame para botões
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        def save_changes():
            command = cmd_entry.get().strip()
            args_text_content = args_text.get("1.0", tk.END).strip()
            
            if not command:
                messagebox.showerror("Erro", "Comando é obrigatório")
                return
            
            # Processar argumentos
            args = []
            if args_text_content:
                args = [arg.strip() for arg in args_text_content.split('\n') if arg.strip()]
            
            try:
                self.mcp_manager.update_mcp(name, command, args)
                self._refresh_mcp_list()
                dialog.destroy()
                messagebox.showinfo("Sucesso", "MCP atualizado com sucesso!")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao atualizar MCP:\n{e}")
        
        ttk.Button(button_frame, text="Salvar", command=save_changes).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancelar", command=dialog.destroy).pack(side='left', padx=5)
    
    def _remove_mcp(self, name):
        """
        Remove um MCP
        """
        if messagebox.askyesno("Confirmar", f"Deseja remover o MCP '{name}'?"):
            try:
                self.mcp_manager.remove_mcp(name)
                self._refresh_mcp_list()
                messagebox.showinfo("Sucesso", "MCP removido com sucesso!")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover MCP:\n{e}")
    
    def _install_template(self, template_name):
        """
        Instala um template
        """
        try:
            # Verificar dependências
            missing_deps = self.mcp_manager.get_missing_dependencies(template_name)
            if missing_deps:
                dep_list = ", ".join(missing_deps)
                if not messagebox.askyesno(
                    "Dependências Ausentes",
                    f"As seguintes dependências estão ausentes: {dep_list}\n\n"
                    "Deseja continuar com a instalação?"
                ):
                    return
            
            self.mcp_manager.install_from_template(template_name)
            self._refresh_mcp_list()
            self._refresh_templates_list()
            messagebox.showinfo("Sucesso", f"Template '{template_name}' instalado com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao instalar template:\n{e}")
    
    def _on_closing(self):
        """
        Manipulador para o evento de fechamento da janela
        """
        if self.pending_changes:
            if messagebox.askyesno(
                "Alterações Pendentes",
                "Há alterações pendentes nos MCPs. Deseja salvá-las antes de sair?"
            ):
                self._save_mcp_changes()
        
        self.root.destroy()
    
    def run(self):
        """
        Inicia o loop principal da interface gráfica
        """
        self.root.mainloop()


def main():
    """
    Função principal para executar a interface gráfica
    """
    try:
        app = MCPGUI()
        app.run()
    except Exception as e:
        logger.error(f"Erro ao executar a aplicação: {e}")
        messagebox.showerror("Erro Fatal", f"Erro ao executar a aplicação:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()