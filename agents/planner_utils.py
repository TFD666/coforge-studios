# agents/planner_utils.py

import uuid
import json
from jsonschema import validate, ValidationError

def generate_plan_id():
    """Generate a UUIDv4 plan ID."""
    return str(uuid.uuid4())

def load_schema(schema_path: str):
    """Load a JSON schema file."""
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)

def validate_plan(plan: dict, schema_path: str):
    """Validate the plan dictionary against the JSON schema."""
    schema = load_schema(schema_path)
    try:
        validate(instance=plan, schema=schema)
        return True, ""
    except ValidationError as e:
        return False, str(e)

def pretty_print_plan(plan: dict):
    """Return a formatted JSON string for printing/debugging."""
    return json.dumps(plan, indent=2, ensure_ascii=False)
