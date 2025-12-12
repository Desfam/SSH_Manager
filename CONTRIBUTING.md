# Contributing

Thanks for contributing!

Quick start
1. Fork and create a branch: git checkout -b feature/awesome
2. Create a virtualenv and install dependencies:
   python -m venv .venv
   # Windows: .venv\Scripts\activate
   source .venv/bin/activate
   pip install -r requirements.txt

Coding standards
- Format with black and lint with ruff.
- Add unit tests for new features.

Commit & PR
- Keep commits small and focused.
- Open a PR with a clear description and link to any related issue.
- CI must pass before merging.

Security
- Never commit secrets or private keys.
- Use the OS keyring (keyring package) or environment variables for credentials.
