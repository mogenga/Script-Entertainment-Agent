# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**情感本DM演绎设计助手** - A script murder game (剧本杀) assistant for emotional storylines. Helps DMs (Dungeon Masters) design one-on-one ritual performance segments to enhance player immersion.

### Architecture

**Multi-Agent System with FastAPI Backend + React Native Frontend**

```
Frontend (React Native) → FastAPI API → Multi-Agent System → Qwen API
                                ↓
                          PostgreSQL
```

**4-Agent Architecture:**
1. **ScriptParser** - Parses raw script text into structured data (characters, episodes)
2. **StrategyDesigner** - Analyzes episode content and recommends performance strategy
3. **PerformanceDesigner** - Generates complete performance manuals (actions, lines, timing, props)
4. **Orchestrator** - Coordinates agent workflow and handles dual-track comparison mode

### Project Structure

```
├── backend/           # FastAPI backend (to be implemented)
│   ├── app/
│   │   ├── agents/    # 4 Agent implementations
│   │   ├── api/       # FastAPI routes
│   │   ├── models/    # SQLModel database models
│   │   ├── services/  # LLM service wrapper
│   │   └── main.py    # FastAPI entry point
│   └── requirements.txt
├── front/             # React Native frontend (initialized)
│   ├── src/
│   ├── package.json
│   └── App.tsx
└── docs/              # Project documentation (Chinese)
    ├── 需求分析.md
    ├── 架构设计.md
    ├── 设计规范.md
    └── 实施计划.md
```

## Common Commands

### Frontend (React Native)

```bash
cd front

# Install dependencies
npm install

# Start Metro bundler
npm start

# Run on Android
npm run android

# Run on iOS
npm run ios

# Run tests
npm test

# Lint
npm run lint
```

### Backend (FastAPI - to be implemented)

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload

# Run tests
pytest

# Format code
black app/
isort app/

# Type check
mypy app/
```

### Database

```bash
# PostgreSQL should be running locally or via Docker
# Connection string in backend/.env:
# DATABASE_URL="postgresql://user:password@localhost:5432/dm_assistant"
```

## Design Constraints

### Frontend (Critical)
- **NO EMOJI** - UI must not use emoji anywhere
- **White Theme** - Primary color is white (#FFFFFF), buttons use dark colors (#1A1A1A)
- **Minimalist** - Remove all non-essential visual elements
- **Functional First** - Every design serves a functional purpose

### Backend
- **Prompt Engineering Only** - No model fine-tuning, use Qwen API with carefully crafted prompts
- **PostgreSQL Unified** - Use PostgreSQL for both dev and production (no SQLite)

### API Endpoints (Planned)

```
POST   /api/v1/scripts              # Create script
POST   /api/v1/scripts/upload       # Upload script file
GET    /api/v1/scripts/{id}         # Get script
POST   /api/v1/scripts/{id}/parse   # Parse script structure
GET    /api/v1/scripts/{id}/episodes # Get episodes

POST   /api/v1/performances         # Generate performance plan (auto)
POST   /api/v1/performances/collaborate  # Generate with user collaboration
GET    /api/v1/performances/{id}    # Get performance plan
```

## Key Implementation Notes

### Agent Output Format

All agents output structured JSON via Qwen API. See `docs/架构设计.md` section 2.1 for exact schemas.

### Dual-Track Mode

When user provides their own idea (`collaborate` mode), Orchestrator generates TWO plans:
1. AI auto-generated plan
2. Plan based on user's idea
3. Comparison analysis showing pros/cons of each

### Database Models

- **Script** - Raw script content + parsed structure
- **Character** - Characters with relationships
- **Episode** - Segments within a script
- **PerformancePlan** - Generated performance manual with steps, lines, props

## Documentation

All project documentation is in Chinese in the `docs/` directory:
- `需求分析.md` - Requirements analysis
- `架构设计.md` - Architecture design
- `设计规范.md` - Design specifications (white theme constraints)
- `实施计划.md` - Implementation plan with 34 tasks

## Git Commit Convention

Format: `type: description`

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example: `feat: add ScriptParser agent with tests`
