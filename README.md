# MCP Manager

Ferramenta para administrar servidores MCP (Model Context Protocol) usando Python.  
Esta versÃ£o mantÃ©m o arquivo `mcp_gui.py` na raiz do repositÃ³rio e organiza o restante
do cÃ³digo em mÃ³dulos e pacotes dedicados.

## ConteÃºdo

1. [Visao Geral](#visao-geral)
2.
3. [Estrutura do Projeto](#estrutura-do-projeto)
4. [Componentes Principais](#componentes-principais)
5. [Configurando o Caminho do Usuario](#configurando-o-caminho-do-usuario)
6. [Instalacao e Execucao](#instalacao-e-execucao)
7. [Executando Testes](#executando-testes)
8. [Distribuicao e Download Seguro](#distribuicao-e-download-seguro)
9. [Exemplos e Ferramentas](#exemplos-e-ferramentas)

## Visao Geral

O MCP Manager lÃª e atualiza o arquivo `settings.json` usado pelo Gemini IDE e Qwen Coder CLI para definir
servidores MCP permitidos, templates prÃ©-configurados e demais ajustes. O projeto oferece:

- Biblioteca para leitura, escrita e validaÃ§Ã£o das configuraÃ§Ãµes (`src/core`).
- Interface grÃ¡fica com Tkinter (`mcp_gui.py`) para selecionar o CLI (Gemini/Qwen).
- Scripts auxiliares e exemplos de uso (`scripts/` e `examples/`).


## Estrutura do Projeto

```
â”œâ”€â”€ mcp_gui.py                  # Interface grÃ¡fica principal
â”œâ”€â”€ README.md                   # Este arquivo
â”œâ”€â”€ CLI.md                      # DocumentaÃ§Ã£o da CLI
â”œâ”€â”€ requirements.txt            # DependÃªncias do projeto
â”œâ”€â”€ INSTALAR.bat                # Script de instalacao (Windows)
â”œâ”€â”€ EXECUTAR.bat                # Script para execuÃ§Ã£o no Windows
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ core/
â”‚   â”‚   â”œâ”€â”€ __init__.py
â”‚   â”‚   â”œâ”€â”€ config_manager.py
â”‚   â”‚   â”œâ”€â”€ mcp_manager.py
â”‚   â”‚   â””â”€â”€ mcp_config.example.json
â”‚   â””â”€â”€ gui/                    # Componentes da interface grÃ¡fica
â”œâ”€â”€ scripts/
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ create_directories.py
â”‚   â”œâ”€â”€ secure_dirs_setup.py
â”‚   â””â”€â”€ setup_user_path.py
â”œâ”€â”€ examples/
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ demo_integration.py
â”‚   â””â”€â”€ example_config_usage.py
â”œâ”€â”€ tests/
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ test_batch_operations.py
â”‚   â”œâ”€â”€ test_cli_switching.py
â”‚   â”œâ”€â”€ test_config_manager.py
â”‚   â”œâ”€â”€ test_corrupt_file_handling.py
â”‚   â”œâ”€â”€ test_dependency_validation.py
â”‚   â”œâ”€â”€ test_dependency_validation_complete.py
â”‚   â”œâ”€â”€ test_gui_batch.py
â”‚   â””â”€â”€ test_mcp_manager_integration.py
â””â”€â”€ docs/
    â””â”€â”€ ...
```

## Componentes Principais

### `src/core/config_manager.py`

- Controla o arquivo `mcp_config.json`, que armazena o caminho base do usuÃ¡rio.
- Normaliza caminhos e valida se o diretÃ³rio informado existe e Ã© acessÃ­vel.
- ExpÃµe a exceÃ§Ã£o `ConfigManagerError` para sinalizar problemas de configuraÃ§Ã£o.

Exemplo rÃ¡pido:

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

- LÃª e escreve o arquivo `settings.json` localizado no diretÃ³rio `.gemini` ou `.qwen` do usuÃ¡rio.
- Realiza backup automÃ¡tico antes de salvar alteraÃ§Ãµes.
- Permite adicionar, remover, ativar/desativar e consultar servidores MCP.
- Gera templates prÃ©-configurados com comandos prontos.

Uso bÃ¡sico:

```python
from src.core.mcp_manager import MCPManager

manager = MCPManager()  # Usa ConfigManager para localizar settings.json
mcps = manager.get_mcps()
print(f"Servidores configurados: {list(mcps)}")
```

### `mcp_gui.py`

- Interface Tkinter que consome os mÃ³dulos anteriores.
- Permite visualizar servidores cadastrados, instalar templates, ativar/desativar,
  atualizar caminhos e salvar alteraÃ§Ãµes.
- Permite selecionar o CLI (Gemini/Qwen) atravÃ©s do menu.
- Usa os mesmos mÃ³dulos `MCPManager` e `ConfigManager` que podem ser usados via cÃ³digo.

## Configurando o Caminho do Usuario

O MCP Manager precisa saber onde fica o diretÃ³rio base do usuÃ¡rio (ex.: `C:/Users/NOME`).
Execute o script abaixo para definir esse caminho:

```bash
python -m scripts.setup_user_path
```

O assistente irÃ¡:
1. Mostrar o caminho atual (se houver).
2. Validar o novo caminho informado.
3. Perguntar qual CLI prefere (Gemini ou Qwen).
4. Persistir a configuraÃ§Ã£o em `src/core/mcp_config.json` (ou em `%APPDATA%/MCPManager`
   no Windows caso seja necessÃ¡rio).

VocÃª pode usar a classe `ConfigManager` diretamente em cÃ³digo se preferir automatizar
esse processo.

> ObservaÃ§Ã£o: o repositÃ³rio inclui somente o template `src/core/mcp_config.example.json`
> com um valor placeholder. O arquivo real `src/core/mcp_config.json` Ã© criado pelo
> `ConfigManager` na primeira execuÃ§Ã£o do script ou da aplicaÃ§Ã£o. Se quiser definir manualmente,
> faÃ§a uma cÃ³pia do template e ajuste o caminho conforme necessÃ¡rio.

## Instalacao e Execucao

### Primeira Execucao (Instalacao)

- Windows: execute `INSTALAR.bat` (instala dependencias via pip). Execute apenas uma vez.
- Multiplataforma (manual): `pip install -r requirements.txt`.

### Execucao Normal

- Windows: `EXECUTAR.bat`.
- Multiplataforma: `python mcp_gui.py`.

A janela principal permite:

- Instalar servidores MCP a partir de templates ou manualmente.
- Ativar e desativar servidores.
- Editar caminho do usuÃ¡rio via menu Arquivo > Configurar caminho do usuÃ¡rio.
- Salvar alteraÃ§Ãµes no `settings.json`.

### Dependencias Opcionais

- `ttkthemes`: opcional, fornece temas adicionais para a interface grÃ¡fica. Se nÃ£o instalado, a aplicaÃ§Ã£o usa o tema padrÃ£o do Tkinter.
- Instalacao via `INSTALAR.bat` ou manualmente com `pip install -r requirements.txt`.

## Executando Testes

Os testes estÃ£o em `tests/` e usam `unittest`. Para executar todo o conjunto:

```bash
python -m unittest
```

Ã‰ possÃ­vel rodar testes especÃ­ficos, por exemplo:

```bash
python -m unittest tests.test_config_manager
```

### DependÃªncias de Teste

- `unittest.mock`: Parte da biblioteca padrÃ£o do Python (versÃ£o 3.3+), utilizado para testes que necessitam de mocking (simulaÃ§Ã£o de componentes).

Para instalar as dependÃªncias:

```bash
pip install -r requirements.txt
```

Nota: `unittest.mock` jÃ¡ estÃ¡ incluÃ­do na instalaÃ§Ã£o padrÃ£o do Python, nÃ£o necessitando instalaÃ§Ã£o adicional.

## Distribuicao e Download Seguro

- Prefira baixar versÃµes oficiais na pÃ¡gina de Releases do GitHub do projeto.
- Releases oficiais tendem a ter menor chance de falso positivo em antivÃ­rus.
- Verifique a autenticidade do release (tags, notas de versÃ£o e, se disponÃ­vel, checksums).
- Releases permitem notas e changelog claros, facilitando auditoria e adoÃ§Ã£o.

## Notas de AtualizaÃ§Ã£o

- **Breaking change**: mÃ³dulos anteriormente acessÃ­veis na raiz (`config_manager.py`,
  `mcp_manager.py`) agora vivem em `src/core`. CÃ³digo externo deve atualizar os imports para
  `from src.core.config_manager import ...` e `from src.core.mcp_manager import ...`.
  Essa reorganizaÃ§Ã£o mantÃ©m apenas `mcp_gui.py` na raiz e simplifica a manutenÃ§Ã£o da base.

## Exemplos e Ferramentas

- `examples/example_config_usage.py`: demonstra o uso da API `ConfigManager`.
  Execute com `python -m examples.example_config_usage`.
- `examples/demo_integration.py`: mostra a integraÃ§Ã£o completa entre os mÃ³dulos.
- `scripts/create_directories.py`: garante a existÃªncia das pastas necessÃ¡rias
  para o projeto.
- `scripts/secure_dirs_setup.py`: utilitÃ¡rio para criar diretÃ³rios com permissÃµes seguras.

Esses arquivos podem ser usados como referÃªncia ao desenvolver integraÃ§Ãµes ou
automatizaÃ§Ãµes adicionais.



