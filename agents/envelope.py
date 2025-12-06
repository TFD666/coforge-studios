# agents/envelope.py
import json
import uuid
from datetime import datetime
from typing import Dict, Any

def now_iso():
    return datetime.utcnow().isoformat() + "Z"

def make_envelope(from_agent: str, to_agent: str, message_type: str, payload: Dict[str, Any], meta: Dict[str, Any] = None):
    env = {
        "envelope_id": str(uuid.uuid4()),
        "from_agent": from_agent,
        "to_agent": to_agent,
        "timestamp": now_iso(),
        "message_type": message_type,
        "payload": payload,
        "meta": meta or {}
    }
    return env

def save_envelope(env: Dict[str, Any], path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(env, f, indent=2)

def load_envelope(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
