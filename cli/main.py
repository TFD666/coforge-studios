# cli/main.py

import argparse
import sys
from agents.planner import Planner
from agents.planner_utils import pretty_print_plan

def main():
    parser = argparse.ArgumentParser(description="Coforge Studios CLI")
    
    subparsers = parser.add_subparsers(dest="command")

    # ----------------------------------------------------
    # create command
    # ----------------------------------------------------
    create_cmd = subparsers.add_parser("create", help="Create a new AI-assisted plan")
    create_cmd.add_argument("request", type=str, help="User request for the Planner agent")
    create_cmd.add_argument(
        "--mock",
        action="store_true",
        help="Run Planner in mock mode (no OpenAI cost)"
    )

    args = parser.parse_args()

    if args.command == "create":
        return run_create(args)
    else:
        print("No command provided. Use --help for options.")
        return


def run_create(args):
    print("\n=== Coforge Studios: Planner Agent ===\n")

    user_input = args.request
    use_mock = args.mock

    print(f"[CLI] User Request: {user_input}")
    if use_mock:
        print("[CLI] Running in MOCK MODE (no OpenAI calls)\n")

    # Initialize planner
    planner = Planner(
        schema_path="agents/schemas/plan_schema.json",
        model_name="gpt-4o-mini",
        mock=use_mock
    )

    # Run planner (interactive clarifying loop)
    try:
        plan = planner.run(user_input)
    except Exception as e:
        print(f"\n[ERROR] Planner failed:\n{e}")
        sys.exit(1)

    # Display plan nicely
    print("\n=== Final Plan (JSON) ===\n")
    print(pretty_print_plan(plan))
    print("\n======================================\n")
    print("✔ Plan saved as an envelope in: envelopes/")
    print("✔ You can now pass this plan to the Builder agent.")
    print()

    return plan


if __name__ == "__main__":
    main()
