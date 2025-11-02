#!/usr/bin/env python3
"""
Jules API Client for LUKHAS Task Execution

Usage:
    python scripts/jules_client.py create-session --task-file docs/gonzo/JULES_TASK1_READY.md
    python scripts/jules_client.py list-sessions
    python scripts/jules_client.py get-session <session_id>
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import requests


class JulesClient:
    """Client for interacting with Google Jules API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("JULES_API_KEY")
        if not self.api_key:
            raise ValueError("JULES_API_KEY not found in environment")

        self.base_url = "https://jules.googleapis.com/v1alpha"
        self.headers = {
            "X-Goog-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """Make HTTP request to Jules API."""
        url = f"{self.base_url}/{endpoint}"

        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, timeout=timeout)
            elif method == "POST":
                response = requests.post(
                    url,
                    headers=self.headers,
                    json=data,
                    timeout=timeout
                )
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            print(f"❌ Request timed out after {timeout}s", file=sys.stderr)
            sys.exit(1)
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP Error: {e}", file=sys.stderr)
            print(f"Response: {e.response.text}", file=sys.stderr)
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}", file=sys.stderr)
            sys.exit(1)

    def list_sources(self) -> Dict[str, Any]:
        """List available GitHub sources."""
        print("📋 Listing Jules sources...")
        return self._make_request("GET", "sources")

    def create_session(
        self,
        prompt: str,
        source_id: str = "github/LukhasAI/Lukhas",
        ref: str = "main"
    ) -> Dict[str, Any]:
        """Create a new Jules session."""
        print(f"🚀 Creating Jules session for source {source_id}...")

        payload = {
            "prompt": prompt,
            "source": f"sources/{source_id}",
            "ref": ref
        }

        return self._make_request("POST", "sessions", data=payload, timeout=60)

    def list_sessions(self) -> Dict[str, Any]:
        """List all Jules sessions."""
        print("📋 Listing Jules sessions...")
        return self._make_request("GET", "sessions")

    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get details of a specific session."""
        print(f"🔍 Getting session {session_id}...")
        return self._make_request("GET", f"sessions/{session_id}")

    def list_activities(self, session_id: str) -> Dict[str, Any]:
        """List activities for a session."""
        print(f"📊 Listing activities for session {session_id}...")
        return self._make_request("GET", f"sessions/{session_id}/activities")


def load_task_prompt(task_file: Path) -> str:
    """Extract the task prompt from the Jules task file."""
    with open(task_file, 'r') as f:
        content = f.read()

    # Extract prompt between EOF markers
    if "EOF" in content:
        parts = content.split("EOF")
        if len(parts) >= 3:
            # Get the content between the first and second EOF
            prompt = parts[1].strip()
            # Remove the quotes/newlines at boundaries
            prompt = prompt.strip("'\"\n")
            return prompt

    # Fallback: return entire content
    print("⚠️  Warning: Could not find EOF markers, using entire file", file=sys.stderr)
    return content


def main():
    parser = argparse.ArgumentParser(description="Jules API Client")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # list-sources command
    subparsers.add_parser("list-sources", help="List GitHub sources")

    # create-session command
    create_parser = subparsers.add_parser("create-session", help="Create a new session")
    create_parser.add_argument(
        "--task-file",
        type=Path,
        default=Path("docs/gonzo/JULES_TASK1_READY.md"),
        help="Path to task file containing prompt"
    )
    create_parser.add_argument(
        "--prompt",
        type=str,
        help="Direct prompt text (overrides --task-file)"
    )
    create_parser.add_argument(
        "--source-id",
        default="github/LukhasAI/Lukhas",
        help="Jules source ID (e.g., github/LukhasAI/Lukhas)"
    )
    create_parser.add_argument("--ref", default="main", help="Git ref")

    # list-sessions command
    subparsers.add_parser("list-sessions", help="List all sessions")

    # get-session command
    get_parser = subparsers.add_parser("get-session", help="Get session details")
    get_parser.add_argument("session_id", help="Session ID")

    # list-activities command
    activities_parser = subparsers.add_parser("list-activities", help="List session activities")
    activities_parser.add_argument("session_id", help="Session ID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        client = JulesClient()

        if args.command == "list-sources":
            result = client.list_sources()
            print(json.dumps(result, indent=2))

        elif args.command == "create-session":
            if args.prompt:
                prompt = args.prompt
            else:
                prompt = load_task_prompt(args.task_file)

            result = client.create_session(
                prompt=prompt,
                source_id=args.source_id,
                ref=args.ref
            )
            print("✅ Session created successfully!")
            print(json.dumps(result, indent=2))

            if "name" in result:
                session_id = result["name"].split("/")[-1]
                print(f"\n🔗 Session ID: {session_id}")
                print(f"📊 Monitor: python scripts/jules_client.py get-session {session_id}")

        elif args.command == "list-sessions":
            result = client.list_sessions()
            print(json.dumps(result, indent=2))

        elif args.command == "get-session":
            result = client.get_session(args.session_id)
            print(json.dumps(result, indent=2))

        elif args.command == "list-activities":
            result = client.list_activities(args.session_id)
            print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
