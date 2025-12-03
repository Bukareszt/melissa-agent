# Contributing to Melissa Voice Assistant

First off, thank you for considering contributing to Melissa! 🎉

## How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title** describing the issue
- **Steps to reproduce** the behavior
- **Expected behavior** vs what actually happened
- **Environment details** (OS, Python version, etc.)
- **Logs** if available

### 💡 Suggesting Features

Feature suggestions are welcome! Please:

- Check if the feature has already been suggested
- Provide a clear description of the feature
- Explain why this feature would be useful
- Consider how it fits with the project's goals

### 🔧 Pull Requests

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create a branch** for your feature/fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes**
5. **Test** your changes thoroughly
6. **Commit** with clear messages:
   ```bash
   git commit -m "Add: description of what you added"
   git commit -m "Fix: description of what you fixed"
   ```
7. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Open a Pull Request**

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/melissa-voice-assistant.git
cd melissa-voice-assistant

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp env.example .env
# Edit .env with your API keys

# Run in development mode
python melissa_agent.py dev
```

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small
- Comment complex logic

## Adding New Tools

When adding new tools to the agent:

1. Add the tool function to `tools.py` (or create a new module)
2. Import and register it in `melissa_agent.py`
3. Add clear docstrings - the LLM uses these to decide when to call the tool
4. Update the agent's `instructions` to mention the new capability
5. Update `README.md` with usage examples

Example:

```python
# In melissa_agent.py
@function_tool()
async def my_new_tool(self, param: str) -> str:
    """
    Clear description of what this tool does.
    The LLM reads this to know when to use the tool.
    
    Args:
        param: Description of the parameter
    
    Returns:
        Description of what is returned
    """
    # Implementation
    return result
```

## Testing

Before submitting a PR:

1. Test the agent manually with various prompts
2. Verify tools work as expected
3. Check that memory persists correctly
4. Ensure no regressions in existing functionality

## Questions?

Feel free to open an issue for any questions about contributing!

---

Thank you for helping make Melissa better! 🙏



