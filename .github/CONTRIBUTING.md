# Contributing to Islam Mate API

Thank you for wanting to contribute! Please read this before opening a PR.

---

## Branch Strategy

| Branch | Purpose |
|---|---|
| `main` | Stable, production-ready code only |
| `development` | All active development — **target this for all PRs** |
| `feature/*` | New features (`feature/quran-module`) |
| `fix/*` | Bug fixes (`fix/auth-init`) |

**Rule: Never push directly to `main`.** All changes go through `development` via Pull Request.

---

## Workflow

```bash
# 1. Fork the repo and clone
git clone https://github.com/YOUR_USERNAME/api.git
cd api

# 2. Set upstream
git remote add upstream https://github.com/islam-mate/api.git

# 3. Create your feature branch FROM development
git checkout development
git pull upstream development
git checkout -b feature/your-feature-name

# 4. Make changes, commit
git add .
git commit -m "feat: add your feature description"

# 5. Push your branch
git push origin feature/your-feature-name

# 6. Open PR → base: development (NOT main)
```

---

## Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add quran audio endpoint
fix: resolve prayer times timezone bug
docs: update API reference
refactor: simplify module loader
chore: update dependencies
```

---

## Module Structure

Every new feature must follow the module structure:

```
modules/your_module/
├── __init__.py
├── models.py      # SQLAlchemy ORM models
├── schemas.py     # Pydantic request/response schemas
├── routes.py      # FastAPI router + endpoints
└── service.py     # Business logic (optional)
```

The Kernel auto-discovers modules — no manual registration needed.

---

## Code Standards

- **Python 3.11+** — use type hints everywhere
- **Docstrings** for all route functions
- **English only** in code, comments, and docstrings (API responses support AR/EN)
- **No hardcoded secrets** — use `.env` and `config.yaml`
- Run `python -m pytest` before opening PR (when tests exist)

---

## Opening a Pull Request

- Target branch: `development`
- Title: describe what it does (not how)
- Link any related issues
- Describe testing steps

---

## Questions?

Open an issue or start a Discussion on GitHub.
