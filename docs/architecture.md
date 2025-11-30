# Architecture (Day 1 snapshot)

This document captures the initial high-level architecture for Coforge Studios.

## Core idea
A multi-agent orchestration: Planner → Builder → Critic.

- **Planner**: Understands user intent, asks clarifying questions, produces a JSON plan (schema in agents/schemas/plan_schema.json).
- **Builder**: Consumes the Planner JSON and generates the requested deliverables (code, files, content) strictly according to the plan.
- **Critic**: Evaluates Builder outputs against the plan's acceptance criteria and requests refinements.

## Data contract
Planner produces a JSON structure that includes:
- `intent`, `constraints`, `acceptance_criteria`, `deliverables`, `steps[]` (each with `step_id`, `description`, `inputs`, `expected_output`).

This JSON is validated with `jsonschema` by Builder and Critic.

## Interfaces
- CLI (initial): `cli/main.py` implements simple `create` and `show` commands.
- Later: a small REST or Web UI for better interactivity.

## Week 1 goal
Get Planner prototype working, CLI wired, schema validated, and tests passing.
