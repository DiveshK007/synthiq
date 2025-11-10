# Contributing to SynthIQ

Thank you for contributing to SynthIQ! This guide will help you get started with local development and understand how CI works.

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 20+
- npm or yarn

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/DiveshK007/synthiq.git
   cd synthiq
   ```

2. **Set up backend services**

   Each service needs its own virtual environment:

   ```bash
   # Orchestrator
   cd orchestrator
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r ../dev-requirements.txt
   export INGESTOR_URL=http://localhost:8081
   export SUMMARIZE_URL=http://localhost:8082
   export VIZ_URL=http://localhost:8083
   export FRONTEND_ORIGIN=http://localhost:5174
   python main.py
   ```

   Repeat for `ingestor`, `summarize`, and `viz` services (see `docs/local-dev.md` for full instructions).

3. **Set up frontend**

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Running Tests Locally

**Python Services:**

```bash
# From service directory
pytest -q

# Or from repo root
pytest orchestrator/tests/
```

**Frontend:**

```bash
cd frontend
npm run typecheck  # TypeScript type checking
npm run build      # Build check
```

### Code Quality Checks

**Python (using ruff and pyright):**

```bash
# Install dev dependencies
pip install -r dev-requirements.txt

# Lint
ruff check orchestrator/

# Format check
ruff format --check orchestrator/

# Type check
pyright orchestrator/
```

**Frontend:**

```bash
cd frontend
npm run typecheck  # TypeScript type checking
```

## CI/CD Pipeline

### GitHub Actions Workflow

The CI pipeline runs automatically on:
- Push to any branch
- Pull requests

### CI Jobs

1. **Python Services Job**
   - Runs for each service (orchestrator, ingestor, summarize, viz)
   - Installs dependencies
   - Runs linting (ruff)
   - Checks formatting (ruff format)
   - Type checking (pyright)
   - Runs unit tests (pytest)

2. **Frontend Job**
   - Installs npm dependencies
   - Type checks TypeScript (`tsc --noEmit`)
   - Builds the frontend (`npm run build`)

### Making CI Pass

- Ensure all Python services pass linting and type checking
- Ensure frontend builds without errors
- Add tests for new features
- Keep code formatted (ruff format)

## Development Workflow

1. Create a feature branch from `main`
2. Make your changes
3. Run local tests and quality checks
4. Commit with descriptive messages
5. Push and create a pull request
6. CI will automatically run checks
7. Address any CI failures
8. Get code review approval
9. Merge to `main`

## Code Style

- **Python**: Follow PEP 8, use ruff for linting
- **TypeScript**: Follow TypeScript best practices, use strict mode
- **Commits**: Use conventional commit messages (feat:, fix:, docs:, etc.)

## Questions?

If you have questions or need help, please open an issue on GitHub.

