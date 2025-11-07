#!/usr/bin/env python3
"""
Jules API Wrapper for LUKHAS AI Agent Integration
=================================================

Google Jules is an AI coding agent that can understand codebases, create plans,
and execute changes autonomously. This wrapper integrates Jules capabilities
into LUKHAS orchestration workflows.

API Documentation: https://developers.google.com/jules/api

Features:
- Session-based interaction with code repositories
- Automated plan approval and PR creation
- Activity streaming and progress tracking
- Multi-source repository support

Usage:
    from bridge.llm_wrappers.jules_wrapper import JulesClient

    client = JulesClient(api_key="your-api-key")

    # Create a session with a coding task
    session = await client.create_session(
        prompt="Write comprehensive tests for core orchestration module",
        source_id="github.com/your-org/your-repo",
        automation_mode="AUTO_CREATE_PR"
    )

    # Monitor activities
    async for activity in client.stream_activities(session["name"]):
        print(f"Activity: {activity['type']} - {activity.get('message', '')}")
"""
from __future__ import annotations

import asyncio
import logging
import os
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from typing import Any

import aiohttp
from pydantic import BaseModel, Field

# Import keychain manager for secure API key storage
try:
    from core.security.keychain_manager import get_jules_api_key
    KEYCHAIN_AVAILABLE = True
except ImportError:
    KEYCHAIN_AVAILABLE = False
    get_jules_api_key = None

logger = logging.getLogger(__name__)


class JulesConfig(BaseModel):
    """Configuration for Jules API client."""

    api_key: str = Field(..., description="Jules API key from Settings page")
    base_url: str = Field(
        default="https://jules.googleapis.com",
        description="Jules API base URL"
    )
    timeout: int = Field(default=300, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    auto_approve_plans: bool = Field(
        default=False,
        description="Automatically approve generated plans"
    )


class JulesSource(BaseModel):
    """Represents a connected repository source."""

    name: str = Field(..., description="Resource name (e.g., sources/123)")
    display_name: Optional[str] = Field(None, description="Human-readable source name")
    repository_url: Optional[str] = Field(None, description="Repository URL")
    create_time: Optional[datetime] = Field(None, description="Creation timestamp")


class JulesSession(BaseModel):
    """Represents a Jules coding session."""

    name: str = Field(..., description="Session resource name")
    display_name: str = Field(..., description="Session display name")
    state: str = Field(..., description="Session state (ACTIVE, COMPLETED, etc.)")
    create_time: datetime = Field(..., description="Creation timestamp")
    prompt: Optional[str] = Field(None, description="Initial prompt")
    require_plan_approval: bool = Field(
        default=False,
        description="Whether plan approval is required"
    )


class JulesActivity(BaseModel):
    """Represents an activity within a Jules session."""

    name: str = Field(..., description="Activity resource name")
    type: str = Field(..., description="Activity type (PLAN, MESSAGE, etc.)")
    create_time: datetime = Field(..., description="Creation timestamp")
    originator: str = Field(..., description="Who created the activity (AGENT/USER)")
    message: Optional[str] = Field(None, description="Activity message text")
    artifacts: dict[str, Optional[Any]] = Field(
        None,
        description="Activity artifacts (code changes, etc.)"
    )


class JulesClient:
    """
    Async client for Google Jules API integration.

    Provides session management, plan approval, activity streaming,
    and automated PR creation for AI-driven coding tasks.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        config: Optional[JulesConfig] = None
    ):
        """
        Initialize Jules API client.

        Args:
            api_key: Jules API key (or use JULES_API_KEY env var or macOS Keychain)
            config: Optional JulesConfig object for advanced configuration

        Raises:
            ValueError: If no API key can be found

        Note:
            API key lookup order:
            1. Explicit api_key parameter
            2. macOS Keychain (if available)
            3. JULES_API_KEY environment variable
            4. Raise ValueError if none found
        """
        if config:
            self.config = config
        else:
            # Try to get API key from multiple sources
            if not api_key:
                # 1. Try macOS Keychain first (most secure)
                if KEYCHAIN_AVAILABLE and get_jules_api_key:
                    api_key = get_jules_api_key()
                    if api_key:
                        logger.debug("Using Jules API key from macOS Keychain")

                # 2. Fallback to environment variable
                if not api_key:
                    api_key = os.getenv("JULES_API_KEY")
                    if api_key:
                        logger.debug("Using Jules API key from environment variable")

                # 3. Since Jules is a Google service, try GOOGLE_API_KEY as fallback
                if not api_key:
                    api_key = os.getenv("GOOGLE_API_KEY")
                    if api_key:
                        logger.debug("Using GOOGLE_API_KEY for Jules (Google service)")
                    elif KEYCHAIN_AVAILABLE:
                        try:
                            from core.security.keychain_manager import KeychainManager
                            api_key = KeychainManager.get_key("GOOGLE_API_KEY", fallback_to_env=False)
                            if api_key:
                                logger.debug("Using GOOGLE_API_KEY from Keychain for Jules")
                        except Exception:
                            pass

            if not api_key:
                raise ValueError(
                    "Jules API key required. Options:\n"
                    "1. Store in macOS Keychain: python scripts/setup_api_keys.py\n"
                    "2. Set environment variable: export JULES_API_KEY=your-key\n"
                    "3. Pass api_key parameter to JulesClient()"
                )

            self.config = JulesConfig(api_key=api_key)

        self._session: aiohttp.Optional[ClientSession] = None
        self.logger = logging.getLogger(f"{__name__}.JulesClient")

    async def __aenter__(self) -> JulesClient:
        """Async context manager entry."""
        self._session = aiohttp.ClientSession(
            headers={
                "X-Goog-Api-Key": self.config.api_key,
                "Content-Type": "application/json",
            },
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._session:
            await self._session.close()

    def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None:
            raise RuntimeError(
                "JulesClient must be used as async context manager: "
                "async with JulesClient() as client: ..."
            )
        return self._session

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any
    ) -> dict[str, Any]:
        """
        Make authenticated API request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional request parameters

        Returns:
            JSON response as dictionary
        """
        url = f"{self.config.base_url}{endpoint}"
        session = self._get_session()

        for attempt in range(self.config.max_retries):
            try:
                async with session.request(method, url, **kwargs) as response:
                    if response.status >= 400:
                        # Try to get error details from response body
                        try:
                            error_body = await response.text()
                            self.logger.error(f"API error response ({response.status}): {error_body}")
                        except (aiohttp.ClientError, UnicodeDecodeError):
                            pass
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientError as e:
                self.logger.warning(
                    f"Request failed (attempt {attempt + 1}/{self.config.max_retries}): {e}"
                )
                if attempt == self.config.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

        raise RuntimeError("Max retries exceeded")

    async def list_sources(self) -> list[JulesSource]:
        """
        List all connected repository sources.

        Returns:
            List of JulesSource objects representing connected repos

        Example:
            sources = await client.list_sources()
            for source in sources:
                print(f"{source.display_name}: {source.repository_url}")
        """
        response = await self._request("GET", "/v1alpha/sources")
        sources = response.get("sources", [])
        return [JulesSource(**source) for source in sources]

    async def get_source_by_url(self, repository_url: str) -> Optional[JulesSource]:
        """
        Find a source by repository URL.

        Args:
            repository_url: Repository URL to search for

        Returns:
            JulesSource if found, None otherwise
        """
        sources = await self.list_sources()
        for source in sources:
            if source.repository_url == repository_url:
                return source
        return None

    async def create_session(
        self,
        prompt: str,
        source_id: Optional[str] = None,
        repository_url: Optional[str] = None,
        display_name: Optional[str] = None,
        automation_mode: Optional[str] = None,
        require_plan_approval: Optional[bool] = None
    ) -> dict[str, Any]:
        """
        Create a new Jules coding session.

        Args:
            prompt: Task description for Jules agent
            source_id: Source resource name (e.g., "sources/123")
            repository_url: Alternative to source_id - will look up source
            display_name: Optional session name
            automation_mode: "AUTO_CREATE_PR" for automatic PR creation
            require_plan_approval: Whether to require explicit plan approval

        Returns:
            Session resource as dictionary

        Example:
            session = await client.create_session(
                prompt="Fix all E402 import ordering violations",
                repository_url="https://github.com/LukhasAI/Lukhas",
                automation_mode="AUTO_CREATE_PR"
            )
        """
        # Resolve source_id from repository_url if needed
        if not source_id and repository_url:
            source = await self.get_source_by_url(repository_url)
            if not source:
                raise ValueError(
                    f"No source found for repository: {repository_url}. "
                    "Connect the repository in Jules app first."
                )
            source_id = source.name

        if not source_id:
            raise ValueError("Either source_id or repository_url must be provided")

        # Build payload according to official Jules API documentation
        # https://developers.google.com/jules/api
        payload: dict[str, Any] = {
            "prompt": prompt,
            "sourceContext": {
                "source": source_id,
                "githubRepoContext": {
                    "startingBranch": "main"
                }
            }
        }

        # Add optional title (displayName)
        if display_name:
            payload["title"] = display_name

        # Add automation mode if specified
        if automation_mode:
            payload["automationMode"] = automation_mode

        # Add plan approval setting
        if require_plan_approval is not None:
            payload["requirePlanApproval"] = require_plan_approval
        elif self.config.auto_approve_plans:
            payload["requirePlanApproval"] = False

        self.logger.debug(f"Creating session with payload: {payload}")
        response = await self._request(
            "POST",
            "/v1alpha/sessions",
            json=payload
        )

        self.logger.info(
            f"Created Jules session: {response.get('name')} - {prompt[:100]}"
        )

        return response

    async def list_sessions(
        self,
        page_size: int = 50,
        page_token: Optional[str] = None
    ) -> dict[str, Any]:
        """
        List Jules sessions with pagination.

        Args:
            page_size: Number of sessions per page
            page_token: Token for pagination

        Returns:
            Dictionary with sessions and nextPageToken
        """
        params = {"pageSize": page_size}
        if page_token:
            params["pageToken"] = page_token

        return await self._request(
            "GET",
            "/v1alpha/sessions",
            params=params
        )

    async def get_session(self, session_id: str) -> dict[str, Any]:
        """
        Get a specific session by ID.

        Args:
            session_id: Session resource name (e.g., "sessions/123")

        Returns:
            Session resource dictionary
        """
        return await self._request("GET", f"/v1alpha/{session_id}")

    async def approve_plan(self, session_id: str) -> dict[str, Any]:
        """
        Approve a session's generated plan.

        Args:
            session_id: Session resource name

        Returns:
            Updated session resource
        """
        self.logger.info(f"Approving plan for session: {session_id}")
        return await self._request(
            "POST",
            f"/v1alpha/{session_id}:approvePlan"
        )

    async def send_message(
        self,
        session_id: str,
        message: str
    ) -> dict[str, Any]:
        """
        Send a message to the Jules agent in a session.

        Args:
            session_id: Session resource name
            message: Message text to send

        Returns:
            Activity resource representing the message
        """
        self.logger.info(f"Sending message to {session_id}: {message[:100]}")
        return await self._request(
            "POST",
            f"/v1alpha/{session_id}:sendMessage",
            json={"message": message}
        )

    async def delete_session(self, session_id: str) -> dict[str, Any]:
        """
        Delete a session.

        Args:
            session_id: Session resource name (e.g., "sessions/123")

        Returns:
            Empty dict on success
        """
        self.logger.info(f"Deleting session: {session_id}")
        return await self._request("DELETE", f"/v1alpha/{session_id}")

    async def list_activities(
        self,
        session_id: str,
        page_size: int = 100,
        page_token: Optional[str] = None
    ) -> dict[str, Any]:
        """
        List activities for a session.

        Args:
            session_id: Session resource name
            page_size: Number of activities per page
            page_token: Token for pagination

        Returns:
            Dictionary with activities and nextPageToken
        """
        params = {"pageSize": page_size}
        if page_token:
            params["pageToken"] = page_token

        return await self._request(
            "GET",
            f"/v1alpha/{session_id}/activities",
            params=params
        )

    async def stream_activities(
        self,
        session_id: str,
        poll_interval: float = 2.0,
        timeout: Optional[float] = None
    ) -> AsyncIterator[JulesActivity]:
        """
        Stream activities from a session with polling.

        Args:
            session_id: Session resource name
            poll_interval: Seconds between polls
            timeout: Optional timeout in seconds

        Yields:
            JulesActivity objects as they occur

        Example:
            async for activity in client.stream_activities(session["name"]):
                if activity.type == "MESSAGE":
                    print(f"Agent: {activity.message}")
                elif activity.type == "PLAN":
                    print("Plan created - awaiting approval")
        """
        seen_activities: set[str] = set()
        start_time = datetime.now(timezone.utc).timestamp()

        while True:
            if timeout and (datetime.now(timezone.utc).timestamp() - start_time) > timeout:
                break

            try:
                response = await self.list_activities(session_id)
                activities = response.get("activities", [])

                for activity_data in activities:
                    activity = JulesActivity(**activity_data)
                    if activity.name not in seen_activities:
                        seen_activities.add(activity.name)
                        yield activity

                # Check if session is complete
                session = await self.get_session(session_id)
                if session.get("state") in ("COMPLETED", "FAILED", "CANCELLED"):
                    self.logger.info(
                        f"Session {session_id} ended with state: {session['state']}"
                    )
                    break

            except Exception as e:
                self.logger.error(f"Error streaming activities: {e}")
                break

            await asyncio.sleep(poll_interval)

    async def approve_plan(self, session_id: str) -> dict[str, Any]:
        """
        Approve the latest plan in a session.

        Args:
            session_id: Session resource name (e.g., "sessions/123")

        Returns:
            Response dictionary (typically empty as per API docs)

        Example:
            await client.approve_plan("sessions/123")
        """
        response = await self._request(
            "POST",
            f"/v1alpha/{session_id}:approvePlan",
            json={}
        )

        self.logger.info(f"Approved plan for session: {session_id}")
        return response

    async def send_message(
        self,
        session_id: str,
        message: str
    ) -> dict[str, Any]:
        """
        Send a message/feedback to a Jules session.

        Args:
            session_id: Session resource name (e.g., "sessions/123")
            message: Your message or feedback to Jules

        Returns:
            Response dictionary (typically empty - check activities for reply)

        Note:
            The agent's response appears as the next activity in the session.
            Poll activities to see Jules' reply.

        Example:
            await client.send_message(
                "sessions/123",
                "Use lukhas.* imports instead of core.* imports"
            )
        """
        payload = {"prompt": message}

        response = await self._request(
            "POST",
            f"/v1alpha/{session_id}:sendMessage",
            json=payload
        )

        self.logger.info(
            f"Sent message to session {session_id}: {message[:50]}..."
        )
        return response


# Convenience functions for quick usage
async def create_jules_session(
    prompt: str,
    repository_url: str,
    api_key: Optional[str] = None,
    auto_create_pr: bool = True
) -> dict[str, Any]:
    """
    Convenience function to quickly create a Jules session.

    Args:
        prompt: Task description
        repository_url: Repository URL
        api_key: Optional API key (uses env var if not provided)
        auto_create_pr: Whether to automatically create PR

    Returns:
        Session resource dictionary
    """
    async with JulesClient(api_key=api_key) as client:
        return await client.create_session(
            prompt=prompt,
            repository_url=repository_url,
            automation_mode="AUTO_CREATE_PR" if auto_create_pr else None
        )


async def monitor_jules_session(
    session_id: str,
    api_key: Optional[str] = None,
    timeout: Optional[float] = 3600.0
) -> list[JulesActivity]:
    """
    Monitor a Jules session until completion.

    Args:
        session_id: Session resource name
        api_key: Optional API key
        timeout: Maximum time to wait in seconds (default 1 hour)

    Returns:
        List of all activities from the session
    """
    activities = []
    async with JulesClient(api_key=api_key) as client:
        async for activity in client.stream_activities(session_id, timeout=timeout):
            activities.append(activity)
            logger.info(
                f"[{activity.type}] {activity.originator}: "
                f"{activity.message or 'No message'}"
            )
    return activities
