# CLI Workspace Context: MCP Manager

## Project Overview

This is a Python project designed to manage MCP (Model Context Protocol) server configurations for the Gemini IDE and Qwen Coder CLI. It provides both a command-line interface and a graphical user interface (GUI) for managing the `settings.json` file used by the respective CLIs.

The project is structured into three main components:

*   **Core Logic (`src/core`)**: Contains the `ConfigManager` and `MCPManager` classes, which handle the reading, writing, and validation of configuration files.
*   **GUI (`mcp_gui.py`)**: A Tkinter-based GUI application that provides a user-friendly interface for managing MCP configurations and selecting the target CLI.
*   **Scripts (`scripts`)**: Includes utility scripts for project setup, such as configuring the user's base path and preferred CLI.

The main technologies used are:

*   **Python**: The primary programming language.
*   **Tkinter**: For the graphical user interface.
*   **unittest**: For testing the core logic.

## Project Structure

```
+-- mcp_gui.py                  # Main GUI application
+-- README.md                   # Project documentation
+-- CLI.md                      # This file
+-- requirements.txt            # Project dependencies
+-- EXECUTAR.bat                # Windows execution script
+-- src/
   +-- __init__.py
   +-- core/
      +-- __init__.py
      +-- config_manager.py
      +-- mcp_manager.py
      +-- mcp_config.example.json
   +-- gui/                    # GUI components
+-- scripts/
   +-- __init__.py
   +-- create_directories.py
   +-- secure_dirs_setup.py
   +-- setup_user_path.py
+-- examples/
   +-- __init__.py
   +-- demo_integration.py
   +-- example_config_usage.py
+-- tests/
   +-- __init__.py
   +-- test_batch_operations.py
   +-- test_cli_switching.py
   +-- test_config_manager.py
   +-- test_corrupt_file_handling.py
   +-- test_dependency_validation.py
   +-- test_dependency_validation_complete.py
   +-- test_gui_batch.py
   +-- test_mcp_manager_integration.py
+-- docs/
    +-- ...
```

## Building and Running

### Prerequisites

*   Python 3.x
*   Tkinter (usually included with Python)

### Configuration

Before running the application, you need to configure the user's base path and preferred CLI. This is the path to the user's home directory (e.g., `C:/Users/YourUser`). You can do this by running the following command:

```bash
python -m scripts.setup_user_path
```

This will create a `mcp_config.json` file in the `src/core` directory with the specified path and CLI preference.

### Running the GUI

To run the GUI application, execute the following command:

```bash
python mcp_gui.py
```

### Running Tests

To run the unit tests, use the following command:

```bash
python -m unittest
```

## Development Conventions

*   **Code Style**: The code follows the PEP 8 style guide.
*   **Testing**: The project uses the `unittest` framework for testing. Tests are located in the `tests` directory.
*   **Modularity**: The project is organized into modules with clear responsibilities. The core logic is separated from the GUI, making it easy to maintain and extend.
*   **Error Handling**: The project uses custom exceptions (`ConfigManagerError` and `MCPManagerError`) to handle errors related to configuration and MCP management.


