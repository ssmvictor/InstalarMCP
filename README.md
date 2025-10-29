# MCP Manager



Ferramenta para administrar servidores MCP (Model Context Protocol) usando Python.  

Esta versão mantém o arquivo `mcp_gui.py` na raiz do repositório e organiza o restante

do código em módulos e pacotes dedicados.



## Conteúdo

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


O MCP Manager lê e atualiza o arquivo `settings.json` usado pelo Gemini IDE e Qwen Coder CLI para definir
servidores MCP permitidos, templates pré-configurados e demais ajustes. O projeto oferece:


- Biblioteca para leitura, escrita e validação das configurações (`src/core`).

- Interface gráfica com Tkinter (`mcp_gui.py`) para selecionar o CLI (Gemini/Qwen).

- Scripts auxiliares e exemplos de uso (`scripts/` e `examples/`).


## Estrutura do Projeto



```

├── mcp_gui.py                  # Interface gráfica principal

├── README.md                   # Este arquivo

├── CLI.md                      # Documentação da CLI

├── requirements.txt            # Dependências do projeto
├── INSTALAR.bat                # Script de instalacao (Windows)
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



## Instalacao e Execucao

### Primeira Execucao (Instalacao)

- Windows: execute `INSTALAR.bat` (instala dependencias via pip). Execute apenas uma vez.
- Multiplataforma (manual): `pip install -r requirements.txt`.

### Execucao Normal

- Windows: `EXECUTAR.bat` (chama `executar.py` que verifica dependências e executa a interface).
- Multiplataforma: `python executar.py` (verifica dependências) ou `python mcp_gui.py`.

A janela principal permite:


- Instalar servidores MCP a partir de templates ou manualmente.

- Ativar e desativar servidores.

- Editar caminho do usuário via menu Arquivo > Configurar caminho do usuário.

- Salvar alterações no `settings.json`.



### Dependencias Opcionais

- `ttkthemes`: opcional, fornece temas adicionais para a interface gráfica. Se não instalado, a aplicação usa o tema padrão do Tkinter.
- Instalacao via `INSTALAR.bat` ou manualmente com `pip install -r requirements.txt`.


## Executando Testes


Os testes estão em `tests/` e usam `unittest`. Para executar todo o conjunto:



```bash

python -m unittest

```



É possível rodar testes específicos, por exemplo:



```bash

python -m unittest tests.test_config_manager

```



### Dependências de Teste



- `unittest.mock`: Parte da biblioteca padrão do Python (versão 3.3+), utilizado para testes que necessitam de mocking (simulação de componentes).



Para instalar as dependências:



```bash

pip install -r requirements.txt

```



Nota: `unittest.mock` já está incluído na instalação padrão do Python, não necessitando instalação adicional.

## Distribuicao e Download Seguro

- Prefira baixar versões oficiais na página de Releases do GitHub do projeto.
- Verifique a autenticidade do release (tags, notas de versão e, se disponível, checksums).
- Releases permitem notas e changelog claros, facilitando auditoria e adoção.


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

