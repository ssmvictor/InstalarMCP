# MCP Manager

Ferramenta para administrar servidores MCP (Model Context Protocol) usando Python.  
Esta versão mantém o arquivo `mcp_gui.py` na raiz do repositório e organiza o restante
do código em módulos e pacotes dedicados.

## Conteúdo

1. [Visão Geral](#visao-geral)
2. [Estrutura do Projeto](#estrutura-do-projeto)
3. [Componentes Principais](#componentes-principais)
4. [Configurando o Caminho do Usuário](#configurando-o-caminho-do-usuario)
5. [Executando a Interface Gráfica](#executando-a-interface-grafica)
6. [Executando Testes](#executando-testes)
7. [Exemplos e Ferramentas](#exemplos-e-ferramentas)

## Visao Geral

O MCP Manager lê e atualiza o arquivo `settings.json` usado pelo Gemini IDE e Qwen Coder CLI para definir
servidores MCP permitidos, templates pré-configurados e demais ajustes. O projeto oferece:

- Biblioteca para leitura, escrita e validação das configurações (`src/core`).
- Interface gráfica com Tkinter (`mcp_gui.py`) para selecionar o CLI (Gemini/Qwen).
- Scripts auxiliares e exemplos de uso (`scripts/` e `examples/`).

## Estrutura do Projeto

```
mcp/
├── mcp_gui.py                  # Interface gráfica principal
├── README.md                   # Este arquivo
├── src/
│   ├── __init__.py
│   └── core/
│       ├── __init__.py
│       ├── config_manager.py
│       ├── mcp_manager.py
│       └── mcp_config.json
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
│   ├── test_config_manager.py
│   ├── test_corrupt_file_handling.py
│   └── test_mcp_manager_integration.py
└── docs/
    └── ...
```

## Componentes Principais

### `src/core/config_manager.py`

- Controla o arquivo `mcp_config.json`, que armazena o caminho base do usuário.
- Normaliza caminhos e valida se o diretório informado existe e é acessível.
- Expõe a exceção `ConfigManagerError` para sinalizar problemas de configuração.

Exemplo rápido:

```python
from src.core.config_manager import ConfigManager, ConfigManagerError

config = ConfigManager()
try:
    config.set_user_path("C:/Users/SEU_USUARIO")
except ConfigManagerError as err:
    print(f"Erro ao configurar caminho: {err}")
else:
    print(f"Caminho salvo em: {config.get_user_path()}")
```

### `src/core/mcp_manager.py`

- Lê e escreve o arquivo `settings.json` localizado no diretório `.gemini` ou `.qwen` do usuário.
- Realiza backup automático antes de salvar alterações.
- Permite adicionar, remover, ativar/desativar e consultar servidores MCP.
- Gera templates pré-configurados com comandos prontos.

Uso básico:

```python
from src.core.mcp_manager import MCPManager

manager = MCPManager()  # Usa ConfigManager para localizar settings.json
mcps = manager.get_mcps()
print(f"Servidores configurados: {list(mcps)}")
```

### `mcp_gui.py`

- Interface Tkinter que consome os módulos anteriores.
- Permite visualizar servidores cadastrados, instalar templates, ativar/desativar,
  atualizar caminhos e salvar alterações.
- Permite selecionar o CLI (Gemini/Qwen) através do menu.
- Usa os mesmos módulos `MCPManager` e `ConfigManager` que podem ser usados via código.

## Configurando o Caminho do Usuario

O MCP Manager precisa saber onde fica o diretório base do usuário (ex.: `C:/Users/NOME`).
Execute o script abaixo para definir esse caminho:

```bash
python -m scripts.setup_user_path
```

O assistente irá:
1. Mostrar o caminho atual (se houver).
2. Validar o novo caminho informado.
3. Perguntar qual CLI prefere (Gemini ou Qwen).
4. Persistir a configuração em `src/core/mcp_config.json` (ou em `%APPDATA%/MCPManager`
   no Windows caso seja necessário).

Você pode usar a classe `ConfigManager` diretamente em código se preferir automatizar
esse processo.

> Observação: o repositório inclui somente o template `src/core/mcp_config.example.json`
> com um valor placeholder. O arquivo real `src/core/mcp_config.json` é criado pelo
> `ConfigManager` na primeira execução do script ou da aplicação. Se quiser definir manualmente,
> faça uma cópia do template e ajuste o caminho conforme necessário.

## Executando a Interface Grafica

Depois de configurar o caminho do usuário, rode a interface:

```bash
python mcp_gui.py
```

A janela principal permite:

- Instalar servidores MCP a partir de templates ou manualmente.
- Ativar e desativar servidores.
- Editar caminho do usuário via menu Arquivo > Configurar caminho do usuário.
- Salvar alterações no `settings.json`.

## Executando Testes

Os testes estão em `tests/` e usam `unittest`. Para executar todo o conjunto:

```bash
python -m unittest
```

É possível rodar testes específicos, por exemplo:

```bash
python -m unittest tests.test_config_manager
```

## Notas de Atualização

- **Breaking change**: módulos anteriormente acessíveis na raiz (`config_manager.py`,
  `mcp_manager.py`) agora vivem em `src/core`. Código externo deve atualizar os imports para
  `from src.core.config_manager import ...` e `from src.core.mcp_manager import ...`.
  Essa reorganização mantém apenas `mcp_gui.py` na raiz e simplifica a manutenção da base.

## Exemplos e Ferramentas

- `examples/example_config_usage.py`: demonstra o uso da API `ConfigManager`.
  Execute com `python -m examples.example_config_usage`.
- `examples/demo_integration.py`: mostra a integração completa entre os módulos.
- `scripts/create_directories.py`: garante a existência das pastas necessárias
  para o projeto.
- `scripts/secure_dirs_setup.py`: utilitário para criar diretórios com permissões seguras.

Esses arquivos podem ser usados como referência ao desenvolver integrações ou
automatizações adicionais.
