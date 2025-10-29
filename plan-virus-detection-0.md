I have created the following plan after thorough exploration and analysis of the codebase. Follow the below plan verbatim. Trust the files and references. Do not re-verify what's written in the plan. Explore only when absolutely necessary. First implement all the proposed file changes and then I'll review all the changes together at the end.

### Observations

O problema ocorre porque o arquivo `EXECUTAR.bat` contém o comando `python -m pip install -r requirements.txt`, que faz o Google Chrome detectar o ZIP como vírus (falso positivo). Antivírus e navegadores são sensíveis a scripts batch que executam instalações automáticas, downloads ou modificações no sistema. O projeto tem dependências mínimas (apenas `ttkthemes`, que é opcional), tornando a separação entre instalação e execução uma solução ideal.

### Approach

Implementar a **Estratégia 1** (separar instalação da execução) combinada com medidas de mitigação. Criar um novo arquivo `INSTALAR.bat` para instalação única das dependências, modificar `EXECUTAR.bat` para remover comandos de instalação, atualizar documentação no `README.md`, criar arquivo `SECURITY.md` para explicar o falso positivo, e melhorar `.gitattributes` para garantir tratamento correto dos arquivos.

### Reasoning

Listei a estrutura do repositório, li o arquivo `EXECUTAR.bat` para entender as modificações feitas, li o `README.md` e `requirements.txt` para compreender o contexto do projeto e suas dependências, e li o `.gitattributes` para verificar a configuração atual de tratamento de arquivos.

## Mermaid Diagram

sequenceDiagram
    participant U as Usuário
    participant GH as GitHub
    participant C as Chrome/Antivírus
    participant I as INSTALAR.bat
    participant E as EXECUTAR.bat
    participant A as Aplicação MCP

    Note over U,A: Situação Atual (Problema)
    U->>GH: Download ZIP
    GH->>U: Arquivo ZIP
    C->>U: ⚠️ VÍRUS DETECTADO (falso positivo)
    Note over C: EXECUTAR.bat contém<br/>pip install

    Note over U,A: Solução Implementada
    
    rect rgb(200, 255, 200)
        Note over U,A: Primeira Execução
        U->>GH: Download Release Oficial
        GH->>U: ZIP sem detecção
        U->>I: Executa INSTALAR.bat
        I->>I: pip install -r requirements.txt
        I->>U: ✅ Dependências instaladas
    end
    
    rect rgb(200, 220, 255)
        Note over U,A: Execuções Subsequentes
        U->>E: Executa EXECUTAR.bat
        Note over E: Sem comandos pip<br/>Apenas execução
        E->>A: python mcp_gui.py
        A->>U: Interface Gráfica
    end
    
    Note over U,A: Documentação e Segurança
    U->>GH: Lê SECURITY.md
    Note over U: Entende que é<br/>falso positivo
    U->>GH: Lê README.md
    Note over U: Instruções claras<br/>de instalação

## Proposed File Changes

### INSTALAR.bat(NEW)

References: 

- requirements.txt
- EXECUTAR.bat(MODIFY)

Criar novo arquivo batch dedicado exclusivamente à instalação das dependências do projeto. Este arquivo será executado apenas uma vez pelo usuário após baixar o projeto.

**Estrutura do arquivo:**
- Incluir cabeçalho com `@echo off` e `setlocal`
- Detectar o diretório do script usando `%~dp0`
- Navegar para o diretório do projeto com `pushd`
- Verificar existência do arquivo `requirements.txt`
- Executar `python -m pip install -r requirements.txt`
- Incluir tratamento de erros com `errorlevel` e mensagens claras em português
- Adicionar mensagem de sucesso ao final
- Incluir pausa opcional para o usuário ver o resultado
- Retornar ao diretório original com `popd`
- Finalizar com `endlocal` e código de saída apropriado

**Mensagens importantes:**
- Informar que este script instala as dependências necessárias
- Explicar que precisa ser executado apenas uma vez
- Indicar que após a instalação, usar `EXECUTAR.bat` para executar a aplicação
- Verificar se Python e pip estão instalados e acessíveis no PATH

### EXECUTAR.bat(MODIFY)

References: 

- mcp_gui.py
- INSTALAR.bat(NEW)

Modificar o arquivo para remover completamente a lógica de instalação automática de dependências, mantendo apenas a funcionalidade de execução da aplicação.

**Modificações necessárias:**
- Manter o cabeçalho com `@echo off` e `setlocal`
- Manter a detecção do diretório do script (`%~dp0`)
- Manter a navegação para o diretório do projeto com `pushd`
- **REMOVER** completamente o bloco de instalação de dependências (linhas 10-20 que verificam `requirements.txt` e executam `pip install`)
- Manter apenas a execução do `python mcp_gui.py` (linha 23)
- Manter a captura do código de saída com `%ERRORLEVEL%`
- Manter o retorno ao diretório original com `popd`
- Manter a finalização com `endlocal` e código de saída
- Adicionar comentário no início explicando que as dependências devem ser instaladas primeiro usando `INSTALAR.bat`

**Resultado esperado:**
O arquivo ficará mais simples, focado apenas em executar a aplicação, sem comandos que possam ser detectados como suspeitos por antivírus.

### README.md(MODIFY)

References: 

- INSTALAR.bat(NEW)
- EXECUTAR.bat(MODIFY)
- SECURITY.md(NEW)

Atualizar a documentação para refletir a nova estrutura de instalação e execução, além de adicionar seção sobre o falso positivo de antivírus.

**Seção 1: Adicionar aviso sobre falso positivo (após "Visão Geral")**
- Criar nova seção "⚠️ Aviso Importante sobre Antivírus"
- Explicar que alguns antivírus/navegadores podem detectar o ZIP como suspeito (falso positivo)
- Esclarecer que o código é open-source e pode ser inspecionado
- Orientar a verificar o código antes de executar
- Mencionar que o projeto não contém malware
- Incluir link para o arquivo `SECURITY.md` (a ser criado)

**Seção 2: Atualizar "Executando a Interface Gráfica" (linha 136)**
- Renomear para "Instalação e Execução"
- Adicionar subseção "Primeira Execução (Instalação)"
  - Instruir a executar `INSTALAR.bat` no Windows OU `pip install -r requirements.txt` manualmente
  - Explicar que isso instala as dependências necessárias
  - Mencionar que precisa ser feito apenas uma vez
- Adicionar subseção "Execução Normal"
  - Instruir a executar `EXECUTAR.bat` no Windows OU `python mcp_gui.py` diretamente
  - Explicar que este comando inicia a interface gráfica

**Seção 3: Atualizar referência ao EXECUTAR.bat (linha 33)**
- Adicionar linha mencionando `INSTALAR.bat` como script de instalação
- Manter `EXECUTAR.bat` como script de execução

**Seção 4: Melhorar seção de dependências (linha 151)**
- Manter informação sobre `ttkthemes` sendo opcional
- Adicionar nota que a instalação é feita via `INSTALAR.bat` ou manualmente

**Formatação:**
- Usar emojis para destacar avisos importantes (⚠️, ✅, 📦)
- Manter formatação markdown consistente
- Adicionar exemplos de comandos em blocos de código
Adicionar seção sobre como criar releases oficiais no GitHub para distribuição mais segura do projeto.

**Nova seção: "Distribuição e Download Seguro" (adicionar após "Executando Testes")**

**Conteúdo da seção:**
- Explicar que o projeto está disponível via GitHub Releases
- Recomendar baixar releases oficiais em vez do ZIP direto do código
- Instruir como verificar a autenticidade do release
- Mencionar que releases oficiais têm menos chance de falso positivo
- Incluir link para a página de releases do repositório
- Adicionar nota sobre verificação de checksums (se implementado)

**Benefícios:**
- Releases oficiais são mais confiáveis para usuários
- GitHub marca releases de forma diferente de downloads diretos
- Permite adicionar notas de versão e changelog
- Possibilita incluir checksums para verificação de integridade
- Reduz significativamente detecções de falso positivo

**Nota para o mantenedor:**
Esta seção serve como documentação para quando você criar releases oficiais no GitHub. Releases devem ser criados através da interface do GitHub (Releases > Create a new release), incluindo tag de versão, título descritivo e notas de lançamento.

### SECURITY.md(NEW)

References: 

- README.md(MODIFY)
- INSTALAR.bat(NEW)
- EXECUTAR.bat(MODIFY)
- requirements.txt

Criar arquivo de segurança seguindo o padrão GitHub Security Policy para explicar o falso positivo e fornecer informações de segurança do projeto.

**Estrutura do arquivo:**

**Seção 1: Cabeçalho**
- Título "Security Policy" ou "Política de Segurança"
- Breve introdução sobre o compromisso com segurança

**Seção 2: Sobre Falsos Positivos de Antivírus**
- Explicar que alguns antivírus/navegadores podem detectar o projeto como suspeito
- Detalhar a causa: arquivos `.bat` que executam comandos de instalação
- Esclarecer que é um falso positivo comum em projetos Python
- Mencionar que o código é 100% open-source e auditável

**Seção 3: Como Verificar a Segurança**
- Instruir a inspecionar o código-fonte antes de executar
- Listar os arquivos principais a verificar: `INSTALAR.bat`, `EXECUTAR.bat`, `mcp_gui.py`
- Explicar que o projeto não faz download de arquivos externos não documentados
- Mencionar que todas as dependências estão listadas em `requirements.txt`
- Sugerir verificar o hash do arquivo baixado (se disponível)

**Seção 4: O que o Projeto Faz**
- Descrever claramente as operações realizadas:
  - `INSTALAR.bat`: instala dependências Python via pip
  - `EXECUTAR.bat`: executa a interface gráfica
  - `mcp_gui.py`: gerencia configurações MCP localmente
- Explicar que não há comunicação com servidores externos (exceto pip para instalação)
- Mencionar que o projeto apenas lê/escreve arquivos de configuração locais

**Seção 5: Reportando Vulnerabilidades**
- Criar seção padrão "Reporting a Vulnerability"
- Fornecer instruções de como reportar problemas de segurança
- Incluir informações de contato (GitHub Issues ou email)
- Definir tempo esperado de resposta

**Seção 6: Versões Suportadas**
- Listar versões do projeto que recebem atualizações de segurança
- Indicar a versão atual como suportada

**Formatação:**
- Usar markdown com cabeçalhos hierárquicos
- Incluir emojis para melhor visualização (🔒, ⚠️, ✅)
- Adicionar badges se aplicável
- Manter tom profissional e transparente

### .gitattributes(MODIFY)

References: 

- INSTALAR.bat(NEW)
- EXECUTAR.bat(MODIFY)

Melhorar o arquivo `.gitattributes` para garantir tratamento correto dos arquivos, especialmente os scripts batch, reduzindo chances de corrupção e problemas de detecção.

**Modificações necessárias:**

**1. Manter configuração atual:**
- Manter a linha `* text=auto` para detecção automática

**2. Adicionar regras específicas para arquivos batch:**
- Adicionar `*.bat text eol=crlf` para garantir que arquivos `.bat` sempre usem line endings Windows (CRLF)
- Isso é crítico porque arquivos batch com LF podem não funcionar corretamente no Windows

**3. Adicionar regras para arquivos Python:**
- Adicionar `*.py text eol=lf` para arquivos Python usarem line endings Unix (LF)
- Isso segue a convenção padrão Python (PEP 8)

**4. Adicionar regras para arquivos de documentação:**
- Adicionar `*.md text eol=lf` para arquivos Markdown
- Adicionar `*.txt text eol=lf` para arquivos de texto

**5. Adicionar regras para arquivos de configuração:**
- Adicionar `*.json text eol=lf` para arquivos JSON

**6. Adicionar comentários explicativos:**
- Incluir comentários explicando cada seção
- Documentar por que CRLF é necessário para `.bat`

**Objetivo:**
Garantir que os arquivos sejam tratados corretamente pelo Git, evitando problemas de line endings que podem causar mau funcionamento ou aumentar suspeitas de antivírus. Arquivos batch com line endings incorretos podem ser detectados como corrompidos ou modificados maliciosamente.