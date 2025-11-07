# MCP Manager



Ferramenta para administrar servidores MCP (Model Context Protocol) usando Python.  

Esta versão mantém o arquivo `mcp_gui.py` na raiz do repositório e organiza o restante

do código em módulos e pacotes dedicados.



## Conteúdo

1. [Visao Geral](#visao-geral)
2. [Instalacao do Github Spec-Kit](#instalacao-do-github-spec-kit)
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



## Instalacao do Github Spec-Kit

### Visao Geral

O Github Spec-Kit é uma ferramenta desenvolvida pelo GitHub para facilitar a especificação e documentação de APIs. Esta funcionalidade está disponível através da aba "Instalar Spec-Kit" na interface gráfica do MCP Manager, que automatiza todo o processo de instalação no Windows.

A ferramenta instala o gerenciador de pacotes UV (se necessário), instala o Spec-Kit a partir do repositório oficial do GitHub, e configura o ambiente Windows para tornar o comando `specify` disponível em qualquer terminal.

Para mais informações sobre o Spec-Kit, consulte a documentação oficial: `https://github.com/github/spec-kit`

### Pre-requisitos

- **Sistema Operacional**: Windows (a funcionalidade é específica para Windows)
- **Privilégios de Administrador**: Não necessários. A ferramenta adiciona o UV bin ao PATH do usuário (HKCU) e não requer privilégios de administrador.
- **Conexão com Internet**: Necessária para baixar o UV e o Spec-Kit do GitHub
- **PowerShell**: Disponível por padrão no Windows, usado para instalação do UV

> Nota: A aba 'Instalar Spec-Kit' só aparece na interface quando executada no Windows

### Funcionalidades da Aba

- **Status de Privilégios**: Exibe se a aplicação está sendo executada como administrador
- **Botões de Ação Individual**: Permite executar cada etapa separadamente
- **Botão 'Executar Tudo'**: Automatiza todo o processo de instalação
- **Área de Logs**: Mostra o progresso em tempo real de cada operação

### Passos Automaticos Realizados

1. **Verificação do UV**: Verifica se o gerenciador de pacotes UV está instalado no sistema
2. **Instalação do UV** (se necessário): Executa o script PowerShell oficial para instalar o UV: `irm https://astral.sh/uv/install.ps1 | iex`
3. **Instalação do Spec-Kit**: Executa o comando `uv tool install specify-cli --from git+https://github.com/github/spec-kit.git` para instalar globalmente
4. **Detecção do Caminho do Bin**: Identifica automaticamente o caminho onde o UV instalou os binários (geralmente `C:\Users\<USUARIO>\.local\bin`)
5. **Adição ao PATH**: Modifica o registro do Windows (chave `HKEY_CURRENT_USER\Environment`) para adicionar o caminho do bin à variável PATH do usuário
6. **Notificação do Sistema**: Envia broadcast `WM_SETTINGCHANGE` para notificar o sistema sobre a mudança na variável de ambiente

> Nota: A instalação completa pode levar de 5 a 15 minutos, dependendo da velocidade da conexão com a internet

### Como Usar

1. Abrir a aplicação MCP Manager (`EXECUTAR.bat` ou `python mcp_gui.py`)
2. Navegar até a aba "Instalar Spec-Kit"
3. Verificar o status de privilégios de administrador exibido no topo
4. Escolher entre duas opções:
   - **Opção A - Instalação Automática**: Clicar no botão "Executar Tudo" para realizar todas as etapas automaticamente
   - **Opção B - Instalação Manual**: Executar cada etapa individualmente usando os botões específicos (útil para diagnóstico ou se alguma etapa falhar)
5. Acompanhar o progresso através da área de logs
6. Aguardar a conclusão de todas as etapas

### Notas Importantes sobre PATH

- **Caminho do UV Bin**: Por padrão, o UV instala ferramentas em `C:\Users\<USUARIO>\.local\bin`. Este caminho é detectado automaticamente pela ferramenta usando o comando `uv tool dir --bin`
- **Modificação do PATH**: A ferramenta adiciona o caminho ao início da variável PATH do usuário (HKCU - HKEY_CURRENT_USER), não do sistema. Alterações no PATH do sistema não são suportadas pela ferramenta atualmente.
- **Persistência**: A modificação é permanente e persiste após reinicialização do sistema
- **Novos Terminais**: É necessário abrir um novo terminal (PowerShell, CMD, ou outro) após a instalação para que as mudanças no PATH tenham efeito. Terminais já abertos não verão a mudança
- **Verificação**: Para verificar se o Spec-Kit foi instalado corretamente, abrir um novo terminal e executar `specify --version`

### Solucao de Problemas

- **Erro de Permissão ao Modificar PATH**:
  - Causa: Falta de privilégios para modificar o registro
  - Solução: Executar a aplicação como administrador (clicar com botão direito em `EXECUTAR.bat` > "Executar como administrador")
- **UV não encontrado após instalação**:
  - Causa: Terminal antigo ainda aberto
  - Solução: Fechar todos os terminais e abrir um novo
- **Timeout durante instalação**:
  - Causa: Conexão lenta com a internet
  - Solução: Verificar conexão e tentar novamente. A ferramenta tem timeout de 5 minutos para UV e 10 minutos para Spec-Kit. Se o timeout for excedido, o processo será automaticamente terminado.
- **Spec-Kit não funciona após instalação**:
  - Causa: PATH não foi atualizado corretamente
  - Solução: Verificar manualmente se o caminho `C:\Users\<USUARIO>\.local\bin` está no PATH usando `echo %PATH%` no CMD

### Integracao com Codigo

```python
from src.core.speckit_manager import SpecKitManager, SpecKitManagerError

try:
    manager = SpecKitManager()
    
    # Verificar se UV está instalado
    is_installed, version = manager.check_uv_installed()
    if not is_installed:
        print("Instalando UV...")
        manager.install_uv()
    
    # Instalar Spec-Kit
    print("Instalando Spec-Kit...")
    manager.install_speckit()
    
    # Adicionar ao PATH
    bin_path = manager.get_uv_bin_path()
    if bin_path:
        manager.add_to_windows_path(bin_path)
        print(f"Spec-Kit instalado com sucesso!")
        print(f"Abra um novo terminal para usar o comando 'specify'")
    
except SpecKitManagerError as err:
    print(f"Erro durante instalação: {err}")
```

> Nota: O módulo `SpecKitManager` está disponível em `src/core/speckit_manager.py` e pode ser usado programaticamente em scripts de automação

### Referencias

- Documentação oficial do Spec-Kit: `https://github.com/github/spec-kit`
- Documentação do UV: `https://github.com/astral-sh/uv`
- Documentação sobre variáveis de ambiente no Windows: `https://docs.microsoft.com/pt-br/windows/win32/procthread/environment-variables`


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

