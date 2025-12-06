# agents/planner.py

import os
import json
import uuid
import datetime
from typing import Dict, List, Tuple, Optional

from openai import OpenAI
from agents.envelope import make_envelope, save_envelope
from agents.planner_utils import (
    generate_plan_id,
    validate_plan,
    pretty_print_plan
)

# -------------------------------
# Planner Class
# -------------------------------

class Planner:
    """
    Planner Agent
    - Asks clarifying questions (interactive)
    - Generates a detailed JSON plan (schema-aligned)
    - Validates JSON output
    - Auto-fixes invalid JSON with one retry
    - Supports smart mock mode
    """

    def __init__(
        self,
        schema_path: str,
        model_name: str = "gpt-4o-mini",
        mock: bool = False,
    ):
        self.schema_path = schema_path
        self.model_name = model_name
        self.mock = mock

        # Auto-create required folders
        os.makedirs("logs/planner", exist_ok=True)
        os.makedirs("envelopes", exist_ok=True)

        # Initialize OpenAI client (will be skipped in mock mode)
        if not mock:
            self.client = OpenAI()

    # -------------------------------
    # Public entrypoint
    # -------------------------------
    def run(self, user_input: str) -> dict:
        """
        Full Planner execution:
        1. Ask clarifying questions interactively
        2. Generate plan (mock or LLM)
        3. Validate plan
        4. Save plan envelope
        """

        print("\n[Planner] Starting planning process...")

        clarifying_history = self.ask_clarifying_questions(user_input)

        print("\n[Planner] Generating final plan...")

        if self.mock:
            plan = self.generate_plan_mock(user_input, clarifying_history)
        else:
            plan = self.generate_plan_llm(user_input, clarifying_history)

        print("\n[Planner] Validating plan...")
        valid, error = validate_plan(plan, self.schema_path)

        if not valid:
            print("[Planner] Plan failed validation. Attempting auto-repair...")

            # One retry: ask LLM to fix JSON output
            if not self.mock:
                plan = self.repair_invalid_json(plan, error)
                valid, error = validate_plan(plan, self.schema_path)

            if not valid:
                raise ValueError(f"Plan validation failed even after repair:\n{error}")

        # Save envelope
        envelope_path = self.save_plan_envelope(plan)

        print(f"\n[Planner] Plan ready ✓ Stored at: {envelope_path}")
        return plan

    # -------------------------------
    # Step 1 — Clarifying Questions
    # -------------------------------
    def ask_clarifying_questions(self, user_input: str) -> List[dict]:
        """
        Interactive clarifying Q/A loop:
        - Ask up to 3 questions
        - User answers via CLI input
        """
        clarifying_questions = []
        max_q = 3

        if self.mock:
            # Smart mock: ask 1-2 simple questions
            print("\n[Planner-MOCK] Asking simulated clarifying questions...")
            questions = [
                "Do you prefer Python or JavaScript?",
                "Should the output include built-in tests? (yes/no)"
            ]
            for q in questions[:2]:
                print(f"Planner: {q}")
                ans = input("You: ")
                clarifying_questions.append({
                    "question": q,
                    "answer": ans,
                    "asked_at": self.now(),
                    "answered_at": self.now()
                })
            return clarifying_questions

        # --- Real LLM-based clarifying questions (interactive) ---
        print("\n[Planner] Checking if clarifying questions are needed...")

        # Ask LLM: "What clarifying questions should I ask?"
        q_list = self.get_llm_clarifying_questions(user_input)
        q_list = q_list[:max_q]

        for q in q_list:
            print(f"\nPlanner: {q}")
            ans = input("You: ")

            clarifying_questions.append({
                "question": q,
                "answer": ans,
                "asked_at": self.now(),
                "answered_at": self.now()
            })

        return clarifying_questions

    # LLM helper — ask which questions to ask
    def get_llm_clarifying_questions(self, user_input: str) -> List[str]:
        msg = f"""
        User says: {user_input}

        Based on the project schema, output ONLY a JSON array of 1–3 clarifying questions.
        Example:
        ["What language should we use?", "Should data persist?"]
        """

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": msg}],
            temperature=0.1
        )

        try:
            return json.loads(response.choices[0].message.content)
        except:
            return [
                "Which language do you prefer?",
                "Should I include test cases?"
            ]

    # -------------------------------
    # Step 2 — Generate plan (LLM)
    # -------------------------------
    def generate_plan_llm(self, user_input: str, clarifying: List[dict]) -> dict:
        """
        Ask the LLM to generate the final JSON plan.
        """
        system_msg = self.get_system_prompt()
        user_msg = self.build_user_prompt(user_input, clarifying)

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.1,
            max_tokens=2500
        )

        raw = response.choices[0].message.content
        self.log_raw_output(raw)

        # Extract JSON
        try:
            start = raw.index("{")
            end = raw.rindex("}") + 1
            plan_json = raw[start:end]
            return json.loads(plan_json)
        except Exception as e:
            print("[Planner] JSON parsing failed. Returning raw for repair...")
            return {"error": raw, "exception": str(e)}

    # -------------------------------
    # Step 2B — Mock Mode
    # -------------------------------
    def generate_plan_mock(self, user_input: str, clarifying: List[dict]) -> dict:
        """
        Smart mock plan generation to simulate realistic Planner output.
        Useful for offline testing and avoiding API cost.
        """
        plan_id = generate_plan_id()
        now = self.now()

        return {
            "plan_id": plan_id,
            "plan_version": "1.0.0",
            "created_at": now,
            "user_input": user_input,
            "intent": "mock_intent",
            "context": {"language": "python"},
            "constraints": {},
            "clarifying_questions": clarifying,
            "acceptance_criteria": [
                "Runs without errors",
                "Produces expected output"
            ],
            "deliverables": [
                {"name": "main.py", "type": "file", "path_hint": "./", "description": "Main script"}
            ],
            "steps": [
                {
                    "step_id": "1",
                    "title": "Initialize project",
                    "description": "Create starter file structure",
                    "type": "code",
                    "expected_output": "main.py created"
                }
            ],
            "metadata": {"author": "planner_mock"}
        }

    # -------------------------------
    # Step 3 — Repair Invalid JSON
    # -------------------------------
    def repair_invalid_json(self, broken_plan: dict, error_msg: str) -> dict:
        """
        Ask LLM to fix invalid JSON response.
        """
        prompt = f"""
        The following JSON is invalid or does not match schema. Fix it.
        Error: {error_msg}

        JSON to fix:
        {json.dumps(broken_plan, indent=2)}

        Return ONLY valid JSON.
        """

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        raw = response.choices[0].message.content
        self.log_raw_output(raw, tag="repair")

        try:
            start = raw.index("{")
            end = raw.rindex("}") + 1
            fixed = raw[start:end]
            return json.loads(fixed)
        except:
            raise ValueError("Failed to repair JSON.")

    # -------------------------------
    # Envelope Saving
    # -------------------------------
    def save_plan_envelope(self, plan: dict) -> str:
        env = make_envelope(
            from_agent="Planner",
            to_agent="Builder",
            message_type="plan",
            payload=plan
        )

        filename = f"envelopes/plan_{plan['plan_id']}.envelope.json"
        save_envelope(env, filename)
        return filename

    # -------------------------------
    # Helpers
    # -------------------------------
    def get_system_prompt(self) -> str:
        return """
        You are Planner — an agent that converts a user's request into a strict, executable JSON plan for a Builder agent.
        Follow the schema exactly.
        Output ONLY JSON.
        """

    def build_user_prompt(self, user_input: str, clarifying: List[dict]) -> str:
        return f"""
        User request:
        {user_input}

        Clarifying Q/A so far:
        {json.dumps(clarifying)}

        Generate the final plan JSON.
        """

    def now(self) -> str:
        return datetime.datetime.utcnow().isoformat() + "Z"

    def log_raw_output(self, text: str, tag: str = "raw"):
        ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = f"logs/planner/{tag}_{ts}.log"
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
