# LexRedline Code Workflow

## Repository
- **GitHub**: `deecody71/LexRedline`
- **Structure**: Monorepo with `backend/` (contract engine) and `frontend/` (Next.js app)

## Branch Strategy
- `main` — production-ready code. Protected.
- Feature branches named `feat/<description>` for new work
- Fix branches named `fix/<description>` for bug fixes

## Process
1. Members clone the repo and create feature branches
2. Work is pushed to the feature branch
3. A pull request is opened to `main`
4. The team lead reviews and merges via squash

## Initial Setup
For the first push to a fresh repo, code is copied from `/home/team/shared/` into the appropriate directories and committed directly to `main`.