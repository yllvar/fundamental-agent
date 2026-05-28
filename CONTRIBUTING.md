# Contributing Guide

Thank you for contributing to the Fundamental Agent project!

## 🚀 Getting Started

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 Development Environment Setup

```bash
# Clone repository
git clone https://github.com/jihwanwoo/fundamental-agent.git
cd fundamental-agent

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env file with actual values

# Run tests
python test_system.py
```

## 🧪 Testing

When adding new features, please include tests.

```bash
# Basic tests
python test_system.py

# Individual component tests
python data_monitoring/technical_analysis.py
python notifications/slack_notifier.py
```

## 📝 Coding Style

- Follow Python PEP 8 style guide
- Write docstrings for functions and classes
- Use clear and meaningful variable names
- Write comments in English

## 🐛 Bug Reports

If you find a bug, please create an issue with the following information:

- Operating system and Python version
- Full error message
- Steps to reproduce
- Expected vs actual behavior

## 💡 Feature Suggestions

When suggesting new features:

- Explain the purpose and need
- Provide implementation ideas
- Include relevant examples or references

## 📞 Contact

If you have questions or need help, please reach out via GitHub Issues.
