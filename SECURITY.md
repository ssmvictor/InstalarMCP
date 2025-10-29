# Política de Segurança

Nos comprometemos com a transparência e a segurança dos usuários do MCP Manager. Este projeto é open‑source e todo o código pode ser auditado publicamente.

## 🔶 Falsos Positivos de Antivírus

Alguns antivírus e navegadores podem sinalizar o download do projeto (especialmente arquivos ZIP) como suspeito. Isso ocorre porque scripts `.bat` que executam instalações com `pip` são frequentemente classificados como potencialmente perigosos por heurísticas automatizadas.

- Causa principal: scripts batch que instalam dependências (ex.: `pip install`).
- Mitigação adotada: separamos a instalação da execução.
  - `INSTALAR.bat`: instala dependências uma única vez.
  - `EXECUTAR.bat`: apenas inicia a aplicação, sem instalar nada.

Este é um falso positivo comum em projetos Python. O repositório não contém malware.

## ✅ Como Verificar a Segurança

- Inspecione o código-fonte antes de executar, em especial:
  - `INSTALAR.bat`: instala dependências via `pip`.
  - `EXECUTAR.bat`: executa `python mcp_gui.py`.
  - `mcp_gui.py`: interface gráfica principal do projeto.
- Todas as dependências estão listadas em `requirements.txt`.
- O projeto não baixa arquivos externos além das dependências declaradas.
- Se disponível, verifique checksums/hashes dos artefatos de release.

## 🔍 O que o Projeto Faz

- `INSTALAR.bat`: instala as dependências Python com `pip` (execução única).
- `EXECUTAR.bat`: inicia a interface gráfica do MCP Manager.
- `mcp_gui.py`: provê a interface com Tkinter para gerenciar configurações MCP locais.
- O projeto lê e escreve arquivos de configuração locais. Não se comunica com servidores remotos durante a execução da aplicação.

## 📣 Reportando Vulnerabilidades

Se você encontrar um problema de segurança:

- Abra uma issue no GitHub com o rótulo "security" OU
- Envie detalhes pelo canal de contato indicado no repositório.

Inclua passos de reprodução, impacto e qualquer sugestão de mitigação. Tentamos responder em até 7 dias úteis.

## 🧭 Versões Suportadas

- Versão atual (branch `main`): suportada.
- Releases estáveis: suporte conforme notas de versão.

Para maior segurança, prefira baixar binários/artefatos em "GitHub Releases" quando disponíveis.

