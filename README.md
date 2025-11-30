# Coforge Studios

A student-built minimal multi-agent system (Planner → Builder → Critic) — Python + LLM API.
Goal: learn while building a job-ready prototype in 1 month.

## Week 1 goal
Create environment, repo, and a minimal Planner that asks clarifying questions and outputs a JSON plan.

## Project structure
- `agents/` — code for Planner, Builder, Critic (Planner first)
- `agents/schemas/plan_schema.json` — Planner output JSON schema
- `cli/` — simple CLI to interact with Planner (and later Builder/Critic)
- `docs/` — architecture and design notes
- `examples/` — example transcripts & sample inputs
- `tests/` — unit tests (pytest)

## Quick start (Windows PowerShell / Cursor)
1. `python -m venv .venv`
2. `.venv\Scripts\Activate.ps1`
3. `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and set `OPENAI_API_KEY`
5. `python -m cli.main create "build a todo app"`

## License
MIT
