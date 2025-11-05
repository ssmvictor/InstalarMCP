I have created the following plan after thorough exploration and analysis of the codebase. Follow the below plan verbatim. Trust the files and references. Do not re-verify what's written in the plan. Explore only when absolutely necessary. First implement all the proposed file changes and then I'll review all the changes together at the end.

### Observations

Identifiquei que o arquivo `settings.json` está sendo criado com o campo `security.auth.selectedType` hardcoded como `"oauth-personal"` em dois locais do `src/core/mcp_manager.py` (linhas 158 e 245). O sistema já possui suporte para múltiplos tipos de CLI (gemini e qwen) através do `ConfigManager`, mas a configuração de segurança não está respeitando essa diferenciação. O `MCPManager` já utiliza o `cli_type` do `ConfigManager` para determinar o diretório correto (`.gemini` ou `.qwen`), mas não o utiliza para definir o tipo de autenticação apropriado.

### Approach

Modificar o método `load_settings()` da classe `MCPManager` para determinar dinamicamente o valor de `security.auth.selectedType` baseado no tipo de CLI configurado. Quando o CLI for "qwen", usar `"qwen-oauth"`; quando for "gemini", manter `"oauth-personal"`. Esta lógica será aplicada tanto na criação inicial do arquivo quanto na recuperação de arquivos corrompidos. Os testes também serão atualizados para validar este comportamento diferenciado.

### Reasoning

Listei a estrutura do repositório e identifiquei os arquivos principais. Busquei por referências a "settings.json", "oauth-personal" e "selectedType" para localizar onde o campo de segurança está sendo definido. Encontrei duas ocorrências no `mcp_manager.py` onde o settings padrão é criado. Verifiquei como o sistema determina o tipo de CLI através do `config_manager.py` e confirmei que não há implementação atual de "qwen-oauth".

## Mermaid Diagram

sequenceDiagram
    participant User
    participant MCPManager
    participant ConfigManager
    participant FileSystem

    User->>MCPManager: load_settings()
    MCPManager->>FileSystem: Verificar se settings.json existe
    
    alt Arquivo não existe ou está corrompido
        MCPManager->>MCPManager: _get_auth_type()
        MCPManager->>ConfigManager: get_cli_type()
        ConfigManager-->>MCPManager: "qwen" ou "gemini"
        
        alt CLI é "qwen"
            MCPManager->>MCPManager: Definir selectedType = "qwen-oauth"
        else CLI é "gemini"
            MCPManager->>MCPManager: Definir selectedType = "oauth-personal"
        end
        
        MCPManager->>FileSystem: Criar settings.json com auth type correto
    else Arquivo existe e é válido
        MCPManager->>FileSystem: Carregar settings existente
    end
    
    MCPManager-->>User: Retornar settings

## Proposed File Changes

### src\core\mcp_manager.py(MODIFY)

References: 

- src\core\config_manager.py

Adicionar um método auxiliar privado `_get_auth_type()` que determina o tipo de autenticação baseado no CLI configurado. Este método deve:

1. Tentar obter o `cli_type` do `ConfigManager` (verificando primeiro `self._external_config_manager`, caso contrário criando uma nova instância)
2. Retornar `"qwen-oauth"` se o `cli_type` for `"qwen"`
3. Retornar `"oauth-personal"` se o `cli_type` for `"gemini"` ou em caso de qualquer erro (fallback seguro)
4. Incluir logging apropriado para debug usando `self._logger`

Modificar o método `load_settings()` em dois pontos específicos:

**Ponto 1 (linha ~158):** Na criação do `default_settings` quando o arquivo não existe, substituir o valor hardcoded `"oauth-personal"` no campo `security.auth.selectedType` por uma chamada ao método `_get_auth_type()`.

**Ponto 2 (linha ~245):** Na criação do `default_settings` dentro do bloco de tratamento de `json.JSONDecodeError` (arquivo corrompido), substituir o valor hardcoded `"oauth-personal"` no campo `security.auth.selectedType` por uma chamada ao método `_get_auth_type()`.

Manter toda a estrutura existente dos dicionários `default_settings` intacta, alterando apenas o valor do campo de autenticação. Não modificar nenhuma outra parte da lógica de validação, salvamento ou cache.

### tests\test_mcp_manager_integration.py(MODIFY)

References: 

- src\core\mcp_manager.py(MODIFY)
- src\core\config_manager.py

Adicionar dois novos testes para validar o comportamento diferenciado de autenticação:

**Teste 1:** `test_qwen_auth_type_in_default_settings()`
- Configurar o `ConfigManager` com `cli_type` definido como `"qwen"`
- Criar um diretório temporário `.qwen`
- Instanciar `MCPManager` sem arquivo settings.json pré-existente
- Chamar `load_settings()` para forçar a criação do arquivo padrão
- Verificar que `settings['security']['auth']['selectedType']` é igual a `"qwen-oauth"`
- Verificar que o arquivo foi criado no diretório `.qwen`

**Teste 2:** `test_gemini_auth_type_in_default_settings()`
- Configurar o `ConfigManager` com `cli_type` definido como `"gemini"`
- Criar um diretório temporário `.gemini`
- Instanciar `MCPManager` sem arquivo settings.json pré-existente
- Chamar `load_settings()` para forçar a criação do arquivo padrão
- Verificar que `settings['security']['auth']['selectedType']` é igual a `"oauth-personal"`
- Verificar que o arquivo foi criado no diretório `.gemini`

Nos testes existentes que criam `initial_settings` manualmente (como nas linhas ~47-53 e ~165-171), adicionar comentários explicando que esses valores representam arquivos pré-existentes e por isso mantêm `"oauth-personal"` independentemente do CLI.

### tests\test_cli_switching.py(MODIFY)

References: 

- src\core\mcp_manager.py(MODIFY)
- src\core\config_manager.py

Expandir a cobertura de testes para validar o tipo de autenticação durante a troca de CLI:

**Modificar o teste existente** `test_cli_switching_to_qwen()` (linha ~40):
- Após a verificação do `settings_path` (linha ~54), adicionar validação do tipo de autenticação
- Chamar `manager.load_settings()` para forçar a criação do arquivo padrão se não existir
- Verificar que `settings['security']['auth']['selectedType']` é igual a `"qwen-oauth"`
- Garantir que o teste limpa o ambiente corretamente após a execução

**Adicionar novo teste** `test_cli_switching_to_gemini_auth_type()`:
- Configurar o `ConfigManager` com `user_path` apontando para o diretório temporário de teste
- Configurar o `cli_type` como `"gemini"`
- Usar mock do `ConfigManager` similar ao teste existente
- Instanciar `MCPManager` e carregar settings padrão
- Verificar que o `settings_path` aponta para `.gemini/settings.json`
- Verificar que `settings['security']['auth']['selectedType']` é `"oauth-personal"`

### tests\test_corrupt_file_handling.py(MODIFY)

References: 

- src\core\mcp_manager.py(MODIFY)
- src\core\config_manager.py

Atualizar os testes de tratamento de arquivos corrompidos para validar o tipo de autenticação correto:

**Modificar o teste existente** `test_corrupt_json_handling()`:
- Após verificar que o arquivo corrompido foi renomeado (linha ~57), adicionar validação do tipo de autenticação
- Verificar que `settings['security']['auth']['selectedType']` é `"oauth-personal"` (pois o teste usa `.gemini` por padrão)
- Adicionar comentário explicando que o tipo de autenticação depende do CLI configurado

**Adicionar novo teste** `test_corrupt_json_with_qwen_cli()`:
- Configurar o `ConfigManager` com `cli_type` definido como `"qwen"`
- Criar diretório temporário `.qwen` em vez de `.gemini`
- Criar arquivo `settings.json` corrompido (JSON inválido) no diretório `.qwen`
- Instanciar `MCPManager` usando mock do `ConfigManager` que retorna `"qwen"` para `get_cli_type()`
- Chamar `load_settings()` para acionar o tratamento de arquivo corrompido
- Verificar que o arquivo corrompido foi renomeado com sufixo `.corrupt.*`
- Verificar que o novo settings padrão criado tem `settings['security']['auth']['selectedType']` igual a `"qwen-oauth"`
- Verificar que a estrutura completa do settings está correta (mcpServers, mcp, model, etc.)