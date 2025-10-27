"""
MCP Manager Module

A Python module for managing MCP (Model Context Protocol) server configurations
in the settings.json file. Provides CRUD operations and validation for MCP server configurations.
"""

import json
import shutil
import logging
import copy
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import uuid
from tempfile import NamedTemporaryFile
from .config_manager import ConfigManager, ConfigManagerError


MCP_TEMPLATES = {
    "context7": {
        "name": "context7",
        "command": "npx",
        "args": ["-y", "@upstash/context7-mcp"],
        "description": "Context7 MCP for enhanced context management"
    },
    "chrome-devtools": {
        "name": "chrome-devtools",
        "command": "npx",
        "args": ["-y", "chrome-devtools-mcp@latest"],
        "description": "Chrome DevTools MCP for browser automation"
    },
    "excel": {
        "name": "excel",
        "command": "uvx",
        "args": ["excel-mcp-server", "stdio"],
        "description": "Excel MCP for spreadsheet manipulation"
    }
}


class MCPManagerError(Exception):
    """Custom exception for MCP Manager errors."""
    pass


class MCPManager:
    """
    A class for managing MCP server configurations in settings.json.

    Provides functionality to add, remove, update, and toggle MCP servers,
    with data validation.
    """

    def __init__(self, settings_path: Optional[str] = None, user_base_path: Optional[str] = None):
        """
        Initialize the MCP Manager.

        Args:
            settings_path: Optional path to the settings.json file.
                           If provided, takes highest priority and will be used directly.
            user_base_path: Optional base path of the user (e.g., 'C:/Users/TI00').
                            If provided, settings_path will be constructed as:
                            user_base_path / ".gemini" / "settings.json"
                            Takes priority over ConfigManager.
        
        Priority order:
            1. settings_path (if provided)
            2. user_base_path (if provided)
            3. ConfigManager.get_user_path() (if configured)
            4. Path.home() (default fallback)
        """
        self._logger = logging.getLogger(__name__)
        self._settings_cache = None

        if settings_path is not None:
            self.settings_path = Path(settings_path)
            self._logger.info(f"Using provided settings path: {self.settings_path}")
            return

        try:
            config_manager = ConfigManager()
            cli_type = config_manager.get_cli_type()
            cli_dir = f".{cli_type}"

            if user_base_path is not None:
                base = self._validate_and_normalize_user_path(user_base_path)
                self.settings_path = base / cli_dir / "settings.json"
                self._logger.info(f"Using settings path from user_base_path: {self.settings_path}")
                return

            user_path = config_manager.get_user_path()

            if user_path:
                try:
                    normalized_path = Path(user_path).expanduser().resolve()
                except (OSError, PermissionError) as e:
                    self._logger.debug(f"Path.resolve() failed, falling back to expanduser(): {e}")
                    normalized_path = Path(user_path).expanduser()
                self.settings_path = normalized_path / cli_dir / "settings.json"
                self._logger.info(f"Using settings path from config: {self.settings_path}")
            else:
                self.settings_path = Path.home() / cli_dir / "settings.json"
                self._logger.warning(f"No user path configured, using default: {self.settings_path}")
                self._logger.info("Execute `python setup_user_path.py` para configurar o caminho do usuário")
        except ConfigManagerError as e:
            cli_dir = ".gemini"  # Fallback
            self.settings_path = Path.home() / cli_dir / "settings.json"
            self._logger.warning(f"Error loading config ({e}), using default path: {self.settings_path}")
            self._logger.info("Execute `python setup_user_path.py` para configurar o caminho do usuário")

    def __repr__(self) -> str:
        return f"MCPManager(settings_path='{self.settings_path}')"

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self._settings_cache = None

    def load_settings(self) -> Dict[str, Any]:
        """
        Load settings from the JSON file.

        Returns:
            Dictionary containing the settings (deep copy to prevent external mutation)

        Raises:
            MCPManagerError: If file cannot be read or parsed
        """
        if self._settings_cache is not None:
            return copy.deepcopy(self._settings_cache)

        try:
            if not self.settings_path.exists():
                self._logger.info(f"Settings file not found, creating default structure")
                default_settings = {
                    "ide": {"hasSeenNudge": True, "enabled": True},
                    "mcp": {"allowed": []},
                    "mcpServers": {},
                    "security": {"auth": {"selectedType": "oauth-personal"}},
                    "ui": {"theme": "Default"}
                }
                self._settings_cache = default_settings
                return copy.deepcopy(self._settings_cache)

            with open(self.settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)

            # Validate required structure with strong type checking
            # mcp
            if not isinstance(settings.get('mcp'), dict):
                settings['mcp'] = {'allowed': []}
            if not isinstance(settings['mcp'].get('allowed'), list):
                settings['mcp']['allowed'] = []
            # mcpServers
            if not isinstance(settings.get('mcpServers'), dict):
                settings['mcpServers'] = {}
            else:
                for name, cfg in list(settings['mcpServers'].items()):
                    if not isinstance(cfg, dict):
                        del settings['mcpServers'][name]
                        continue
                    cmd = cfg.get('command')
                    args = cfg.get('args', [])
                    if not isinstance(cmd, str) or not cmd:
                        del settings['mcpServers'][name]
                        continue
                    if not isinstance(args, list) or any(not isinstance(a, str) for a in args):
                        cfg['args'] = [str(a) for a in args] if isinstance(args, list) else []

            self._settings_cache = settings
            return copy.deepcopy(self._settings_cache)

        except json.JSONDecodeError as e:
            # Handle corrupt JSON file by renaming it and creating default structure
            # Try multiple names with incremental/UUID suffix in case of race conditions
            max_attempts = 5
            base_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            for attempt in range(max_attempts):
                try:
                    if attempt == 0:
                        # First attempt: use timestamp only
                        suffix = base_timestamp
                    else:
                        # Subsequent attempts: add UUID for uniqueness
                        suffix = f"{base_timestamp}_{uuid.uuid4().hex[:8]}"
                    
                    corrupt_path = self.settings_path.with_name(f"{self.settings_path.name}.corrupt.{suffix}")
                    
                    self._logger.debug(f"Attempt {attempt + 1}/{max_attempts}: Renaming corrupt file to: {corrupt_path}")
                    shutil.move(str(self.settings_path), str(corrupt_path))
                    
                    self._logger.warning(f"Corrupt JSON file renamed to: {corrupt_path}")
                    self._logger.info(f"Creating default settings structure due to corrupt JSON: {e}")
                    
                    # Create default settings structure
                    default_settings = {
                        "ide": {"hasSeenNudge": True, "enabled": True},
                        "mcp": {"allowed": []},
                        "mcpServers": {},
                        "security": {"auth": {"selectedType": "oauth-personal"}},
                        "ui": {"theme": "Default"}
                    }
                    
                    self._settings_cache = default_settings
                    return copy.deepcopy(self._settings_cache)
                    
                except (OSError, PermissionError, shutil.Error) as rename_error:
                    self._logger.warning(f"Attempt {attempt + 1}/{max_attempts} failed to rename corrupt file: {rename_error}")
                    if attempt == max_attempts - 1:
                        # Last attempt failed, raise original error
                        self._logger.error(f"All {max_attempts} attempts to rename corrupt file failed")
                        raise MCPManagerError(f"Invalid JSON in settings file: {e}")
            
            # This should never be reached, but added for type safety
            raise MCPManagerError(f"Invalid JSON in settings file: {e}")
        except PermissionError as e:
            raise MCPManagerError(f"Permission denied reading settings file: {e}")
        except Exception as e:
            raise MCPManagerError(f"Error loading settings: {e}")

    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Save settings to the JSON file.

        Args:
            settings: Dictionary containing the settings to save

        Returns:
            True if successful

        Raises:
            MCPManagerError: If file cannot be written
        """
        try:
            # Validate required structure with defensive checks
            if 'mcp' not in settings:
                raise MCPManagerError("Missing required 'mcp' key in settings")
            if 'mcpServers' not in settings:
                raise MCPManagerError("Missing required 'mcpServers' key in settings")
            if not isinstance(settings['mcp'], dict):
                raise MCPManagerError("'mcp' must be a dictionary")
            if not isinstance(settings['mcpServers'], dict):
                raise MCPManagerError("'mcpServers' must be a dictionary")
            if not isinstance(settings['mcp'].get('allowed'), list):
                raise MCPManagerError("'mcp.allowed' must be a list")

            # Validate mcpServers structure
            for name, cfg in settings['mcpServers'].items():
                if not isinstance(cfg, dict):
                    raise MCPManagerError(f"MCP '{name}' configuration must be a dictionary")
                if not isinstance(cfg.get('command'), str) or not cfg.get('command'):
                    raise MCPManagerError(f"MCP '{name}' must have a non-empty 'command' string")
                if not isinstance(cfg.get('args'), list):
                    raise MCPManagerError(f"MCP '{name}' 'args' must be a list")
                if any(not isinstance(arg, str) for arg in cfg['args']):
                    raise MCPManagerError(f"MCP '{name}' 'args' must contain only strings")

            # Ensure target directory exists
            self.settings_path.parent.mkdir(parents=True, exist_ok=True)

            # Write to temp file in same directory
            with NamedTemporaryFile('w', delete=False, dir=str(self.settings_path.parent), encoding='utf-8') as tf:
                json.dump(settings, tf, indent=2)
                temp_name = tf.name

            # Atomic replace
            Path(temp_name).replace(self.settings_path)

            # Update cache
            self._settings_cache = settings
            self._logger.info("Settings saved successfully")
            return True

        except PermissionError as e:
            raise MCPManagerError(f"Permission denied writing settings file: {e}")
        except IOError as e:
            raise MCPManagerError(f"IO error writing settings file: {e}")
        except Exception as e:
            raise MCPManagerError(f"Error saving settings: {e}")


    def _validate_and_normalize_user_path(self, user_base_path: str) -> Path:
        """
        Validate and normalize a user base path.
        
        Args:
            user_base_path: The user base path to validate (e.g., 'C:/Users/TI00')
        
        Returns:
            Normalized Path object
        
        Raises:
            MCPManagerError: If path is invalid or inaccessible
        """
        if not isinstance(user_base_path, str) or not user_base_path.strip():
            raise MCPManagerError("user_base_path must be a non-empty string")

        raw_path = Path(user_base_path).expanduser()

        try:
            normalized = raw_path.resolve()
        except (OSError, PermissionError) as e:
            self._logger.debug(f"Path.resolve() failed, falling back to expanduser(): {e}")
            normalized = raw_path

        permission_target: Optional[Path]

        if normalized.exists():
            if not normalized.is_dir():
                raise MCPManagerError(f"user_base_path '{normalized}' is not a directory")
            permission_target = normalized
        else:
            self._logger.warning(
                f"user_base_path '{normalized}' does not exist. Directory will be created if needed."
            )
            permission_target = next((parent for parent in normalized.parents if parent.exists()), None)
            if permission_target is None:
                raise MCPManagerError(
                    f"Não foi possível localizar um diretório existente para validar permissões de '{normalized}'. "
                    "Verifique o caminho informado."
                )

        try:
            config_manager = ConfigManager()
            checker = getattr(config_manager, "_check_write_permission", None)
        except Exception as e:
            checker = None
            self._logger.debug(f"Falha ao inicializar verificação de permissão reutilizando ConfigManager: {e}")

        if callable(checker):
            has_permission = checker(permission_target, aggressive_check=False)
            if not has_permission:
                path_for_msg = normalized if normalized.exists() else permission_target
                raise MCPManagerError(
                    f"Sem permissão de escrita para '{path_for_msg}'. "
                    "Ajuste as permissões ou selecione outro caminho e execute `python setup_user_path.py` novamente."
                )
        else:
            self._logger.debug(
                "Não foi possível reutilizar ConfigManager._check_write_permission; pulando verificação de permissão antecipada."
            )

        return normalized

    def get_mcps(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all MCPs with their configuration and enabled status.

        Returns:
            Dictionary with MCP information:
            {
                "mcp_name": {
                    "command": "...",
                    "args": [...],
                    "enabled": True/False
                }
            }
        """
        settings = self.load_settings()
        result = {}

        mcp_servers = settings.get('mcpServers', {})
        allowed_list = settings.get('mcp', {}).get('allowed', [])

        for name, config in mcp_servers.items():
            result[name] = {
                'command': config.get('command', ''),
                'args': config.get('args', []),
                'enabled': name in allowed_list
            }

        return result

    def get_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all available MCP templates.

        Returns:
            Dictionary with template information:
            {
                "template_name": {
                    "name": "...",
                    "command": "...",
                    "args": [...],
                    "description": "..."
                }
            }
        """
        return copy.deepcopy(MCP_TEMPLATES)

    def add_mcp(self, name: str, command: str, args: List[str]) -> bool:
        """
        Add a new MCP server configuration.

        Args:
            name: Name of the MCP server
            command: Command to run the server
            args: List of arguments for the command (must be list of strings)

        Returns:
            True if successful

        Raises:
            MCPManagerError: If MCP already exists or parameters are invalid
        """
        # Validate parameters
        if not name or not isinstance(name, str):
            raise MCPManagerError("MCP name must be a non-empty string")
        if not command or not isinstance(command, str):
            raise MCPManagerError("MCP command must be a non-empty string")
        if not isinstance(args, list):
            raise MCPManagerError("MCP args must be a list")

        # Validate and coerce args elements to strings (consistent with load_settings behavior)
        if any(not isinstance(a, str) for a in args):
            args = [str(a) for a in args]

        settings = self.load_settings()

        # Check if MCP already exists
        if name in settings.get('mcpServers', {}):
            raise MCPManagerError(f"MCP '{name}' already exists")

        # Add new MCP
        settings.setdefault('mcpServers', {})[name] = {
            'command': command,
            'args': args
        }

        # Save settings
        self.save_settings(settings)
        self._logger.info(f"Added MCP '{name}'")
        return True

    def remove_mcp(self, name: str) -> bool:
        """
        Remove an MCP server configuration.

        Args:
            name: Name of the MCP server to remove

        Returns:
            True if successful

        Raises:
            MCPManagerError: If MCP doesn't exist
        """
        settings = self.load_settings()

        # Check if MCP exists
        if name not in settings.get('mcpServers', {}):
            raise MCPManagerError(f"MCP '{name}' not found")

        # Remove from mcpServers
        del settings['mcpServers'][name]

        # Remove from allowed list if present
        allowed_list = settings.setdefault('mcp', {}).setdefault('allowed', [])
        if name in allowed_list:
            allowed_list.remove(name)

        # Save settings
        self.save_settings(settings)
        self._logger.info(f"Removed MCP '{name}'")
        return True

    def toggle_allowed(self, name: str, enabled: Optional[bool] = None) -> bool:
        """
        Toggle or set the allowed status of an MCP server.

        Args:
            name: Name of the MCP server
            enabled: True to enable, False to disable, None to toggle

        Returns:
            New enabled state (True/False)

        Raises:
            MCPManagerError: If MCP doesn't exist
        """
        settings = self.load_settings()

        # Check if MCP exists
        if name not in settings.get('mcpServers', {}):
            raise MCPManagerError(f"MCP '{name}' not found")

        allowed_list = settings.setdefault('mcp', {}).setdefault('allowed', [])
        current_state = name in allowed_list

        # Determine new state
        if enabled is None:
            new_state = not current_state
        else:
            new_state = enabled

        # Update allowed list
        if new_state and not current_state:
            allowed_list.append(name)
        elif not new_state and current_state:
            allowed_list.remove(name)

        # Save settings
        self.save_settings(settings)
        self._logger.info(f"Set MCP '{name}' enabled state to: {new_state}")
        return new_state

    def get_mcp_details(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get details of a specific MCP server.

        Args:
            name: Name of the MCP server

        Returns:
            Dictionary with MCP details or None if not found:
            {
                "name": "...",
                "command": "...",
                "args": [...],
                "enabled": True/False
            }
        """
        settings = self.load_settings()

        mcp_servers = settings.get('mcpServers', {})
        allowed_list = settings.get('mcp', {}).get('allowed', [])

        if name not in mcp_servers:
            return None

        config = mcp_servers[name]
        return {
            'name': name,
            'command': config.get('command', ''),
            'args': config.get('args', []),
            'enabled': name in allowed_list
        }

    def update_mcp(self, name: str, command: Optional[str] = None,
                   args: Optional[List[str]] = None) -> bool:
        """
        Update an existing MCP server configuration.

        Args:
            name: Name of the MCP server to update
            command: New command (None to keep existing)
            args: New args list (None to keep existing, must be list of strings if provided)

        Returns:
            True if successful

        Raises:
            MCPManagerError: If MCP doesn't exist or parameters are invalid
        """
        settings = self.load_settings()

        # Check if MCP exists
        if name not in settings.get('mcpServers', {}):
            raise MCPManagerError(f"MCP '{name}' not found")

        # Validate parameters if provided
        if command is not None and (not command or not isinstance(command, str)):
            raise MCPManagerError("MCP command must be a non-empty string")
        if args is not None and not isinstance(args, list):
            raise MCPManagerError("MCP args must be a list")

        # Update configuration
        config = settings['mcpServers'][name]
        if command is not None:
            config['command'] = command
        if args is not None:
            # Validate and coerce args elements to strings (consistent with load_settings behavior)
            if any(not isinstance(a, str) for a in args):
                args = [str(a) for a in args]
            config['args'] = args

        # Save settings
        self.save_settings(settings)
        self._logger.info(f"Updated MCP '{name}'")
        return True

    def install_from_template(self, template_name: str, enable: bool = True) -> bool:
        """
        Install an MCP from a predefined template.

        Args:
            template_name: Name of the template to install
            enable: Whether to enable the MCP after installation

        Returns:
            True if successful

        Raises:
            MCPManagerError: If template doesn't exist or MCP already exists
        """
        # Check if template exists
        if template_name not in MCP_TEMPLATES:
            raise MCPManagerError(f"Template '{template_name}' not found")

        # Get template configuration
        template = MCP_TEMPLATES[template_name]

        # Check if MCP already exists based on template['name']
        mcps = self.get_mcps()
        if template["name"] in mcps:
            raise MCPManagerError(f"MCP '{template['name']}' already exists")

        # Install MCP
        self.add_mcp(template["name"], template["command"], template["args"])

        # Enable if requested
        if enable:
            self.toggle_allowed(template["name"], True)

        self._logger.info(f"Installed MCP '{template_name}' from template")
        return True

    def is_template_installed(self, template_name: str) -> bool:
        """
        Check if a template is already installed.

        Args:
            template_name: Name of the template to check

        Returns:
            True if the MCP from this template is installed
        """
        if template_name not in MCP_TEMPLATES:
            return False

        template = MCP_TEMPLATES[template_name]
        mcps = self.get_mcps()
        return template["name"] in mcps

    def refresh_settings_path(self, settings_path: Optional[str] = None, user_base_path: Optional[str] = None) -> None:
        """
        Refresh the settings path by reloading from ConfigManager or using provided path.

        Args:
            settings_path: Optional new settings path. If provided, takes priority.
            user_base_path: Optional base path of the user (e.g., 'C:/Users/TI00').
                            If provided, settings_path will be constructed as:
                            user_base_path / ".gemini" / "settings.json"
                            Takes priority over ConfigManager reload.
        
        Priority order:
            1. settings_path (if provided)
            2. user_base_path (if provided)
            3. ConfigManager.get_user_path() (reload from config)
            4. Path.home() (default fallback)
        """
        try:
            config_manager = ConfigManager()
            cli_type = config_manager.get_cli_type()
            cli_dir = f".{cli_type}"

            if settings_path is not None:
                self.settings_path = Path(settings_path)
                self._logger.info(f"Using provided settings path: {self.settings_path}")
            elif user_base_path is not None:
                base = self._validate_and_normalize_user_path(user_base_path)
                self.settings_path = base / cli_dir / "settings.json"
                self._logger.info(f"Using settings path from user_base_path: {self.settings_path}")
            else:
                user_path = config_manager.get_user_path()
                if user_path:
                    try:
                        normalized_path = Path(user_path).expanduser().resolve()
                    except (OSError, PermissionError) as e:
                        self._logger.debug(f"Path.resolve() failed, falling back to expanduser(): {e}")
                        normalized_path = Path(user_path).expanduser()
                    self.settings_path = normalized_path / cli_dir / "settings.json"
                    self._logger.info(f"Refreshed settings path from config: {self.settings_path}")
                else:
                    self.settings_path = Path.home() / cli_dir / "settings.json"
                    self._logger.warning(f"No user path configured, using default: {self.settings_path}")
                    self._logger.info("Execute `python setup_user_path.py` para configurar o caminho do usuário")
        except ConfigManagerError as e:
            cli_dir = ".gemini"  # Fallback
            self.settings_path = Path.home() / cli_dir / "settings.json"
            self._logger.warning(f"Error loading config ({e}), using default path: {self.settings_path}")
            self._logger.info("Execute `python setup_user_path.py` para configurar o caminho do usuário")

        # Clear cache to force reload
        self._settings_cache = None

