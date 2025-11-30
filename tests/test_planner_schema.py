import json
import os
from jsonschema import validate, ValidationError

SCHEMA_PATH = os.path.join("agents", "schemas", "plan_schema.json")
SAMPLE_PLAN_PATH = "tests/sample_plan.json"

def load_schema():
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def test_schema_loads():
    schema = load_schema()
    assert "properties" in schema

def test_sample_plan_validates():
    schema = load_schema()
    sample_plan = {
        "intent": "build a todo CLI",
        "constraints": {"language": "python"},
        "acceptance_criteria": ["creates tasks", "lists tasks"],
        "deliverables": ["cli app"],
        "steps": [
            {"step_id": "1", "description": "init repo", "inputs": {}, "expected_output": "repo skeleton"}
        ]
    }
    # should not raise ValidationError
    validate(instance=sample_plan, schema=schema)
