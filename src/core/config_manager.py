"""
Módulo para gerenciar configurações do usuário, especificamente o caminho base do usuário.
"""

import json
import logging
import os
import stat
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigManagerError(Exception):
    """Exceção personalizada para erros do ConfigManager."""
    pass


class ConfigManager:
    """
    Gerencia configurações do usuário, persistindo-as em um arquivo JSON.
    
    Armazena e recupera o caminho base do usuário, validando caminhos e
    tratando erros de forma adequada.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa o ConfigManager.
        
        Args:
            config_path: Caminho opcional para o arquivo de configuração.
                        Se não fornecido, usa 'mcp_config.json' no mesmo
                        diretório do script.
                        
        Nota:
            O caminho de configuração padrão é o diretório do script, que pode
            ser somente leitura em alguns ambientes. Se ocorrer erro de escrita,
            o sistema tentará usar o diretório home do usuário como fallback.
            No Windows, também considera AppData como opção de fallback.
        """
        if config_path is None:
            # Usa o mesmo diretório do script
            script_dir = Path(__file__).parent
            self.config_path = script_dir / "mcp_config.json"
            
            # No Windows, prioriza AppData/Roaming como fallback
            if os.name == 'nt':
                appdata_path = Path(os.environ.get('APPDATA', '')) / 'MCPManager'
                self._fallback_path = appdata_path / "mcp_config.json"
            else:
                # Armazena o caminho de fallback para o diretório home
                self._fallback_path = Path.home() / "mcp_config.json"
        else:
            self.config_path = Path(config_path)
            self._fallback_path = None
        
        self._logger = logging.getLogger(__name__)
    
    def get_user_path(self) -> Optional[str]:
        """
        Recupera o caminho base do usuário armazenado na configuração.
        
        Returns:
            O caminho base do usuário se existir na configuração e for válido, None caso contrário.
        """
        try:
            config = self._load_config()
            user_base_path = config.get("user_base_path")
            
            # Valida se o valor é uma string e aponta para um diretório existente
            if user_base_path is not None and isinstance(user_base_path, str) and user_base_path.strip():
                path_obj = Path(user_base_path)
                if path_obj.exists() and path_obj.is_dir():
                    return user_base_path
                else:
                    self._logger.warning(f"O caminho armazenado não é um diretório válido: {user_base_path}")
                    return None
            else:
                self._logger.warning("O caminho do usuário na configuração não é uma string válida ou está vazio")
                return None
        except Exception as e:
            self._logger.error(f"Erro ao recuperar caminho do usuário: {e}")
            return None
    
    def set_user_path(self, user_path: str) -> bool:
        """
        Define o caminho base do usuário na configuração.
        
        Args:
            user_path: O caminho base do usuário a ser armazenado.
            
        Returns:
            True se o caminho foi definido com sucesso.
            
        Raises:
            ConfigManagerError: Se o caminho for inválido ou ocorrer erro ao salvar.
        """
        if not user_path or not isinstance(user_path, str):
            raise ConfigManagerError("Caminho do usuário deve ser uma string não vazia")
        
        # Validação do caminho
        path_obj = Path(user_path)
        if not path_obj.exists():
            raise ConfigManagerError(f"O caminho não existe: {user_path}")
        
        if not path_obj.is_dir():
            raise ConfigManagerError(f"O caminho não é um diretório: {user_path}")
        
        try:
            # Carrega configuração existente ou cria nova
            config = self._load_config()
            
            # Normaliza o caminho para usar barras forward
            normalized_path = path_obj.as_posix()
            config["user_base_path"] = normalized_path
            
            # Salva a configuração
            self._save_config(config)
            
            self._logger.info(f"Caminho do usuário definido com sucesso: {normalized_path}")
            return True
            
        except PermissionError as e:
            error_msg = f"Sem permissão para acessar o arquivo de configuração: {e}"
            self._logger.error(error_msg)
            raise ConfigManagerError(error_msg)
        except Exception as e:
            error_msg = f"Erro ao definir caminho do usuário: {e}"
            self._logger.error(error_msg)
            raise ConfigManagerError(error_msg)

    def get_cli_type(self) -> str:
        """
        Recupera o tipo de CLI (gemini ou qwen) armazenado na configuração.

        Returns:
            O tipo de CLI ('gemini' ou 'qwen'). O padrão é 'gemini'.
        """
        try:
            config = self._load_config()
            cli_type = config.get("cli_type", "gemini")

            if cli_type not in ["gemini", "qwen"]:
                self._logger.warning(f"Tipo de CLI inválido '{cli_type}' encontrado. Usando 'gemini' como padrão.")
                return "gemini"

            return cli_type
        except Exception as e:
            self._logger.error(f"Erro ao recuperar tipo de CLI: {e}")
            return "gemini"

    def set_cli_type(self, cli_type: str) -> bool:
        """
        Define o tipo de CLI na configuração.

        Args:
            cli_type: O tipo de CLI a ser armazenado ('gemini' ou 'qwen').

        Returns:
            True se o tipo de CLI foi definido com sucesso.

        Raises:
            ConfigManagerError: Se o tipo de CLI for inválido ou ocorrer erro ao salvar.
        """
        if cli_type not in ["gemini", "qwen"]:
            raise ConfigManagerError("Tipo de CLI deve ser 'gemini' ou 'qwen'")

        try:
            # Carrega configuração existente ou cria nova
            config = self._load_config()

            config["cli_type"] = cli_type

            # Salva a configuração
            self._save_config(config)

            self._logger.info(f"Tipo de CLI definido com sucesso: {cli_type}")
            return True

        except Exception as e:
            error_msg = f"Erro ao definir o tipo de CLI: {e}"
            self._logger.error(error_msg)
            raise ConfigManagerError(error_msg)
    
    def has_config(self) -> bool:
        """
        Verifica se existe uma configuração válida.
        
        Returns:
            True se o arquivo de configuração existe e contém a chave 'user_base_path'
            com um valor não vazio que aponta para um diretório existente.
        """
        try:
            config = self._load_config()
            user_base_path = config.get("user_base_path")
            
            # Verifica se o caminho é uma string não vazia e aponta para um diretório existente
            if user_base_path is not None and isinstance(user_base_path, str) and user_base_path.strip():
                path_obj = Path(user_base_path)
                return path_obj.exists() and path_obj.is_dir()
            
            return False
        except Exception:
            return False
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Carrega a configuração do arquivo JSON.
        
        Returns:
            Dicionário com a configuração carregada ou dicionário vazio se não existir.
            
        Nota:
            Se o arquivo principal não puder ser lido, tentará usar o caminho
            alternativo (_fallback_path) se disponível.
        """
        # Verifica se config_path é válido antes de tentar acessar
        if self.config_path is None or not self.config_path.exists():
            # try fallback if available
            if hasattr(self, '_fallback_path') and self._fallback_path is not None and self._fallback_path.exists():
                try:
                    self._logger.info(f"Arquivo de configuração principal não encontrado em {self.config_path}, tentando fallback")
                    with open(self._fallback_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # if successful, also update config_path to fallback for this instance
                        self.config_path = self._fallback_path
                        self._logger.info(f"Usando arquivo de configuração fallback: {self._fallback_path}")
                        return data
                except Exception as e:
                    self._logger.warning(f"Falha ao ler arquivo de configuração fallback {self._fallback_path}: {e}")
                    return {}
            self._logger.info(f"Arquivo de configuração não encontrado em {self.config_path} e sem fallback disponível")
            return {}

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._logger.debug(f"Configuração carregada com sucesso de: {self.config_path}")
                return data
        except (json.JSONDecodeError, PermissionError) as e:
            self._logger.warning(f"Falha ao ler arquivo de configuração principal {self.config_path}: {e}")
            # try fallback
            if hasattr(self, '_fallback_path') and self._fallback_path is not None and self._fallback_path.exists():
                try:
                    self._logger.info(f"Tentando arquivo de configuração fallback: {self._fallback_path}")
                    with open(self._fallback_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.config_path = self._fallback_path
                        self._logger.info(f"Usando arquivo de configuração fallback: {self._fallback_path}")
                        return data
                except Exception as e:
                    self._logger.warning(f"Falha ao ler arquivo de configuração fallback {self._fallback_path}: {e}")
                    return {}
            self._logger.warning(f"Falha ao ler configuração e sem fallback disponível: {e}")
            return {}
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """
        Salva a configuração no arquivo JSON.
        
        Args:
            config: Dicionário de configuração a ser salvo.
            
        Raises:
            ConfigManagerError: Se ocorrer erro ao salvar o arquivo.
            
        Nota:
            Se o diretório padrão for somente leitura, tentará usar o diretório
            home do usuário como caminho alternativo.
        """
        import tempfile
        
        try:
            # Tenta salvar no caminho principal primeiro
            try:
                # Verifica se config_path é válido antes de tentar acessar
                if self.config_path is None:
                    raise ConfigManagerError("Caminho de configuração não está definido")
                
                # Verifica permissões de escrita no diretório (especialmente importante no Windows)
                # Verificação conservadora primeiro (não invasiva)
                if not self._check_write_permission(self.config_path.parent, aggressive_check=False):
                    # Só realiza tentativa de escrita real (agressiva) se explicitamente necessário
                    if not self._check_write_permission(self.config_path.parent, aggressive_check=True):
                        raise PermissionError(f"Sem permissão de escrita no diretório: {self.config_path.parent}")
                
                # Garante que o diretório pai exista
                self.config_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Escreve atomicamente: escreve JSON em um arquivo temporário no diretório do destino,
                # e então substitui o arquivo de destino
                with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                                                dir=self.config_path.parent,
                                                suffix='.json', delete=False) as temp_file:
                    json.dump(config, temp_file, indent=2, ensure_ascii=False)
                    temp_name = temp_file.name
                
                # Substitui o arquivo alvo pelo temporário
                Path(temp_name).replace(self.config_path)
                    
                self._logger.info(f"Configuração salva em: {self.config_path}")
                return
                
            except PermissionError:
                # Se o caminho principal falhar por permissão, tenta o fallback
                if self._fallback_path is not None:
                    self._logger.warning(f"Sem permissão para escrever em {self.config_path}, tentando fallback")
                    
                    # Verifica permissões no diretório de fallback também
                    # Verificação conservadora primeiro (não invasiva)
                    if not self._check_write_permission(self._fallback_path.parent, aggressive_check=False):
                        # Só realiza tentativa de escrita real (agressiva) se explicitamente necessário
                        if not self._check_write_permission(self._fallback_path.parent, aggressive_check=True):
                            raise PermissionError(f"Sem permissão de escrita no diretório de fallback: {self._fallback_path.parent}")
                    
                    self._fallback_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Escreve atomicamente no caminho de fallback também
                    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                                                    dir=self._fallback_path.parent,
                                                    suffix='.json', delete=False) as temp_file:
                        json.dump(config, temp_file, indent=2, ensure_ascii=False)
                        temp_name = temp_file.name
                    
                    # Substitui o arquivo alvo pelo temporário
                    Path(temp_name).replace(self._fallback_path)
                        
                    self._logger.info(f"Configuração salva no caminho alternativo: {self._fallback_path}")
                    # Atualiza o caminho de configuração para o fallback
                    self.config_path = self._fallback_path
                    return
                else:
                    # Se não há fallback, propaga o erro
                    raise
                    
        except PermissionError as e:
            raise ConfigManagerError(f"Sem permissão para escrever no arquivo de configuração: {e}")
        except Exception as e:
            raise ConfigManagerError(f"Erro ao salvar configuração: {e}")
    
    def _check_write_permission(self, directory: Path, aggressive_check: bool = False) -> bool:
        """
        Verifica permissão de escrita de forma conservadora primeiro e só realiza
        tentativa de escrita real quando explicitamente solicitado.
        
        Comportamento:
        - Se o diretório existir, tenta primeiro os.access(directory, os.W_OK).
        - Se o resultado for False ou inconclusivo (por exemplo, diretório inexistente),
          somente fará uma tentativa de escrita real quando aggressive_check=True.
        - Quando aggressive_check=True, a tentativa é controlada usando artefatos
          temporários evita criar o diretório alvo inexistente.
        
        Args:
            directory: Diretório a verificar.
            aggressive_check: Quando True, faz tentativa de escrita real (controlada).
            
        Returns:
            True se houver evidência confiável de permissão de escrita; False caso contrário.
        """
        try:
            # Caso o diretório exista: verificação não invasiva com os.access
            if directory.exists():
                if os.access(str(directory), os.W_OK):
                    return True
                if not aggressive_check:
                    return False
                # Verificação agressiva controlada: cria arquivo temporário dentro do diretório
                import tempfile
                try:
                    with tempfile.NamedTemporaryFile(
                        dir=directory,
                        prefix=".perm_test_",
                        suffix=".tmp",
                        delete=True
                    ) as tf:
                        tf.write(b"ok")
                        tf.flush()
                    return True
                except (PermissionError, OSError) as e:
                    self._logger.debug(f"Tentativa agressiva falhou em {directory}: {e}")
                    return False
            
            # Diretório não existe: sem tentativa de criação quando em modo conservador
            if not aggressive_check:
                self._logger.debug(f"Diretório {directory} não existe; verificação conservadora retorna False sem criar artefatos.")
                return False
            
            # Agressivo: verifica capacidade de criar dentro do diretório pai (sem criar o alvo)
            parent = directory.parent if directory.parent != directory else Path.cwd()
            if not parent.exists():
                # Não criamos ancestrais durante a verificação
                return False
            
            # Mesmo que os.access no pai falhe, confirmamos com tentativa controlada
            import tempfile
            try:
                with tempfile.TemporaryDirectory(prefix=".perm_test_", dir=parent) as tmp_dir:
                    test_path = Path(tmp_dir) / ".t.tmp"
                    with open(test_path, "w", encoding="utf-8") as fh:
                        fh.write("ok")
                return True
            except (PermissionError, OSError) as e:
                self._logger.debug(f"Tentativa agressiva no pai {parent} falhou: {e}")
                return False
        except Exception as e:
            self._logger.debug(f"Erro ao verificar permissão em {directory}: {e}")
            return False