# Contributing to HeatLens

Thank you for your interest in contributing to HeatLens! We welcome contributions from the community.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a new branch for your feature
4. Make your changes
5. Push to your fork
6. Create a Pull Request

## Code of Conduct

Please be respectful and constructive in all interactions.

## Development Setup

```bash
# Clone and setup
git clone https://github.com/your-fork/heatlens.git
cd heatlens_v1.0

# Backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
npm install
```

## Making Changes

### Backend Changes
- Follow PEP 8 style guide
- Add tests for new features
- Update docstrings
- Use type hints

### Frontend Changes
- Follow existing TypeScript conventions
- Use Tailwind CSS for styling
- Test in multiple browsers
- Keep components focused

## Commit Messages

Use clear, descriptive commit messages:
```
feat: Add new heat analysis endpoint
fix: Resolve cache invalidation bug
docs: Update API documentation
test: Add tests for anomaly detection
```

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass: `pytest tests/` and TypeScript checks
4. Reference any related issues
5. Wait for review and address feedback

## Reporting Issues

- Check if issue already exists
- Provide clear description
- Include steps to reproduce
- Attach logs if applicable

## Questions?

Open a GitHub issue or discussion for questions.

Thank you for contributing! 🎉
