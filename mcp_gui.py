#!/usr/bin/env python3
if False:
    def _make_scrollable_list(self, container):
        """
        Cria um frame rolável (Canvas + Scrollbar + Frame interno)
        e retorna (canvas, scrollbar, inner_frame).
        """
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        inner_frame = ttk.Frame(canvas)

        inner_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return canvas, scrollbar, inner_frame
# -*- coding: utf-8 -*-
"""
Interface GrÃ¡fica para Gerenciamento de Servidores MCP (Model Context Protocol)

Este mÃ³dulo fornece uma interface grÃ¡fica usando Tkinter para gerenciar
servidores MCP, permitindo selecionar o CLI (Gemini/Qwen) e configurar
os servidores disponÃ­veis.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import logging
import sys
import os
from pathlib import Path

# DependÃªncias de tema opcionais: sv_ttk e darkdetect
try:
    import sv_ttk
    HAS_SVTTK = True
except ImportError:
    sv_ttk = None  # type: ignore
    HAS_SVTTK = False

try:
    import darkdetect
    HAS_DARKDETECT = True
except ImportError:
    darkdetect = None  # type: ignore
    HAS_DARKDETECT = False

# Adicionar o diretÃ³rio src ao path para importar os mÃ³dulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.config_manager import ConfigManager, ConfigManagerError
from src.core.mcp_manager import MCPManager, MCPManagerError

# ConfiguraÃ§Ã£o de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCPGUI:
    """
    Classe principal da Interface GrÃ¡fica do MCP Manager
    """
    
    def __init__(self):
        """
        Inicializa a interface grÃ¡fica com tratamento de erro para o tema 'arc'
        """
        self.root = None
        self.style = None
        self.config_manager = None
        self.mcp_manager = None
        self.mcp_vars = {}
        self.pending_changes = False
        self.temperature_var = None
        self.temperature_frame = None
        self.theming_available = False
        
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
        Inicializa a janela principal, detecta o tema do sistema (claro/escuro)
        e aplica o tema correspondente usando sv-ttk quando disponÃ­vel.
        """
        self.root = tk.Tk()
        self.current_theme = "light"  # PadrÃ£o
        if HAS_SVTTK:
            self.theming_available = True
            try:
                chosen = "light"
                if HAS_DARKDETECT:
                    try:
                        theme = darkdetect.theme()
                        if theme and str(theme).lower() == "dark":
                            chosen = "dark"
                    except Exception:
                        # Se darkdetect falhar, permanece "light"
                        chosen = "light"
                sv_ttk.set_theme(chosen)  # type: ignore[attr-defined]
                self.current_theme = chosen
                logger.info(f"Tema {chosen} aplicado via sv_ttk.")
            except Exception as e:
                logger.warning(f"Falha ao aplicar tema via sv_ttk: {e}. Usando tema padrÃ£o do Tkinter.")
                # Fallback para o tema padrÃ£o do Tkinter
                self.theming_available = False
                self.style = ttk.Style()
                try:
                    available_themes = self.style.theme_names()
                    if "clam" in available_themes:
                        self.style.theme_use("clam")
                    else:
                        self.style.theme_use("default")
                except tk.TclError:
                    self.style.theme_use("default")
        else:
            # Sem sv_ttk: usar temas nativos do ttk
            self.theming_available = False
            self.style = ttk.Style()
            try:
                available_themes = self.style.theme_names()
                if "clam" in available_themes:
                    self.style.theme_use("clam")
                else:
                    self.style.theme_use("default")
            except tk.TclError:
                self.style.theme_use("default")

        # Configurar propriedades bÃ¡sicas da janela
        self.root.title("MCP Manager - Gerenciador de Servidores MCP")
        self.root.geometry("800x650")  # Aumentar a altura para melhor espaÃ§amento
        self.root.minsize(700, 500)

        # Configurar o fechamento da janela
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _init_managers(self):
        """
        Inicializa os gerenciadores de configuraÃ§Ã£o e MCP
        """
        try:
            self.config_manager = ConfigManager()
            self.mcp_manager = MCPManager(config_manager=self.config_manager)
            logger.info("Gerenciadores inicializados com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar gerenciadores: {e}")
            messagebox.showerror(
                "Erro de InicializaÃ§Ã£o",
                f"NÃ£o foi possÃ­vel inicializar os gerenciadores:\n{e}"
            )
            sys.exit(1)
    
    def _setup_ui(self):
        """
        Configura os componentes da interface Gráfica
        """
        # Criar a barra de menu
        menubar = tk.Menu(self.root)
        view_menu = tk.Menu(menubar, tearoff=0)
        if self.theming_available:
            view_menu.add_command(label="Alternar Tema (Claro/Escuro)", command=self._toggle_theme)
        else:
            # Desabilita ou omite quando theming nÃ£o estÃ¡ disponÃ­vel
            view_menu.add_command(label="Alternar Tema (Claro/Escuro)", state='disabled')
        menubar.add_cascade(label="Exibir", menu=view_menu)
        self.root.config(menu=menubar)

        # Criar o notebook para abas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Aba de configurações
        self._setup_config_tab()
        
        # Aba de Servidores MCP
        self._setup_mcp_tab()
        
        # Aba de Templates
        self._setup_templates_tab()
        
        # Barra de status
        self._setup_status_bar()

    def _toggle_theme(self):
        """
        Alterna entre os temas claro e escuro.
        """
        if not self.theming_available:
            if hasattr(self, "status_label") and self.status_label:
                self.status_label.config(text="AlternÃ¢ncia de tema indisponÃ­vel (sv_ttk ausente).")
            return
        try:
            if self.current_theme == "dark":
                sv_ttk.set_theme("light")  # type: ignore[attr-defined]
                self.current_theme = "light"
                self.status_label.config(text="Tema alterado para claro")
            else:
                sv_ttk.set_theme("dark")  # type: ignore[attr-defined]
                self.current_theme = "dark"
                self.status_label.config(text="Tema alterado para escuro")
            logger.info(f"Tema alterado manualmente para {self.current_theme}")
        except Exception as e:
            logger.error(f"Erro ao alternar tema: {e}")
            messagebox.showerror("Erro de Tema", f"NÃ£o foi possÃ­vel alterar o tema:\n{e}")
    
    def _setup_config_tab(self):
        """
        Configura a aba de configurações do CLI
        """
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="Configurações")

        # Frame principal com mais espaçamento
        main_frame = ttk.Frame(config_frame, padding="30")
        main_frame.pack(fill='both', expand=True)

        # Título
        title_label = ttk.Label(
            main_frame,
            text="Configuração do CLI",
            font=('TkDefaultFont', 16, 'bold') # Fonte maior
        )
        title_label.pack(pady=(0, 25))

        # Frame para seleção do CLI
        cli_frame = ttk.LabelFrame(main_frame, text="Selecionar CLI", padding="15")
        cli_frame.pack(fill='x', pady=(0, 25))

        # Variável para o tipo de CLI
        self.cli_var = tk.StringVar()

        # Radio buttons para seleção do CLI
        ttk.Radiobutton(
            cli_frame,
            text="Gemini",
            variable=self.cli_var,
            value="gemini",
            command=self._on_cli_change
        ).pack(anchor='w', pady=8)
        
        ttk.Radiobutton(
            cli_frame,
            text="Qwen",
            variable=self.cli_var,
            value="qwen",
            command=self._on_cli_change
        ).pack(anchor='w', pady=8)

        # Frame para caminho do usuário
        path_frame = ttk.LabelFrame(main_frame, text="Caminho do Usuário", padding="15")
        path_frame.pack(fill='x', pady=(0, 25))
        
        # Label para mostrar o caminho atual
        self.path_label = ttk.Label(path_frame, text="Carregando...")
        self.path_label.pack(anchor='w', pady=8)
        
        # BotÃ£o para alterar o caminho
        ttk.Button(
            path_frame,
            text="Alterar Caminho",
            command=self._change_user_path
        ).pack(pady=8)

        # Frame para configurações do modelo (Gemini e Qwen)
        self.temperature_frame = ttk.LabelFrame(main_frame, text="Configurações do Modelo", padding="15")
        self.temperature_frame.pack(fill='x', pady=(0, 25))

        # Variável e controle deslizante de temperatura (0.0 a 2.0)
        self.temperature_var = tk.DoubleVar()
        temp_desc_label = ttk.Label(
            self.temperature_frame,
            text="Ajuste a temperatura do modelo (0.0 = mais determinístico, 2.0 = mais criativo)",
            font=('TkDefaultFont', 9),
            foreground='gray'
        )
        temp_desc_label.pack(anchor='w', padx=(0, 0), pady=(0, 8))
        self.temperature_scale = ttk.Scale(
            self.temperature_frame,
            from_=0.0,
            to=2.0,
            orient='horizontal',
            length=300,
            variable=self.temperature_var,
            command=self._on_temperature_change
        )
        self.temperature_scale.pack(anchor='w', pady=8)
        # Persistir somente ao soltar o mouse
        self.temperature_scale.bind('<ButtonRelease-1>', lambda e: self._on_temperature_commit())
        self.temperature_value_label = ttk.Label(self.temperature_frame, text="Valor atual: -")
        self.temperature_value_label.pack(anchor='w', padx=(0, 0), pady=(0, 8))

        # Botão para salvar configurações
        ttk.Button(
            main_frame,
            text="Salvar Configurações",
            command=self._save_config
        ).pack(pady=15)
    
    def _make_scrollable_list(self, container):
        """
        Cria um frame rolável (Canvas + Scrollbar + Frame interno)
        e retorna (canvas, scrollbar, inner_frame).
        """
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        inner_frame = ttk.Frame(canvas)
        inner_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return canvas, scrollbar, inner_frame

    def _setup_mcp_tab(self):
        """
        Configura a aba de gerenciamento de servidores MCP
        """
        mcp_frame = ttk.Frame(self.notebook)
        self.notebook.add(mcp_frame, text="Servidores MCP")
        
        # Frame principal com mais espaÃ§amento
        main_frame = ttk.Frame(mcp_frame, padding="30")
        main_frame.pack(fill='both', expand=True)
        
        # TÃ­tulo
        title_label = ttk.Label(
            main_frame,
            text="Servidores MCP Configurados",
            font=('TkDefaultFont', 16, 'bold')
        )
        title_label.pack(pady=(0, 25))
        
        # Frame para lista de MCPs
        list_frame = ttk.LabelFrame(main_frame, text="Servidores", padding="15")
        list_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Scrollable frame para a lista de MCPs
        canvas, scrollbar, inner_frame = self._make_scrollable_list(list_frame)
        self.mcp_list_frame = inner_frame
        
        # Frame para botÃµes
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=15)
        
        ttk.Button(
            button_frame,
            text="Adicionar MCP",
            command=self._add_mcp_dialog
        ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame,
            text="Salvar AlteraÃ§Ãµes",
            command=self._save_mcp_changes
        ).pack(side='left', padx=5)
        
        # Label para mostrar status das alteraÃ§Ãµes
        self.changes_label = ttk.Label(button_frame, text="")
        self.changes_label.pack(side='left', padx=20)
    
    def _setup_templates_tab(self):
        """
        Configura a aba de templates de MCP
        """
        templates_frame = ttk.Frame(self.notebook)
        self.notebook.add(templates_frame, text="Templates")
        
        # Frame principal com mais espaÃ§amento
        main_frame = ttk.Frame(templates_frame, padding="30")
        main_frame.pack(fill='both', expand=True)
        
        # TÃ­tulo
        title_label = ttk.Label(
            main_frame,
            text="Templates DisponÃ­veis",
            font=('TkDefaultFont', 16, 'bold')
        )
        title_label.pack(pady=(0, 25))
        
        # Frame para lista de templates
        list_frame = ttk.LabelFrame(main_frame, text="Templates", padding="15")
        list_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Scrollable frame para a lista de templates
        canvas, scrollbar, inner_frame = self._make_scrollable_list(list_frame)
        self.templates_list_frame = inner_frame
    
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
            # Carregar configurações do CLI
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

            # Carregar configuração de temperatura e atualizar UI
            self._update_temperature_visibility()
            self._load_temperature_state()

            self.status_label.config(text="Dados carregados com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados iniciais: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar dados:\n{e}")
    
    def _refresh_mcp_list(self):
        """
        Atualiza a lista de MCPs na interface usando um layout de grid.
        """
        # Limpar widgets existentes
        for widget in self.mcp_list_frame.winfo_children():
            widget.destroy()
        
        self.mcp_vars.clear()
        
        # Configurar o grid para expandir a coluna do meio
        self.mcp_list_frame.grid_columnconfigure(1, weight=1)

        try:
            mcps = self.mcp_manager.get_mcps()
            
            if not mcps:
                ttk.Label(
                    self.mcp_list_frame,
                    text="Nenhum servidor MCP configurado"
                ).grid(row=0, column=0, pady=20, padx=10)
                return
            
            for i, (name, details) in enumerate(mcps.items()):
                var = tk.BooleanVar(value=details.get('enabled', False))
                self.mcp_vars[name] = var
                
                # Checkbox para habilitar/desabilitar
                cb = ttk.Checkbutton(
                    self.mcp_list_frame,
                    text=name,
                    variable=var,
                    command=self._on_mcp_toggle
                )
                cb.grid(row=i, column=0, sticky='w', padx=(5, 10), pady=8)
                
                # Label com detalhes do comando
                cmd_text = f"Comando: {details.get('command', '')}"
                cmd_label = ttk.Label(self.mcp_list_frame, text=cmd_text, font=('TkDefaultFont', 9))
                cmd_label.grid(row=i, column=1, sticky='w', padx=(0, 10))
                
                # BotÃ£o para editar
                edit_button = ttk.Button(
                    self.mcp_list_frame,
                    text="Editar",
                    command=lambda n=name: self._edit_mcp(n)
                )
                edit_button.grid(row=i, column=2, sticky='e', padx=5)

                # BotÃ£o para remover
                remove_button = ttk.Button(
                    self.mcp_list_frame,
                    text="Remover",
                    command=lambda n=name: self._remove_mcp(n)
                )
                remove_button.grid(row=i, column=3, sticky='e', padx=(0, 5))
        
        except Exception as e:
            logger.error(f"Erro ao atualizar lista de MCPs: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar MCPs:\n{e}")
    
    def _refresh_templates_list(self):
        """
        Atualiza a lista de templates na interface com um design de cards.
        """
        # Limpar widgets existentes
        for widget in self.templates_list_frame.winfo_children():
            widget.destroy()
        
        # Configurar a coluna do grid para expandir
        self.templates_list_frame.grid_columnconfigure(0, weight=1)

        try:
            templates = self.mcp_manager.get_templates()
            
            if not templates:
                ttk.Label(
                    self.templates_list_frame,
                    text="Nenhum template disponÃ­vel"
                ).pack(pady=20)
                return
            
            for i, (name, template) in enumerate(templates.items()):
                # Frame do card
                card_frame = ttk.Frame(self.templates_list_frame, relief='solid', borderwidth=1, padding=15)
                card_frame.pack(fill='x', pady=10, padx=5)

                card_frame.grid_columnconfigure(0, weight=1)

                # Nome do template
                name_label = ttk.Label(card_frame, text=name, font=('TkDefaultFont', 12, 'bold'))
                name_label.grid(row=0, column=0, sticky='w', pady=(0, 10))
                
                # DescriÃ§Ã£o
                desc_label = ttk.Label(card_frame, text=template.get('description', ''), wraplength=500, justify="left")
                desc_label.grid(row=1, column=0, sticky='w', padx=(10, 0), pady=(0, 5))
                
                # Comando
                cmd_label = ttk.Label(card_frame, text=f"Comando: {template.get('command', '')}", font=('TkDefaultFont', 9, 'italic'))
                cmd_label.grid(row=2, column=0, sticky='w', padx=(10, 0), pady=(0, 10))
                
                # BotÃ£o de Instalar ou Label de Status
                if self.mcp_manager.is_template_installed(name):
                    status_label = ttk.Label(card_frame, text="âœ“ Instalado", foreground='green', font=('TkDefaultFont', 10, 'bold'))
                    status_label.grid(row=3, column=0, sticky='w', padx=(10, 0), pady=(10, 0))
                else:
                    install_button = ttk.Button(
                        card_frame,
                        text="Instalar",
                        command=lambda n=name: self._install_template(n)
                    )
                    install_button.grid(row=3, column=0, sticky='w', padx=(10, 0), pady=(10, 0))
        
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

            # Após persistir, então chamar refresh_settings_path(), _refresh_mcp_list() e _refresh_templates_list()
            self.mcp_manager.refresh_settings_path()
            self._refresh_mcp_list()
            self._refresh_templates_list()

            # Atualizar visibilidade do checkbox de temperatura
            self._update_temperature_visibility()

            self.status_label.config(text=f"CLI alterado para {self.cli_var.get()}")
        except ConfigManagerError as e:
            logger.error(f"Erro ao persistir tipo de CLI: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar tipo de CLI:\n{e}")
            # Reverter a seleÃ§Ã£o na interface em caso de erro
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
            self._refresh_templates_list()

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
                self._refresh_templates_list()

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
        dialog.geometry("450x350")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(dialog, padding="25")
        main_frame.pack(fill='both', expand=True)
        
        # Nome
        ttk.Label(main_frame, text="Nome:").grid(row=0, column=0, sticky='w', pady=8)
        name_entry = ttk.Entry(main_frame, width=35)
        name_entry.grid(row=0, column=1, pady=8, padx=(10, 0))
        
        # Comando
        ttk.Label(main_frame, text="Comando:").grid(row=1, column=0, sticky='w', pady=8)
        cmd_entry = ttk.Entry(main_frame, width=35)
        cmd_entry.grid(row=1, column=1, pady=8, padx=(10, 0))
        
        # Argumentos
        ttk.Label(main_frame, text="Argumentos:").grid(row=2, column=0, sticky='w', pady=8)
        args_text = tk.Text(main_frame, width=35, height=5)
        args_text.grid(row=2, column=1, pady=8, padx=(10, 0))
        
        # Frame para botÃµes
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=25)
        
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
        Abre diÃ¡logo para editar um MCP existente
        """
        # Obter detalhes do MCP
        details = self.mcp_manager.get_mcp_details(name)
        if not details:
            messagebox.showerror("Erro", f"MCP '{name}' nÃ£o encontrado")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Editar MCP: {name}")
        dialog.geometry("450x350")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(dialog, padding="25")
        main_frame.pack(fill='both', expand=True)
        
        # Nome (somente leitura)
        ttk.Label(main_frame, text="Nome:").grid(row=0, column=0, sticky='w', pady=8)
        name_label = ttk.Label(main_frame, text=name)
        name_label.grid(row=0, column=1, pady=8, padx=(10, 0), sticky='w')
        
        # Comando
        ttk.Label(main_frame, text="Comando:").grid(row=1, column=0, sticky='w', pady=8)
        cmd_entry = ttk.Entry(main_frame, width=35)
        cmd_entry.grid(row=1, column=1, pady=8, padx=(10, 0))
        cmd_entry.insert(0, details.get('command', ''))
        
        # Argumentos
        ttk.Label(main_frame, text="Argumentos:").grid(row=2, column=0, sticky='w', pady=8)
        args_text = tk.Text(main_frame, width=35, height=5)
        args_text.grid(row=2, column=1, pady=8, padx=(10, 0))
        
        # Preencher argumentos
        args = details.get('args', [])
        if args:
            args_text.insert("1.0", '\n'.join(args))
        
        # Frame para botÃµes
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=25)
        
        def save_changes():
            command = cmd_entry.get().strip()
            args_text_content = args_text.get("1.0", tk.END).strip()
            
            if not command:
                messagebox.showerror("Erro", "Comando Ã© obrigatÃ³rio")
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

    def _update_temperature_visibility(self):
        """
        Atualiza a visibilidade do checkbox de temperature baseado no CLI selecionado
        """
        try:
            cli_type = self.config_manager.get_cli_type()

            if self.temperature_frame is not None:
                if cli_type in ["gemini", "qwen"]:
                    # Mostrar para Gemini e Qwen
                    self.temperature_frame.pack(fill='x', pady=(0, 20))
                    self._load_temperature_state()
                else:
                    # Esconder para outros CLIs
                    self.temperature_frame.pack_forget()
        except Exception as e:
            logger.error(f"Erro ao atualizar visibilidade do temperature: {e}")

    def _load_temperature_state(self):
        """
        Carrega o valor atual da temperatura e atualiza o slider e o label
        """
        try:
            cli_type = self.config_manager.get_cli_type()
            if self.temperature_var is not None and cli_type in ["gemini", "qwen"]:
                temperature_value = self.mcp_manager.get_temperature()
                self.temperature_var.set(temperature_value)
                if hasattr(self, "temperature_value_label") and self.temperature_value_label:
                    self.temperature_value_label.config(text=f"Valor atual: {temperature_value:.1f}")
        except Exception as e:
            logger.error(f"Erro ao carregar estado do temperature: {e}")

    def _on_temperature_change(self, value=None):
        """
        Atualiza apenas o label com o valor atual durante o arraste do slider
        """
        try:
            cli_type = self.config_manager.get_cli_type()
            if cli_type not in ["gemini", "qwen"]:
                return

            current_value = self.temperature_var.get()
            temp_rounded = round(float(current_value), 1)
            if hasattr(self, "temperature_value_label") and self.temperature_value_label:
                self.temperature_value_label.config(text=f"Valor atual: {temp_rounded:.1f}")
        except Exception as e:
            logger.error(f"Erro ao alterar temperature: {e}")

    def _on_temperature_commit(self):
        """
        Persiste o valor ao soltar o mouse no slider
        """
        try:
            cli_type = self.config_manager.get_cli_type()
            if cli_type not in ["gemini", "qwen"]:
                return

            current_value = self.temperature_var.get()
            temp_rounded = round(float(current_value), 1)
            self.mcp_manager.set_temperature(temp_rounded)
            if hasattr(self, "status_label") and self.status_label:
                self.status_label.config(text=f"Temperature definida para {temp_rounded:.1f}")
        except Exception as e:
            logger.error(f"Erro ao alterar temperature: {e}")
            messagebox.showerror("Erro", f"Erro ao alterar temperature:\n{e}")
            try:
                self._load_temperature_state()
            except:
                pass

    def run(self):
        """
        Inicia o loop principal da interface grÃ¡fica
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
