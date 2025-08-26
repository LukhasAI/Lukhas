"""
LUKHAS PWM Python SDK
Simple client library for interacting with LUKHAS PWM API
"""

import json
import time
from typing import Any, Optional, Union
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class LukhasClient:
    """Client for interacting with LUKHAS PWM API"""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize LUKHAS client.

        Args:
            base_url: Base URL of LUKHAS API
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

        # Set up session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set default headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "LUKHAS-Python-SDK/1.0.0",
        })

        if api_key:
            self.session.headers["x-api-key"] = api_key

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Make HTTP request to API"""
        url = urljoin(self.base_url, endpoint)

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")

    # === Core Methods ===

    def complete(
        self,
        message: str,
        context: Optional[list[str]] = None,
        signals: Optional[dict[str, float]] = None,
        safety_mode: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Send a message for completion with optional modulation.

        Args:
            message: User message to process
            context: Optional context snippets
            signals: Optional endocrine signals (stress, novelty, etc.)
            safety_mode: Optional override (strict/balanced/creative)

        Returns:
            Completion response with audit_id
        """
        data = {
            "message": message,
            "context": context or [],
            "signals": signals or {},
        }

        if safety_mode:
            data["safety_mode"] = safety_mode

        return self._request("POST", "/complete", data=data)

    # === Feedback Methods ===

    def give_feedback(
        self,
        target_action_id: str,
        rating: int,
        note: Optional[str] = None,
        user_id: str = "default",
    ) -> dict[str, Any]:
        """
        Submit feedback for an action.

        Args:
            target_action_id: ID of the action to rate (audit_id)
            rating: Rating from 1-5
            note: Optional text feedback
            user_id: User identifier

        Returns:
            Updated LUT (Look-Up Table) with style adjustments
        """
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")

        data = {
            "target_action_id": target_action_id,
            "rating": rating,
            "note": note or "",
            "user_id": user_id,
        }

        response = self._request("POST", "/feedback/card", data=data)
        return response.get("lut", {})

    def get_feedback_lut(self) -> dict[str, Any]:
        """Get current feedback LUT (style adjustments)"""
        return self._request("GET", "/feedback/lut")

    def check_health(self) -> dict[str, Any]:
        """Check system health status"""
        return self._request("GET", "/feedback/health")

    # === Audit Methods ===

    def get_audit(self, audit_id: str) -> dict[str, Any]:
        """
        Retrieve audit details for a specific action.

        Args:
            audit_id: Audit identifier

        Returns:
            Audit bundle with signals, params, and explanation
        """
        return self._request("GET", f"/audit/{audit_id}")

    def log_audit(self, bundle: dict[str, Any]) -> dict[str, Any]:
        """
        Log an audit bundle (for custom integrations).

        Args:
            bundle: Audit data with audit_id, signals, params, etc.

        Returns:
            Confirmation response
        """
        if "audit_id" not in bundle:
            raise ValueError("Audit bundle must include audit_id")

        return self._request("POST", "/audit/log", data=bundle)

    # === Tools Methods ===

    def get_tools_registry(self) -> dict[str, Any]:
        """Get all available tool schemas"""
        return self._request("GET", "/tools/registry")

    def get_tool_names(self) -> list[str]:
        """Get list of available tool names"""
        response = self._request("GET", "/tools/available")
        return response.get("tools", [])

    def get_tool_schema(self, tool_name: str) -> dict[str, Any]:
        """Get schema for a specific tool"""
        return self._request("GET", f"/tools/{tool_name}")

    # === Admin Methods (requires API key) ===

    def get_admin_summary(self, window_seconds: int = 86400) -> dict[str, Any]:
        """
        Get admin summary (requires FLAG_ADMIN_DASHBOARD=true).

        Args:
            window_seconds: Time window for statistics (default 24h)

        Returns:
            Summary with safety modes and tool usage
        """
        params = {"window_s": window_seconds}
        return self._request("GET", "/admin/summary.json", params=params)

    def get_incidents(self, format: str = "json") -> Union[dict, str]:
        """
        Get security incidents.

        Args:
            format: Response format (json or csv)

        Returns:
            Incidents data in requested format
        """
        endpoint = "/admin/incidents.csv" if format == "csv" else "/admin/incidents"
        response = self._request("GET", endpoint)
        return response

    # === Convenience Methods ===

    def set_feature_flag(self, flag_name: str, value: bool) -> None:
        """
        Set a feature flag (local override only).

        Note: This only affects the client's view of flags,
        not the server configuration.
        """
        # Store as client state for header injection
        if not hasattr(self, "_feature_flags"):
            self._feature_flags = {}
        self._feature_flags[flag_name] = value

        # Update session headers
        self.session.headers[f"X-Feature-{flag_name}"] = str(value).lower()

    def batch_complete(
        self,
        messages: list[str],
        shared_context: Optional[list[str]] = None,
        shared_signals: Optional[dict[str, float]] = None,
    ) -> list[dict[str, Any]]:
        """
        Process multiple messages with shared context/signals.

        Args:
            messages: List of messages to process
            shared_context: Context shared across all messages
            shared_signals: Signals shared across all messages

        Returns:
            List of completion responses
        """
        results = []
        for message in messages:
            try:
                result = self.complete(
                    message=message,
                    context=shared_context,
                    signals=shared_signals,
                )
                results.append(result)
                # Small delay to avoid rate limiting
                time.sleep(0.1)
            except Exception as e:
                results.append({"error": str(e), "message": message})

        return results

    def interactive_session(self) -> None:
        """
        Start an interactive session with the LUKHAS system.
        Simple REPL for testing.
        """
        print("=== LUKHAS PWM Interactive Session ===")
        print("Type 'quit' to exit, 'help' for commands")
        print()

        session_context = []
        session_signals = {}

        while True:
            try:
                user_input = input("You: ").strip()

                if user_input.lower() == "quit":
                    print("Goodbye!")
                    break

                elif user_input.lower() == "help":
                    print("\nCommands:")
                    print("  quit - Exit session")
                    print("  help - Show this help")
                    print("  !context add <text> - Add to context")
                    print("  !context clear - Clear context")
                    print("  !signal <name> <value> - Set signal (0.0-1.0)")
                    print("  !audit <id> - View audit details")
                    print("  !feedback <id> <rating> [note] - Give feedback")
                    print()
                    continue

                elif user_input.startswith("!context add "):
                    context_item = user_input[13:]
                    session_context.append(context_item)
                    print(f"Added to context: {context_item}")
                    continue

                elif user_input == "!context clear":
                    session_context = []
                    print("Context cleared")
                    continue

                elif user_input.startswith("!signal "):
                    parts = user_input[8:].split()
                    if len(parts) == 2:
                        signal_name, signal_value = parts
                        session_signals[signal_name] = float(signal_value)
                        print(f"Set {signal_name} = {signal_value}")
                    continue

                elif user_input.startswith("!audit "):
                    audit_id = user_input[7:]
                    audit = self.get_audit(audit_id)
                    print(json.dumps(audit, indent=2))
                    continue

                elif user_input.startswith("!feedback "):
                    parts = user_input[10:].split(maxsplit=2)
                    if len(parts) >= 2:
                        target_id = parts[0]
                        rating = int(parts[1])
                        note = parts[2] if len(parts) > 2 else None
                        lut = self.give_feedback(target_id, rating, note)
                        print(f"Feedback submitted. LUT updated: {lut}")
                    continue

                # Regular message
                response = self.complete(
                    message=user_input,
                    context=session_context,
                    signals=session_signals,
                )

                print(f"\nLUKHAS: {response.get('response', 'No response')}")

                if response.get("audit_id"):
                    print(f"(Audit ID: {response['audit_id']})")

                print()

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
                print()


# === Example Usage ===

if __name__ == "__main__":
    # Example 1: Basic usage
    client = LukhasClient()

    # Check health
    health = client.check_health()
    print(f"System health: {health}")

    # Example 2: Send a message with signals
    response = client.complete(
        message="Help me write a Python function",
        signals={"novelty": 0.7, "stress": 0.2},
        safety_mode="balanced"
    )
    print(f"Response: {response}")

    # Example 3: Give feedback
    if response.get("audit_id"):
        lut = client.give_feedback(
            target_action_id=response["audit_id"],
            rating=4,
            note="Good but could be more detailed"
        )
        print(f"Updated LUT: {lut}")

    # Example 4: Interactive session
    # Uncomment to try:
    # client.interactive_session()
