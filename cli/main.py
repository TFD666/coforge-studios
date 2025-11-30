import os
import json
import click

SESSION_FILE = "latest_session.json"

@click.group()
def cli():
    """Coforge Studios CLI - Planner placeholder"""
    pass

@cli.command()
@click.argument("prompt", nargs=-1)
def create(prompt):
    """Create a new plan (placeholder Planner)."""
    user_input = " ".join(prompt)
    # placeholder planner behavior
    plan = {
        "intent": user_input,
        "constraints": {},
        "acceptance_criteria": ["works locally", "passes simple tests"],
        "deliverables": ["prototype"],
        "steps": [
            {"step_id": "1", "description": "Create repo skeleton", "inputs": {}, "expected_output": "repo skeleton"},
            {"step_id": "2", "description": "Implement minimal Planner", "inputs": {}, "expected_output": "JSON plan output"}
        ]
    }
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2)
    click.echo("Planner (placeholder) created a plan and saved to latest_session.json")
    click.echo(json.dumps(plan, indent=2))

@cli.command()
def show():
    """Show the latest generated plan."""
    if not os.path.exists(SESSION_FILE):
        click.echo("No session found. Run `create` first.")
        return
    click.echo(open(SESSION_FILE, "r", encoding="utf-8").read())

if __name__ == "__main__":
    cli()
