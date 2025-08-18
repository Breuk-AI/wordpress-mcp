# Contributing to WordPress MCP

First off, thank you for considering contributing to WordPress MCP! It's people like you that make this tool better for everyone.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, please include:

- **Clear and descriptive title**
- **Steps to reproduce** the issue
- **Expected behavior** vs what actually happened
- **Screenshots** if applicable
- **Environment details**:
  - WordPress version
  - PHP version
  - Python version
  - MCP client (e.g., Claude Desktop version)
  - Operating system

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **List any alternatives** you've considered

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. Ensure the test suite passes
4. Make sure your code follows the existing style
5. Issue that pull request!

## Development Setup

### Prerequisites

- Python 3.8+
- WordPress test site
- Git

### Setting Up Your Development Environment

1. Fork and clone the repository:
```bash
git clone https://github.com/your-username/wordpress-mcp.git
cd wordpress-mcp
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
cd mcp-server
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available
```

4. Set up your test WordPress site with the plugin

5. Copy `.env.example` to `.env` and configure

### Running Tests

```bash
# Python tests
pytest tests/

# With coverage
pytest --cov=. tests/
```

### Code Style

#### Python
- Follow PEP 8
- Use type hints where appropriate
- Add docstrings to all functions and classes
- Maximum line length: 100 characters

#### PHP
- Follow WordPress Coding Standards
- Use PHPDoc for all functions and classes
- Properly escape all output
- Sanitize all input

### Making Changes

1. **Create a feature branch**:
```bash
git checkout -b feature/amazing-feature
```

2. **Make your changes**:
- Write clean, well-documented code
- Add tests for new functionality
- Update documentation as needed

3. **Commit your changes**:
```bash
git commit -m "Add amazing feature"
```

Use conventional commit messages:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks

4. **Push to your fork**:
```bash
git push origin feature/amazing-feature
```

5. **Open a Pull Request**

## Project Structure

```
wordpress-mcp/
├── mcp-server/           # Python MCP server
│   ├── server.py         # Main server entry point
│   ├── wp_client.py      # WordPress API client
│   ├── tools/            # Tool modules
│   │   ├── posts.py
│   │   ├── pages.py
│   │   ├── media.py
│   │   ├── woocommerce.py
│   │   ├── templates.py
│   │   └── system.py
│   └── tests/            # Test files
├── wp-mcp-plugin/        # WordPress plugin
│   ├── wp-mcp-plugin.php # Main plugin file
│   └── includes/         # Plugin includes
│       ├── api-endpoints.php
│       ├── auth.php
│       └── backup-manager.php
└── docs/                 # Documentation

```

## Adding New Tools

To add a new tool:

1. Create a new module in `mcp-server/tools/`
2. Implement the tool class with:
   - `get_tools()` - Return tool definitions
   - `handles_tool()` - Check if module handles a tool
   - `execute_tool()` - Execute the tool
3. Register in `server.py`
4. Add documentation
5. Add tests

Example tool structure:
```python
class MyNewTools:
    def __init__(self, wp_client):
        self.wp = wp_client
        self.tools = {
            "wp_my_tool": self.my_tool_method
        }
    
    def get_tools(self) -> List[Tool]:
        return [
            Tool(
                name="wp_my_tool",
                description="Description here",
                inputSchema={...}
            )
        ]
    
    def handles_tool(self, tool_name: str) -> bool:
        return tool_name in self.tools
    
    async def execute_tool(self, tool_name: str, arguments: Dict) -> Any:
        if tool_name in self.tools:
            return await self.tools[tool_name](**arguments)
        raise ValueError(f"Unknown tool: {tool_name}")
```

## Testing Guidelines

- Write tests for all new functionality
- Maintain test coverage above 80%
- Test both success and failure cases
- Mock external API calls
- Use fixtures for test data

## Documentation

- Update README.md for user-facing changes
- Add docstrings to all new functions
- Update tool descriptions for clarity
- Include examples for complex features
- Keep CHANGELOG.md updated

## Release Process

1. Update version numbers:
   - `mcp-server/server.py`
   - `wp-mcp-plugin/wp-mcp-plugin.php`
   - `package.json` (if applicable)

2. Update CHANGELOG.md

3. Create a release PR

4. After merge, tag the release:
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## Questions?

Feel free to open an issue for:
- Questions about the codebase
- Clarification on contributing guidelines
- Discussion about potential features

## Recognition

Contributors will be recognized in:
- The project README
- Release notes
- The contributors page

Thank you for contributing! 🎉
