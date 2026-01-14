# Contributing to PhishScope

Thank you for your interest in contributing to PhishScope! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and professional
- Focus on constructive feedback
- Help create a welcoming environment for all contributors

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/PhishScope/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - PhishScope version and environment details
   - Sample URL (if safe to share)

### Suggesting Features

1. Check existing feature requests
2. Create a new issue with:
   - Clear use case description
   - Why this feature would be valuable
   - Proposed implementation (optional)

### Contributing Code

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation if needed

4. **Test your changes**
   ```bash
   python -m pytest tests/
   ```

5. **Commit with clear messages**
   ```bash
   git commit -m "Add: Brief description of changes"
   ```

6. **Push and create a Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/PhishScope.git
cd PhishScope

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Install in development mode
pip install -e .
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Keep functions focused and single-purpose
- Maximum line length: 100 characters
- Use descriptive variable names

## Testing

- Add tests for new features
- Ensure existing tests pass
- Test with various phishing page types
- Consider edge cases

## Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Update EXAMPLE_REPORT.md if output format changes
- Comment complex algorithms

## Areas for Contribution

### High Priority
- Additional JavaScript deobfuscation techniques
- More phishing pattern detection rules
- Performance optimizations
- Test coverage improvements

### Medium Priority
- Support for additional browsers (Firefox, Safari)
- Multi-language support for reports
- PDF report generation
- MITRE ATT&CK technique mapping

### Low Priority
- GUI interface
- Docker containerization
- CI/CD pipeline improvements
- Additional output formats

## Security Considerations

- Never commit real phishing URLs or credentials
- Test in isolated environments only
- Be cautious with sample data
- Report security vulnerabilities privately

## Questions?

- Open a discussion in GitHub Discussions
- Tag issues with "question" label
- Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make PhishScope better! 🔍