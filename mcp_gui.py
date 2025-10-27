#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Manager GUI
Interface gráfica para gerenciamento de MCPs
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import logging
import json
import sys
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageTk
from ttkthemes import ThemedTk

from src.core.mcp_manager import MCPManager, MCPManagerError
from src.core.config_manager import ConfigManager, ConfigManagerError

class MCPManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MCP Manager - Gerenciador de MCPs")
        self.root.geometry("1200x600")
        self.root.minsize(1200, 500)

        # Configurar estilo
        self.style = ttk.Style()
        self.style.theme_use('arc')
        self.style.configure("TButton", padding=6, relief="flat", font=('Helvetica', 10))
        self.style.configure("TLabel", padding=5, font=('Helvetica', 10))
        self.style.configure("TEntry", padding=5, font=('Helvetica', 10))
        self.style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))
        self.style.configure("TLabelFrame.Label", font=('Helvetica', 12, 'bold'))

        # Instanciar MCPManager
        try:
            self.config_manager = ConfigManager()
            self.manager = MCPManager()
            self.cli_type = tk.StringVar(value=self.config_manager.get_cli_type())
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível inicializar o MCP Manager: {str(e)}")
            root.destroy()
            return

        # Criar imagens para checkboxes
        self.create_checkbox_images()

        # Criar menu
        self.create_menu()

        self.setup_ui()
        self.load_mcps()

    def create_menu(self):
        """Cria o menu da aplicação."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Configurar caminho do usuário", command=self.configure_user_path)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)
        
        # Menu CLI
        cli_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="CLI", menu=cli_menu)
        cli_menu.add_radiobutton(label="Gemini", variable=self.cli_type, value="gemini", command=lambda: self.set_cli("gemini"))
        cli_menu.add_radiobutton(label="Qwen", variable=self.cli_type, value="qwen", command=lambda: self.set_cli("qwen"))

        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Sobre", command=self.show_about)

    def set_cli(self, cli_type: str):
        """Define o CLI a ser usado."""
        try:
            self.config_manager.set_cli_type(cli_type)
            self.manager.refresh_settings_path()
            self.load_mcps()
            self.update_status(f"CLI alterado para: {cli_type.capitalize()}")
            messagebox.showinfo("Sucesso", f"CLI alterado para {cli_type.capitalize()} com sucesso!")
        except (ConfigManagerError, MCPManagerError) as e:
            self.update_status(f"Erro ao alterar CLI: {str(e)}", error=True)
            messagebox.showerror("Erro", f"Não foi possível alterar o CLI: {str(e)}")

    def configure_user_path(self):
        """Abre diálogo para configurar o caminho do usuário."""
        try:
            # Solicitar diretório do usuário
            directory = filedialog.askdirectory(
                title="Selecione o diretório base do usuário",
                initialdir=str(Path.home())
            )
            
            if not directory:
                return  # Usuário cancelou
                
            # Configurar o caminho usando ConfigManager
            config_manager = ConfigManager()
            config_manager.set_user_path(directory)
            
            # Atualizar o MCPManager com o novo caminho
            self.manager.refresh_settings_path()
            
            # Recarregar a lista de MCPs
            self.load_mcps()
            
            self.update_status(f"Caminho do usuário configurado: {directory}")
            messagebox.showinfo("Sucesso", f"Caminho do usuário configurado com sucesso!\n\n{directory}")
            
        except ConfigManagerError as e:
            self.update_status(f"Erro ao configurar caminho: {str(e)}", error=True)
            messagebox.showerror("Erro", f"Não foi possível configurar o caminho:\n{str(e)}")
        except Exception as e:
            self.update_status(f"Erro inesperado: {str(e)}", error=True)
            messagebox.showerror("Erro", f"Erro inesperado ao configurar caminho:\n{str(e)}")

    def show_about(self):
        """Exibe informações sobre a aplicação."""
        about_text = """MCP Manager - Gerenciador de MCPs

Versão: 1.0.0

Uma ferramenta para gerenciar servidores MCP (Model Context Protocol)
no arquivo settings.json.

Para configurar o caminho do usuário, use:
Arquivo -> Configurar caminho do usuário

Ou execute o script setup_user_path.py manualmente."""
        messagebox.showinfo("Sobre", about_text)

    def create_checkbox_images(self):
        """Create checkbox images for checked and unchecked states."""
        try:
            # Criar imagem para checkbox desmarcado
            unchecked_img = Image.new('RGBA', (16, 16), (255, 255, 255, 0))
            draw = ImageDraw.Draw(unchecked_img)
            draw.rectangle([2, 2, 14, 14], outline='gray', width=2)
            self.unchecked_photo = ImageTk.PhotoImage(unchecked_img)

            # Criar imagem para checkbox marcado
            checked_img = Image.new('RGBA', (16, 16), (255, 255, 255, 0))
            draw = ImageDraw.Draw(checked_img)
            draw.rectangle([2, 2, 14, 14], outline='green', fill='lightgreen', width=2)
            # Desenhar o "check"
            draw.line([4, 8, 7, 11, 12, 5], fill='darkgreen', width=2)
            self.checked_photo = ImageTk.PhotoImage(checked_img)
        except ImportError:
            # Fallback para PIL não disponível - usar texto simples
            self.unchecked_photo = None
            self.checked_photo = None
        except Exception as e:
            logging.warning(f"Could not create checkbox images: {e}")
            self.unchecked_photo = None
            self.checked_photo = None

    def setup_ui(self):
        self.create_widgets()

    def create_widgets(self):
        # Container principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar peso do grid para responsividade
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)  # Column for MCPs
        main_frame.columnconfigure(1, weight=1)  # Column for templates
        main_frame.rowconfigure(0, weight=3)  # Lista de MCPs ocupa mais espaço
        # main_frame.rowconfigure(1, weight=2)  # Formulário ocupa menos espaço (removido)
        main_frame.rowconfigure(1, weight=0)  # Barra de status ocupa pouco espaço (ajustado de 2 para 1)

        # Criar frames
        self.create_mcp_list_frame(main_frame)
        # self.create_form_frame(main_frame)  # Formulário de adição de MCP removido
        self.create_templates_frame(main_frame)
        self.create_status_bar(main_frame)

    def create_mcp_list_frame(self, parent):
        # Frame da lista de MCPs
        list_frame = ttk.LabelFrame(parent, text="MCPs Instalados", padding="5")
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Treeview para lista de MCPs
        columns = ("Nome", "Command", "Args")
        self.mcp_tree = ttk.Treeview(list_frame, columns=columns, show="tree headings", height=10)

        # Configurar colunas
        self.mcp_tree.heading("#0", text="Status")
        self.mcp_tree.heading("Nome", text="Nome")
        self.mcp_tree.heading("Command", text="Command")
        self.mcp_tree.heading("Args", text="Args")

        self.mcp_tree.column("#0", width=40, minwidth=32, anchor='center')
        self.mcp_tree.column("Nome", width=150, minwidth=100)
        self.mcp_tree.column("Command", width=250, minwidth=150)
        self.mcp_tree.column("Args", width=250, minwidth=150)

        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.mcp_tree.yview)
        tree_scroll_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.mcp_tree.xview)
        self.mcp_tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

        # Grid dos widgets
        self.mcp_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        tree_scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Bind clique para alternar checkboxes no Status column
        self.mcp_tree.bind("<Button-1>", self.on_tree_click)
        # Manter binding duplo clique para compatibilidade
        self.mcp_tree.bind("<Double-1>", self.toggle_mcp_status)

        # Frame de botões
        button_frame = ttk.Frame(list_frame)
        button_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))

        ttk.Button(button_frame, text="Salvar", command=self.save_settings).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Atualizar Lista", command=self.load_mcps).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Remover Selecionado", command=self.remove_mcp).pack(side=tk.LEFT)

    def create_form_frame(self, parent):
        # Frame do formulário
        form_frame = ttk.LabelFrame(parent, text="Adicionar Novo MCP", padding="5")
        form_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        form_frame.columnconfigure(1, weight=1)
        form_frame.rowconfigure(2, weight=1)

        # Campo Nome
        ttk.Label(form_frame, text="Nome:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.name_entry = ttk.Entry(form_frame, width=40)
        self.name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))

        # Campo Command
        ttk.Label(form_frame, text="Command:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.command_entry = ttk.Entry(form_frame, width=40)
        self.command_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))

        # Campo Args
        ttk.Label(form_frame, text="Args:").grid(row=2, column=0, sticky=(tk.N, tk.W), pady=(0, 5))
        args_container = ttk.Frame(form_frame)
        args_container.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        args_container.columnconfigure(0, weight=1)
        args_container.rowconfigure(0, weight=1)

        self.args_text = scrolledtext.ScrolledText(args_container, height=4, width=40)
        self.args_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Label de ajuda
        help_label = ttk.Label(form_frame, text="Digite um argumento por linha", font=("TkDefaultFont", 8))
        help_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        # Frame de botões
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))

        ttk.Button(button_frame, text="Adicionar MCP", command=self.add_mcp).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Limpar Formulário", command=self.clear_form).pack(side=tk.LEFT)

    def create_status_bar(self, parent):
        # Barra de status
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(0, weight=1)

        self.status_label = ttk.Label(status_frame, text="Pronto", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))

    def create_templates_frame(self, parent):
        # Frame de templates
        templates_frame = ttk.LabelFrame(parent, text="Templates de MCPs", padding="5")
        templates_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        templates_frame.columnconfigure(0, weight=1)
        templates_frame.rowconfigure(0, weight=1)

        # Listbox para os templates
        self.templates_listbox = tk.Listbox(templates_frame, height=10, font=('Helvetica', 10))
        self.templates_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.templates_listbox.bind('<<ListboxSelect>>', self.show_template_details)

        # Scrollbar para a Listbox
        templates_scrollbar = ttk.Scrollbar(templates_frame, orient=tk.VERTICAL, command=self.templates_listbox.yview)
        self.templates_listbox.config(yscrollcommand=templates_scrollbar.set)
        templates_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Frame de detalhes do template
        details_frame = ttk.LabelFrame(templates_frame, text="Detalhes do Template", padding="5")
        details_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        details_frame.columnconfigure(0, weight=1)

        self.template_details_label = ttk.Label(details_frame, text="Selecione um template para ver os detalhes", wraplength=300)
        self.template_details_label.pack(fill=tk.X, expand=True)

        # Botão de instalação
        install_button = ttk.Button(templates_frame, text="Instalar Template", command=self.install_selected_template)
        install_button.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        self.populate_templates_list()

    def populate_templates_list(self):
        self.templates_listbox.delete(0, tk.END)
        templates = self.manager.get_templates()
        for name in sorted(templates):
            self.templates_listbox.insert(tk.END, name)

    def show_template_details(self, event):
        selection = self.templates_listbox.curselection()
        if not selection:
            return

        template_name = self.templates_listbox.get(selection[0])
        templates = self.manager.get_templates()
        template_data = templates.get(template_name)

        if template_data:
            details_text = f"Nome: {template_data['name']}\n\n"
            details_text += f"Descrição: {template_data['description']}\n\n"
            details_text += f"Comando: {template_data['command']}\n\n"
            details_text += f"Argumentos: {', '.join(template_data['args'])}"
            self.template_details_label.config(text=details_text)
        else:
            self.template_details_label.config(text="Detalhes não encontrados.")

    def install_selected_template(self):
        selection = self.templates_listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um template para instalar.")
            return

        template_name = self.templates_listbox.get(selection[0])
        self.install_template(template_name)

    def install_template(self, template_name: str, enable: bool = True):
        """Install an MCP from template."""
        try:
            # Verificar se já está instalado
            if self.manager.is_template_installed(template_name):
                messagebox.showinfo("Informação", f"MCP '{template_name}' já está instalado!")
                return

            # Instalar a partir do template, sempre habilitando
            self.manager.install_from_template(template_name, enable=True)

            # Mostrar mensagem de sucesso
            action = "e ativado" if enable else "do"
            messagebox.showinfo("Sucesso", f"MCP '{template_name}' foi instalado {action} com sucesso!")

            # Recarregar lista de MCPs
            self.load_mcps()

            self.update_status(f"Template '{template_name}' instalado com sucesso!")

        except MCPManagerError as e:
            self.update_status(f"Erro ao instalar template: {str(e)}", error=True)
            messagebox.showerror("Erro", f"Não foi possível instalar o template: {str(e)}")
        except Exception as e:
            self.update_status(f"Erro inesperado: {str(e)}", error=True)
            messagebox.showerror("Erro", f"Erro inesperado ao instalar template: {str(e)}")



    def load_mcps(self):
        try:
            # Limpar treeview
            for item in self.mcp_tree.get_children():
                self.mcp_tree.delete(item)

            # Obter MCPs do manager
            mcps = self.manager.get_mcps()

            # Popular treeview
            for name in sorted(mcps):
                data = mcps[name]
                command = data.get('command', '')
                args = ', '.join(data.get('args', []))
                enabled = data.get('enabled', False)

                # Inserir item no treeview com checkbox na coluna #0
                item = self.mcp_tree.insert('', tk.END, text='',
                    image=(self.checked_photo if enabled else self.unchecked_photo),
                    values=(name, command, args))

            self.update_status(f"Carregados {len(mcps)} MCPs")

        except MCPManagerError as e:
            self.update_status(f"Erro ao carregar MCPs: {str(e)}", error=True)
            messagebox.showerror("Erro", f"Não foi possível carregar os MCPs: {str(e)}")
        except Exception as e:
            self.update_status(f"Erro inesperado: {str(e)}", error=True)
            messagebox.showerror("Erro", f"Erro inesperado ao carregar MCPs: {str(e)}")

    def set_item_checkbox(self, item, enabled):
        """Set checkbox image for an item in the treeview."""
        if enabled and self.checked_photo:
            self.mcp_tree.item(item, image=self.checked_photo)
        elif not enabled and self.unchecked_photo:
            self.mcp_tree.item(item, image=self.unchecked_photo)
        else:
            # Fallback para texto se imagens não disponíveis - define texto na coluna #0
            status_text = "✓" if enabled else "✗"
            self.mcp_tree.item(item, text=status_text, image=None)

    def on_tree_click(self, event):
        """Handle click events on the treeview."""
        try:
            # Identificar a coluna clicada
            column = self.mcp_tree.identify_column(event.x)
            if column != "#0":  # Status column (tree column)
                return

            # Identificar a linha clicada
            row = self.mcp_tree.identify_row(event.y)
            if not row:
                return

            # Obter valores do item
            values = self.mcp_tree.item(row, 'values')
            if not values:
                return

            name = values[0]

            # Obter estado atual
            mcps = self.manager.get_mcps()
            enabled = mcps.get(name, {}).get('enabled', False)

            # Alternar status usando toggle_allowed
            self.manager.toggle_allowed(name, not enabled)

            # Atualizar apenas esta linha
            self.set_item_checkbox(row, not enabled)

            self.update_status(f"Status do MCP '{name}' alterado com sucesso")

        except MCPManagerError as e:
            self.update_status(f"Erro ao alterar status: {str(e)}", error=True)
            messagebox.showerror("Erro", f"Não foi possível alterar o status: {str(e)}")
        except Exception as e:
            self.update_status(f"Erro inesperado: {str(e)}", error=True)
            messagebox.showerror("Erro", f"Erro inesperado ao alterar status: {str(e)}")

    def toggle_mcp_status(self, event):
        """Handle double-click events for backward compatibility."""
        try:
            # Obter item clicado usando identify_row
            row = self.mcp_tree.identify_row(event.y)
            column = self.mcp_tree.identify_column(event.x)

            if not row or column != "#0":  # Apenas na coluna Status (tree column)
                return

            values = self.mcp_tree.item(row, 'values')
            if not values:
                return

            name = values[0]

            # Alternar status
            self.manager.toggle_allowed(name)

            # Recarregar lista
            self.load_mcps()

            self.update_status(f"Status do MCP '{name}' alterado com sucesso")

        except MCPManagerError as e:
            self.update_status(f"Erro ao alterar status: {str(e)}", error=True)
            messagebox.showerror("Erro", f"Não foi possível alterar o status: {str(e)}")
        except Exception as e:
            self.update_status(f"Erro inesperado: {str(e)}", error=True)
            messagebox.showerror("Erro", f"Erro inesperado ao alterar status: {str(e)}")

    def add_mcp(self):
        try:
            # Validar campos
            name = self.name_entry.get().strip()
            command = self.command_entry.get().strip()
            args_text = self.args_text.get("1.0", tk.END).strip()

            if not name:
                messagebox.showerror("Erro", "O campo 'Nome' é obrigatório")
                return

            if not command:
                messagebox.showerror("Erro", "O campo 'Command' é obrigatório")
                return

            # Processar args
            args = [arg.strip() for arg in args_text.split('\n') if arg.strip()]

            # Adicionar MCP
            self.manager.add_mcp(name, command, args)

            # Limpar formulário
            self.clear_form()

            # Recarregar lista
            self.load_mcps()

            messagebox.showinfo("Sucesso", f"MCP '{name}' adicionado com sucesso!")

        except MCPManagerError as e:
            self.update_status(f"Erro ao adicionar MCP: {str(e)}", error=True)
            messagebox.showerror("Erro", f"Não foi possível adicionar o MCP: {str(e)}")
        except Exception as e:
            self.update_status(f"Erro inesperado: {str(e)}", error=True)
            messagebox.showerror("Erro", f"Erro inesperado ao adicionar MCP: {str(e)}")

    def remove_mcp(self):
        try:
            # Obter item selecionado
            selection = self.mcp_tree.selection()
            if not selection:
                messagebox.showwarning("Aviso", "Selecione um MCP para remover")
                return

            item = selection[0]
            values = self.mcp_tree.item(item, 'values')
            name = values[0]

            # Confirmar remoção
            if not messagebox.askyesno("Confirmar", f"Tem certeza que deseja remover o MCP '{name}'?"):
                return

            # Remover MCP
            self.manager.remove_mcp(name)

            # Recarregar lista
            self.load_mcps()

            messagebox.showinfo("Sucesso", f"MCP '{name}' removido com sucesso!")

        except MCPManagerError as e:
            self.update_status(f"Erro ao remover MCP: {str(e)}", error=True)
            messagebox.showerror("Erro", f"Não foi possível remover o MCP: {str(e)}")
        except Exception as e:
            self.update_status(f"Erro inesperado: {str(e)}", error=True)
            messagebox.showerror("Erro", f"Erro inesperado ao remover MCP: {str(e)}")

    def save_settings(self):
        """Save current settings using MCPManager.save_settings()."""
        try:
            # Força o MCPManager a salvar o estado atual
            # Como as alterações são salvas imediatamente nas operações individuais,
            # este método serve como confirmação explícita do usuário
            settings = self.manager.load_settings()
            self.manager.save_settings(settings)

            self.update_status("Configurações salvas com sucesso!")
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")

        except MCPManagerError as e:
            self.update_status(f"Erro ao salvar configurações: {str(e)}", error=True)
            messagebox.showerror("Erro", f"Não foi possível salvar as configurações: {str(e)}")
        except Exception as e:
            self.update_status(f"Erro inesperado ao salvar: {str(e)}", error=True)
            messagebox.showerror("Erro", f"Erro inesperado ao salvar: {str(e)}")

    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.command_entry.delete(0, tk.END)
        self.args_text.delete("1.0", tk.END)
        self.name_entry.focus()

    def update_status(self, message, error=False):
        self.status_label.config(text=message, foreground="red" if error else "green")


def main():
    # Configurar logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Criar janela principal com tema
    root = ThemedTk(theme="arc")

    try:
        # Criar aplicação
        app = MCPManagerGUI(root)

        # Iniciar loop principal
        root.mainloop()

    except Exception as e:
        logging.error(f"Erro ao iniciar aplicação: {str(e)}")
        messagebox.showerror("Erro Fatal", f"Não foi possível iniciar a aplicação: {str(e)}")


if __name__ == "__main__":
    main()

