# InstalarMCP

## 🚀 Overview
InstalarMCP é uma ferramenta Python que permite gerenciar servidores MCP (Model Context Protocol) usando a linha de comando. Este projeto oferece uma interface gráfica com Tkinter para facilitar a seleção do CLI (Gemini/Qwen) e a configuração dos servidores disponíveis. Ele também inclui scripts auxiliares e exemplos de uso para facilitar a integração e o desenvolvimento.

## ✨ Features
- **Interface Gráfica**: Utiliza Tkinter para fornecer uma interface amigável para gerenciar servidores MCP.
- **Configuração de Caminho do Usuário**: Permite configurar o caminho base do usuário e o CLI preferido.
- **Validação de Dependências**: Verifica e instala dependências ausentes antes de executar a aplicação.
- **Scripts Auxiliares**: Inclui scripts para criar diretórios, configurar caminhos e instalar dependências.
- **Exemplos de Uso**: Fornece exemplos de integração com o ConfigManager e MCPManager.

## 🛠️ Tech Stack
- **Programming Language**: Python
- **Frameworks**: Tkinter, SpecKitManager (Windows)
- **Libraries**: sv-ttk, darkdetect
- **System Requirements**: Python 3.x, Tkinter

## 📦 Installation

### Prerequisites
- Python 3.x
- Tkinter (normalmente incluído com Python)

### Quick Start
```bash
# Clone o repositório
git clone https://github.com/seu-usuario/InstalarMCP.git

# Navegue até o diretório do projeto
cd InstalarMCP

# Instale as dependências
pip install -r requirements.txt

# Configure o caminho base do usuário
python scripts/setup_user_path.py

# Execute a aplicação
python mcp_gui.py
```

### Alternative Installation Methods
- **Docker**: Utilize o Dockerfile fornecido para criar uma imagem Docker do projeto.
- **Development Setup**: Siga as instruções de desenvolvimento para configurar o ambiente de desenvolvimento.

## 🎯 Usage

### Basic Usage
```python
# Exemplo básico de uso do ConfigManager
from src.core.config_manager import ConfigManager, ConfigManagerError

config = ConfigManager()
try:
    config.set_user_path("C:/Users/SEU_USUARIO")
except ConfigManagerError as err:
    print(f"Erro ao configurar caminho: {err}")
else:
    print(f"Caminho salvo em: {config.get_user_path()}")
```

### Advanced Usage
- **Integração com MCPManager**: Utilize o MCPManager para gerenciar servidores MCP.
- **Configuração de Caminho do Usuário**: Configure o caminho base do usuário e o CLI preferido.
- **Validação de Dependências**: Verifique e instale dependências ausentes antes de executar a aplicação.

## 📁 Project Structure
```
├── mcp_gui.py                  # Interface gráfica principal
├── README.md                   # Este arquivo
├── CLI.md                      # Documentação da CLI
├── requirements.txt            # Dependências do projeto
├── instalar.py                 # Script de instalação (Python)
├── EXECUTAR.bat                # Script para execução no Windows
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config_manager.py
│   │   ├── mcp_manager.py
│   │   └── mcp_config.example.json
│   └── gui/                    # Componentes da interface gráfica
├── scripts/
│   ├── __init__.py
│   ├── create_directories.py
│   ├── secure_dirs_setup.py
│   └── setup_user_path.py
├── examples/
│   ├── __init__.py
│   ├── demo_integration.py
│   └── example_config_usage.py
├── tests/
│   ├── __init__.py
│   ├── test_batch_operations.py
│   ├── test_cli_switching.py
│   ├── test_config_manager.py
│   ├── test_corrupt_file_handling.py
│   ├── test_dependency_validation.py
│   ├── test_dependency_validation_complete.py
│   ├── test_gui_batch.py
│   └── test_mcp_manager_integration.py
```

## 🔧 Configuration
- **Environment Variables**: Configure variáveis de ambiente conforme necessário.
- **Configuration Files**: Utilize o arquivo `mcp_config.json` para armazenar configurações do usuário.
- **Customization Options**: Ajuste as configurações conforme necessário para atender às suas necessidades.

## 🤝 Contributing
- **How to Contribute**: Envie pull requests com melhorias e correções.
- **Development Setup**: Clone o repositório e instale as dependências.
- **Code Style Guidelines**: Siga o estilo de código PEP 8.
- **Pull Request Process**: Revise e melhore o código antes de enviar pull requests.

## 📝 License
Este projeto está licenciado sob a Licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👥 Authors & Contributors
- **Maintainers**: [Seu Nome]
- **Contributors**: [Lista de Contribuidores]

## 🐛 Issues & Support
- **Report Issues**: Crie uma issue no repositório para relatar problemas.
- **Get Help**: Envie uma mensagem no [canal de suporte](https://github.com/seu-usuario/InstalarMCP/issues).
- **FAQ**: Consulte a seção de perguntas frequentes para obter respostas rápidas.

## 🗺️ Roadmap
- **Planned Features**: Adicionar suporte para mais CLIs.
- **Known Issues**: Resolver problemas de compatibilidade com versões antigas do Python.
- **Future Improvements**: Melhorar a interface gráfica e adicionar novas funcionalidades.

---

**Badges:**
[![Build Status](https://github.com/seu-usuario/InstalarMCP/workflows/CI/badge.svg)](https://github.com/seu-usuario/InstalarMCP/actions)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Contributors](https://img.shields.io/github/contributors/seu-usuario/InstalarMCP)](https://github.com/seu-usuario/InstalarMCP/graphs/contributors)

---

**Additional Guidelines:**
- Use modern markdown features (badges, collapsible sections, etc.)
- Include practical, working code examples
- Make it visually appealing with appropriate emojis
- Ensure all code snippets are syntactically correct for Python
- Include relevant badges (build status, version, license, etc.)
- Make installation instructions copy-pasteable
- Focus on clarity and developer experience