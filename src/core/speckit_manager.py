"""
Módulo para gerenciar a instalação do Github Spec-Kit no Windows.
"""

import logging
import subprocess
import os
import ctypes
from ctypes import wintypes
from pathlib import Path
from typing import Optional, Tuple, List


class SpecKitManagerError(Exception):
    """Exceção personalizada para erros do SpecKitManager."""
    pass


class SpecKitManager:
    """
    Gerencia a instalação do Github Spec-Kit no Windows.
    
    Fornece funcionalidades para verificar/instalar o UV, instalar o Spec-Kit via 
    uv tool install, obter o caminho do bin do UV, e adicionar esse caminho ao PATH 
    do Windows modificando o registro.
    """
    
    def __init__(self):
        """
        Inicializa o SpecKitManager.
        
        Raises:
            SpecKitManagerError: Se o sistema operacional não for Windows.
        """
        self._logger = logging.getLogger(__name__)
        
        # Verificar se está rodando no Windows
        if os.name != 'nt':
            raise SpecKitManagerError("Este módulo é específico para Windows e não pode ser usado em outros sistemas operacionais")
        
        self._logger.debug("SpecKitManager inicializado para Windows")
    
    def is_admin(self) -> bool:
        """
        Verifica se o processo atual está executando com privilégios de administrador.
        
        Returns:
            True se estiver executando como administrador, False caso contrário.
        """
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception as e:
            self._logger.error(f"Erro ao verificar privilégios de administrador: {e}")
            return False
    
    def check_uv_installed(self) -> Tuple[bool, Optional[str]]:
        """
        Verifica se o UV está instalado no sistema.
        
        Returns:
            Tupla (True, versão) se instalado, (False, None) caso contrário.
        """
        try:
            result = subprocess.run(['uv', '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip()
                self._logger.info(f"UV está instalado, versão: {version}")
                return True, version
            else:
                self._logger.info("UV não está instalado")
                return False, None
        except FileNotFoundError:
            self._logger.info("UV não está instalado (comando não encontrado)")
            return False, None
        except subprocess.TimeoutExpired:
            self._logger.warning("Timeout ao verificar instalação do UV")
            return False, None
        except Exception as e:
            self._logger.error(f"Erro ao verificar instalação do UV: {e}")
            return False, None
    
    def install_uv(self, log_callback=None) -> bool:
        """
        Instala o UV usando o script PowerShell oficial.
        
        Args:
            log_callback: Função callback para log em tempo real (opcional)
            
        Returns:
            True se a instalação for bem-sucedida.
            
        Raises:
            SpecKitManagerError: Se ocorrer erro durante a instalação.
        """
        import time
        
        try:
            self._logger.info("Iniciando instalação do UV...")
            if log_callback:
                log_callback("Iniciando instalação do UV...")
            
            # Comando PowerShell para instalar o UV
            command = 'powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"'
            
            # Usar subprocess.Popen para log em tempo real
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True
            )
            
            # Definir timeout de 5 minutos (300 segundos)
            timeout_seconds = 300
            start_time = time.time()
            
            # Ler stdout em tempo real com controle de timeout
            output_lines = []
            while True:
                # Verificar timeout
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout_seconds:
                    process.terminate()
                    error_msg = f"Timeout de {timeout_seconds//60} minutos excedido durante a instalação do UV"
                    self._logger.error(error_msg)
                    if log_callback:
                        log_callback(f"Erro: {error_msg}")
                    raise SpecKitManagerError(error_msg)
                
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    line = line.strip()
                    output_lines.append(line)
                    if log_callback:
                        log_callback(line)
            
            # Verificar resultado
            if process.returncode == 0:
                self._logger.info("UV instalado com sucesso")
                if log_callback:
                    log_callback("UV instalado com sucesso")
                
                # Atualizar o PATH do processo atual para que o UV seja encontrado imediatamente
                try:
                    # Obter o caminho padrão do bin do UV
                    uv_bin_path = str(Path.home() / '.local' / 'bin')
                    self._logger.debug(f"Verificando se o caminho do UV bin existe: {uv_bin_path}")
                    
                    # Usar o helper para adicionar o caminho ao PATH do processo
                    if self.__add_to_process_path_if_missing(uv_bin_path, insert_at_beginning=True):
                        self._logger.info("PATH do processo atualizado. UV agora está disponível nesta sessão.")
                        if log_callback:
                            log_callback("PATH do processo atualizado. UV agora está disponível nesta sessão.")
                    else:
                        self._logger.warning(f"Caminho do UV bin não encontrado ou não foi possível adicioná-lo ao PATH: {uv_bin_path}")
                        if log_callback:
                            log_callback(f"Aviso: Caminho do UV bin não encontrado ou não foi possível adicioná-lo ao PATH: {uv_bin_path}")
                
                except Exception as e:
                    # Erros na atualização do PATH não devem interromper o fluxo
                    self._logger.warning(f"Não foi possível atualizar o PATH do processo: {e}")
                    if log_callback:
                        log_callback(f"Aviso: Não foi possível atualizar o PATH do processo: {e}")
                
                return True
            else:
                error_msg = f"Falha na instalação do UV (código {process.returncode})"
                if output_lines:
                    error_msg += f": {' '.join(output_lines[-5:])}"  # Últimas 5 linhas
                self._logger.error(error_msg)
                if log_callback:
                    log_callback(f"Erro: {error_msg}")
                raise SpecKitManagerError(error_msg)
                
        except Exception as e:
            error_msg = f"Erro ao instalar UV: {e}"
            self._logger.error(error_msg)
            if log_callback:
                log_callback(f"Erro: {error_msg}")
            raise SpecKitManagerError(error_msg)
    
    def get_uv_bin_path(self) -> Optional[str]:
        """
        Obtém o caminho do diretório de binários do UV.
        
        Returns:
            O caminho do diretório de binários do UV ou None se não for possível determinar.
        """
        try:
            # Tentar obter o caminho usando o comando uv tool dir --bin
            result = subprocess.run(
                ['uv', 'tool', 'dir', '--bin'],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            
            # Com check=True, não é necessário verificar returncode
            bin_path = result.stdout.strip()
            if bin_path and Path(bin_path).exists():
                self._logger.info(f"Caminho do binário do UV: {bin_path}")
                return bin_path
            
            self._logger.warning("Caminho retornado pelo UV não existe ou está vazio")
            
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            self._logger.warning(f"Erro ao obter caminho do binário do UV: {e}")
        except Exception as e:
            self._logger.error(f"Erro inesperado ao obter caminho do binário do UV: {e}")
        
        # Tentar o caminho padrão como fallback
        default_path = Path.home() / '.local' / 'bin'
        if default_path.exists():
            self._logger.info(f"Usando caminho padrão do UV como fallback: {default_path}")
            return str(default_path)
        
        self._logger.warning("Não foi possível determinar o caminho do binário do UV")
        return None
    
    def install_speckit(self, log_callback=None) -> bool:
        """
        Instala o Spec-Kit usando o UV.
        
        Args:
            log_callback: Função callback para log em tempo real (opcional)
            
        Returns:
            True se a instalação for bem-sucedida.
            
        Raises:
            SpecKitManagerError: Se o UV não estiver instalado ou ocorrer erro durante a instalação.
        """
        import time
        
        # Verificar se o UV está instalado
        uv_installed, uv_version = self.check_uv_installed()
        if not uv_installed:
            raise SpecKitManagerError("UV não está instalado. Instale o UV antes de continuar.")
        
        try:
            self._logger.info("Iniciando instalação do Spec-Kit...")
            if log_callback:
                log_callback("Iniciando instalação do Spec-Kit...")
            
            # Comando para instalar o Spec-Kit
            process = subprocess.Popen(
                ['uv', 'tool', 'install', 'specify-cli', '--from', 'git+https://github.com/github/spec-kit.git'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True
            )
            
            # Definir timeout de 10 minutos (600 segundos)
            timeout_seconds = 600
            start_time = time.time()
            
            # Ler stdout em tempo real com controle de timeout
            output_lines = []
            while True:
                # Verificar timeout
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout_seconds:
                    process.terminate()
                    error_msg = f"Timeout de {timeout_seconds//60} minutos excedido durante a instalação do Spec-Kit"
                    self._logger.error(error_msg)
                    if log_callback:
                        log_callback(f"Erro: {error_msg}")
                    raise SpecKitManagerError(error_msg)
                
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    line = line.strip()
                    output_lines.append(line)
                    if log_callback:
                        log_callback(line)
            
            # Verificar resultado
            if process.returncode == 0:
                self._logger.info("Spec-Kit instalado com sucesso")
                if log_callback:
                    log_callback("Spec-Kit instalado com sucesso")
                return True
            else:
                error_msg = f"Falha na instalação do Spec-Kit (código {process.returncode})"
                if output_lines:
                    error_msg += f": {' '.join(output_lines[-5:])}"  # Últimas 5 linhas
                self._logger.error(error_msg)
                if log_callback:
                    log_callback(f"Erro: {error_msg}")
                raise SpecKitManagerError(error_msg)
                
        except Exception as e:
            error_msg = f"Erro ao instalar Spec-Kit: {e}"
            self._logger.error(error_msg)
            if log_callback:
                log_callback(f"Erro: {error_msg}")
            raise SpecKitManagerError(error_msg)
    
    def add_to_windows_path(self, path: str, log_callback=None) -> bool:
        """
        Adiciona um caminho à variável de ambiente PATH do Windows.
        
        Args:
            path: O caminho a ser adicionado ao PATH.
            log_callback: Função callback para log em tempo real (opcional)
            
        Returns:
            True se o caminho foi adicionado com sucesso.
            
        Raises:
            SpecKitManagerError: Se o caminho for inválido ou ocorrer erro ao modificar o registro.
        """
        # Importação condicional do winreg apenas para Windows
        import winreg
        
        # Validar o parâmetro path
        if not path or not isinstance(path, str):
            raise SpecKitManagerError("O caminho deve ser uma string não vazia")
        
        # Validar que o caminho existe
        path_obj = Path(path)
        if not path_obj.exists():
            raise SpecKitManagerError(f"O caminho não existe: {path}")
        
        try:
            if log_callback:
                log_callback(f"Verificando se o caminho já existe no PATH: {path}")
            
            # Abrir a chave do registro para o usuário atual
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                "Environment",
                0,
                winreg.KEY_READ | winreg.KEY_WRITE
            ) as key:
                # Ler o valor atual do PATH
                try:
                    current_path, _ = winreg.QueryValueEx(key, "Path")
                except FileNotFoundError:
                    # Se a chave Path não existir (primeira execução), usar string vazia
                    current_path = ""
                
                # Normalizar o caminho para comparação
                normalized_path = self._normalize_path(path)
                
                # Dividir o PATH atual em componentes
                path_components = current_path.split(';') if current_path else []
                
                # Verificar se o caminho já está no PATH
                for component in path_components:
                    if component and self._normalize_path(component) == normalized_path:
                        self._logger.info(f"O caminho já está no PATH: {path}")
                        if log_callback:
                            log_callback(f"O caminho já está no PATH: {path}")
                        return True
                
                if log_callback:
                    log_callback("Adicionando caminho ao registro do Windows...")
                
                # Adicionar o novo caminho ao início da lista
                new_path_components = [path] + path_components
                new_path = ';'.join(new_path_components)
                
                # Escrever o novo valor no registro
                winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                
                if log_callback:
                    log_callback("Notificando o sistema sobre a mudança...")
                
                # Fazer broadcast da mudança para notificar o sistema
                self._broadcast_env_change()
                
                # Usar o helper para atualizar o PATH no processo atual
                self.__add_to_process_path_if_missing(path, insert_at_beginning=True)
                
                self._logger.info(f"Caminho adicionado ao PATH com sucesso: {path}")
                self._logger.info("Nota: Novos terminais precisarão ser abertos para ver a mudança")
                if log_callback:
                    log_callback(f"Caminho adicionado ao PATH com sucesso: {path}")
                    log_callback("Nota: Novos terminais precisarão ser abertos para ver a mudança")
                return True
                
        except PermissionError as e:
            error_msg = f"Sem permissão para modificar o registro: {e}"
            self._logger.error(error_msg)
            if log_callback:
                log_callback(f"Erro de permissão: {error_msg}")
            raise SpecKitManagerError(error_msg)
        except OSError as e:
            error_msg = f"Erro ao acessar o registro: {e}"
            self._logger.error(error_msg)
            if log_callback:
                log_callback(f"Erro ao acessar o registro: {error_msg}")
            raise SpecKitManagerError(error_msg)
        except Exception as e:
            error_msg = f"Erro ao adicionar caminho ao PATH: {e}"
            self._logger.error(error_msg)
            if log_callback:
                log_callback(f"Erro: {error_msg}")
            raise SpecKitManagerError(error_msg)
    
    def _broadcast_env_change(self) -> None:
        """
        Método privado para fazer broadcast de mudanças de ambiente para o sistema.
        
        Envia uma mensagem WM_SETTINGCHANGE para notificar todas as janelas sobre
        a mudança nas variáveis de ambiente.
        """
        try:
            # Constantes para a mensagem
            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x001A
            SMTO_ABORTIFHUNG = 0x0002
            
            # Criar tipos explícitos para os parâmetros
            env_str = ctypes.c_wchar_p("Environment")
            result = ctypes.c_ulong(0)
            
            # Enviar a mensagem
            ctypes.windll.user32.SendMessageTimeoutW(
                HWND_BROADCAST,
                WM_SETTINGCHANGE,
                0,
                env_str,  # lParam usando tipo explícito
                SMTO_ABORTIFHUNG,
                5000,  # 5 segundos de timeout
                ctypes.byref(result)  # Último argumento usando referência
            )
            
            if result:
                self._logger.debug("Broadcast de mudança de ambiente enviado com sucesso")
            else:
                self._logger.warning("Falha ao enviar broadcast de mudança de ambiente")
                
        except Exception as e:
            self._logger.warning(f"Erro ao fazer broadcast de mudança de ambiente: {e}")
            # Não é crítico, então não lança exceção
    
    def __add_to_process_path_if_missing(self, path: str, insert_at_beginning: bool = True) -> bool:
        """
        Método privado para adicionar um caminho ao PATH do processo atual se não estiver presente.
        
        Args:
            path: O caminho a ser adicionado ao PATH.
            insert_at_beginning: Se True, insere no início do PATH; se False, insere no final.
            
        Returns:
            True se o caminho foi adicionado ou já estava presente, False caso contrário.
        """
        try:
            # Verificar se o caminho existe
            if not Path(path).exists():
                self._logger.warning(f"Caminho não encontrado: {path}")
                return False
            
            # Obter o PATH atual (tentar ambas as variantes do Windows)
            current_path = os.environ.get('PATH', '') or os.environ.get('Path', '')
            
            # Dividir o PATH atual em componentes
            path_components = current_path.split(os.pathsep) if current_path else []
            
            # Normalizar o caminho para comparação
            normalized_path = self._normalize_path(path)
            
            # Verificar se o caminho já está no PATH
            path_exists = False
            for component in path_components:
                if component and self._normalize_path(component) == normalized_path:
                    path_exists = True
                    break
            
            if not path_exists:
                # Adicionar o caminho ao PATH (no início ou no final conforme especificado)
                if insert_at_beginning:
                    new_path = os.pathsep.join([path] + path_components)
                else:
                    new_path = os.pathsep.join(path_components + [path])
                
                # Atualizar ambas as variantes do PATH para compatibilidade com Windows
                os.environ['PATH'] = new_path
                os.environ['Path'] = new_path
                
                self._logger.info(f"Caminho adicionado ao PATH do processo: {path}")
                return True
            else:
                self._logger.debug(f"Caminho já está no PATH do processo: {path}")
                return True
                
        except Exception as e:
            self._logger.error(f"Erro ao adicionar caminho ao PATH do processo: {e}")
            return False
    
    def _normalize_path(self, path: str) -> str:
        """
        Método privado para normalizar caminhos para comparação.
        
        Args:
            path: O caminho a ser normalizado.
            
        Returns:
            O caminho normalizado.
        """
        # Expandir variáveis de ambiente
        expanded = os.path.expandvars(path)
        
        # Normalizar o caminho
        normalized = os.path.normpath(expanded)
        
        # Converter para case-insensitive
        case_normalized = os.path.normcase(normalized)
        
        return case_normalized