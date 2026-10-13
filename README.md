# PySQL - MySQL Client Application

A modular, maintainable Tkinter-based MySQL client that can be packaged as a standalone executable.

## Features

- **MySQL Connection Management**: Connect, reconnect, and disconnect from MySQL servers
- **SQL Query Editor**: Multi-line editor with example query
- **Query Execution**: Support for multiple SQL statements and result sets
- **Result Display**: Table view with horizontal and vertical scrolling
- **SQL-literal Style Formatting**: Optional display of text values with single quotes
- **Transaction Support**: Automatic commit/rollback handling
- **Error Handling**: Informative error messages and status updates

## Prerequisites

- Python 3.14 or higher
- MySQL server (for runtime usage)

## Development Setup

### Using uv (Recommended)

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

1. **Install uv** (if not already installed):
   ```bash
   curl -Ls https://astral.sh/uv/install.sh | sh
   ```

2. **Create virtual environment and install dependencies**:
   ```bash
   cd PySQL
   uv sync
   ```

3. **Activate the virtual environment**:
   ```bash
   source .venv/bin/activate
   ```

### Alternative: Using pip

If you prefer pip:

```bash
# Create virtual environment
python -m venv .venv

# Activate on Unix/Linux
source .venv/bin/activate

# Activate on Windows
.venv\Scripts\activate

# Install dependencies
pip install mysql-connector-python
```

## Dependency Management

### Install runtime dependencies
```bash
uv add mysql-connector-python
```

### Install development dependencies
```bash
uv add --dev pyinstaller pytest
```

### Show installed dependencies
```bash
uv pip list
```

### Update dependencies
```bash
uv lock --upgrade
uv sync --upgrade
```

## Running the Application

### Development execution
```bash
uv run python -m pysql
```

Or, if you have the virtual environment activated:
```bash
python -m pysql
```

## Running Tests

The test suite includes unit tests for formatting, query processing, and database operations using mocking (no MySQL server required).

```bash
uv run pytest
```

### Run tests with verbose output
```bash
uv run pytest -v
```

### Run specific test file
```bash
uv run pytest tests/test_formatter.py
uv run pytest tests/test_query.py
```

### Run tests with coverage (if coverage is installed)
```bash
uv run pytest --cov=pysql --cov-report=term
```

## Packaging with PyInstaller

### Development Dependencies

Ensure PyInstaller is installed as a development dependency:
```bash
uv add --dev pyinstaller
```

### Basic Build Command

For a reliable one-directory build:

```bash
uv run pyinstaller \
  --name PySQL \
  --windowed \
  --onedir \
  --paths src \
  --collect-all mysql.connector \
  --clean \
  src/pysql/__main__.py
```

### Build Options Explained

- `--name PySQL`: Sets the application name
- `--windowed`: Prevents console window from showing on Windows/macOS
- `--onedir`: Creates a directory with all dependencies (recommended)
- `--paths src`: Ensures the src directory is in the Python path
- `--collect-all mysql.connector`: Collects all MySQL Connector/Python resources
- `--clean`: Cleans PyInstaller cache before building

### Platform-Specific Considerations

- **Windows**: Must be built on Windows. The executable will work on Windows systems.
- **Linux**: Must be built on Linux. The executable will work on Linux systems.
- **macOS**: Must be built on macOS. You may need to sign the application for distribution.

### One-File Build (Optional)

For a single executable file:

```bash
uv run pyinstaller \
  --name PySQL \
  --windowed \
  --onefile \
  --paths src \
  --collect-all mysql.connector \
  --clean \
  src/pysql/__main__.py
```

> **Note**: One-file builds may have longer startup times and some platforms may flag them as suspicious.

### Build Artifacts Location

- **Development**: The PyInstaller build process creates files in:
  - `build/` - Temporary build files
  - `dist/` - Final packaged application

- **Cleanup**: To remove build artifacts:
  ```bash
  rm -rf build/ dist/
  ```

### Testing the Packaged Application

After building, test the packaged application:

```bash
# Navigate to the dist directory
cd dist/PySQL

# Run the application (varies by platform)
./PySQL  # Linux/macOS
PySQL.exe  # Windows
```

## Project Structure

```text
PySQL/
├── README.md                    # This file
├── pyproject.toml              # Project configuration and dependencies
├── .gitignore                  # Git ignore rules
├── uv.lock                    # Lock file for uv dependencies
├── src/
│   └── pysql/
│       ├── __init__.py         # Package initialization
│       ├── __main__.py         # Module entry point
│       ├── app.py              # Application composition and startup
│       ├── core/
│       │   ├── __init__.py     # Core module
│       │   └── config.py       # Application constants and configuration
│       ├── database/
│       │   ├── __init__.py     # Database module
│       │   ├── connection.py   # MySQL connection management
│       │   └── query.py        # SQL query execution and result processing
│       ├── services/
│       │   ├── __init__.py     # Services module
│       │   └── formatter.py    # Database value display formatting
│       └── ui/
│           ├── __init__.py     # UI module
│           ├── main_window.py  # Main application window
│           ├── connection_panel.py  # Connection input controls
│           ├── query_editor.py  # SQL query editor
│           ├── results_view.py  # Result table display
│           └── options_panel.py # Display options
└── tests/
    ├── __init__.py             # Tests package
    ├── test_formatter.py       # Formatter service tests
    └── test_query.py           # Query and database tests
```

## Usage

### Connecting to MySQL

1. Enter connection details in the "MySQL connection" panel:
   - **Host**: MySQL server address (default: 127.0.0.1)
   - **Port**: MySQL server port (default: 3306)
   - **User**: MySQL username (default: root)
   - **Password**: MySQL password
   - **Database**: Optional database name

2. Click **Connect** to establish the connection

### Executing Queries

1. Enter SQL in the query editor
2. Click **Run query** to execute
3. Results appear in the table below
4. Use **Clear results** to clear the current results

### Display Options

- **SQL-literal style**: When checked, string values are displayed with single quotes
- This is a display convention only and does not affect database values

## Configuration

Application defaults can be modified in `src/pysql/core/config.py`:

- `DEFAULT_HOST`, `DEFAULT_PORT`, `DEFAULT_USER`: Connection defaults
- `DEFAULT_WINDOW_WIDTH`, `DEFAULT_WINDOW_HEIGHT`: Window dimensions
- `CONNECTION_TIMEOUT`: Connection timeout in seconds
- `DEFAULT_QUERY`: Default query in the editor

## Known Limitations

1. **Platform-specific builds**: PyInstaller builds must be created on the target platform
2. **MySQL dependency**: Requires MySQL server for runtime usage
3. **Display server**: GUI tests may require a display server in headless environments
4. **Large result sets**: Very large result sets may impact performance

## Troubleshooting

### "Missing dependency" error

Install the MySQL Connector/Python:
```bash
uv add mysql-connector-python
```

### PyInstaller not found

Install PyInstaller as a development dependency:
```bash
uv add --dev pyinstaller
```

### Build fails with missing modules

Ensure all dependencies are installed and the virtual environment is active.

### Application doesn't start after packaging

Check that:
- All dependencies are included (`--collect-all mysql.connector`)
- The build was performed on the correct platform
- Required DLLs/files are present in the dist directory

## GitHub Actions

This repository includes GitHub Actions workflows for automated testing and release publishing.

### Workflows

#### Test and Build (`test-and-build.yml`)
- **Trigger**: Push to `main` branch or pull requests targeting `main`
- **Actions**:
  - Run all unit tests with pytest
  - Test PyInstaller build on Linux
  - Verify build artifacts are created correctly

#### Release Build (`release.yml`)
- **Trigger**: New tag push (pattern: `v*`)
- **Actions**:
  - Build standalone executables for Linux, Windows, and macOS
  - Create GitHub release with platform-specific executables
  - Upload executables as release assets

### Creating a Release

To create a new release:

```bash
# Create and push a new tag
git tag v1.0.0
git push origin v1.0.0
```

The release workflow will automatically:
1. Build executables for all three platforms (Linux, Windows, macOS)
2. Create a GitHub release with the tag name
3. Attach platform-specific executables as assets:
   - `PySQL-linux-x86_64` (Linux executable)
   - `PySQL-windows-x86_64.exe` (Windows executable)
   - `PySQL-macos-x86_64` (macOS executable)

### Notes

- Each platform-specific executable is self-contained and includes all dependencies
- Executables are built using `--onefile` option for single-file distribution
- Windows builds are created on Windows runners
- Linux builds are created on Ubuntu runners  
- macOS builds are created on macOS runners
- Release assets are available for download from the GitHub release page

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `uv run pytest`
5. Submit a pull request

## License

This project is private. Do not distribute without permission.

---

**PySQL** - A maintainable MySQL client application built with Python and Tkinter.