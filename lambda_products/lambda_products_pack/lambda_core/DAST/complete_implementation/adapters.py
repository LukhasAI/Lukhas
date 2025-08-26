"""
🔗 LUCAS DAST Adapters

Integration adapters for seamless connectivity with external systems,
legacy DAST implementations, and third-party task management tools.
"""

import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp


@dataclass
class AdapterConfig:
    """Configuration for external system adapters"""
    name: str
    endpoint: Optional[str] = None
    auth_token: Optional[str] = None
    rate_limit: int = 100  # requests per minute
    timeout: int = 30  # seconds
    retry_attempts: int = 3
    cache_ttl: int = 300  # seconds

class DASTAdapter:
    """
    🔗 Universal adapter for integrating with existing DAST systems and external tools
    """

    def __init__(self):
        self.adapters: Dict[str, Any] = {}
        self.request_cache: Dict[str, Any] = {}
        self.rate_limiters: Dict[str, List[float]] = {}

    def register_adapter(self, config: AdapterConfig) -> bool:
        """Register a new external system adapter"""
        try:
            adapter_instance = self._create_adapter_instance(config)
            self.adapters[config.name] = {
                "config": config,
                "instance": adapter_instance,
                "status": "active",
                "last_sync": None,
                "error_count": 0
            }
            return True
        except Exception as e:
            print(f"Failed to register adapter {config.name}: {e}")
            return False

    def _create_adapter_instance(self, config: AdapterConfig) -> Dict[str, Any]:
        """Create adapter instance based on configuration"""
        return {
            "sync_tasks": self._create_sync_function(config),
            "push_task": self._create_push_function(config),
            "get_status": self._create_status_function(config)
        }

    def _create_sync_function(self, config: AdapterConfig):
        """Create synchronization function for the adapter"""
        async def sync_tasks() -> List[Dict]:
            if not self._check_rate_limit(config.name, config.rate_limit):
                return []

            try:
                # Check cache first
                cache_key = f"{config.name}:sync_tasks"
                cached_result = self._get_from_cache(cache_key, config.cache_ttl)
                if cached_result:
                    return cached_result

                # Perform actual sync based on adapter type
                if config.name == "jira":
                    tasks = await self._sync_jira_tasks(config)
                elif config.name == "github":
                    tasks = await self._sync_github_issues(config)
                elif config.name == "legacy_dast":
                    tasks = await self._sync_legacy_dast(config)
                elif config.name == "trello":
                    tasks = await self._sync_trello_cards(config)
                else:
                    tasks = await self._sync_generic_api(config)

                # Cache the result
                self._cache_result(cache_key, tasks, config.cache_ttl)

                # Update adapter status
                self.adapters[config.name]["last_sync"] = datetime.now()
                self.adapters[config.name]["error_count"] = 0

                return tasks

            except Exception as e:
                self.adapters[config.name]["error_count"] += 1
                print(f"Sync failed for {config.name}: {e}")
                return []

        return sync_tasks

    def _create_push_function(self, config: AdapterConfig):
        """Create push function for the adapter"""
        async def push_task(task_data: Dict) -> bool:
            if not self._check_rate_limit(config.name, config.rate_limit):
                return False

            try:
                if config.name == "jira":
                    return await self._push_to_jira(config, task_data)
                elif config.name == "github":
                    return await self._push_to_github(config, task_data)
                elif config.name == "legacy_dast":
                    return await self._push_to_legacy_dast(config, task_data)
                else:
                    return await self._push_to_generic_api(config, task_data)

            except Exception as e:
                print(f"Push failed for {config.name}: {e}")
                return False

        return push_task

    def _create_status_function(self, config: AdapterConfig):
        """Create status check function for the adapter"""
        async def get_status() -> Dict[str, Any]:
            try:
                adapter_info = self.adapters.get(config.name, {})
                return {
                    "name": config.name,
                    "status": adapter_info.get("status", "unknown"),
                    "last_sync": adapter_info.get("last_sync"),
                    "error_count": adapter_info.get("error_count", 0),
                    "rate_limit_remaining": self._get_rate_limit_remaining(config.name, config.rate_limit)
                }
            except Exception as e:
                return {
                    "name": config.name,
                    "status": "error",
                    "error": str(e)
                }

        return get_status

    # ========================================
    # 🔄 SPECIFIC ADAPTER IMPLEMENTATIONS
    # ========================================

    async def _sync_jira_tasks(self, config: AdapterConfig) -> List[Dict]:
        """Sync tasks from Jira"""
        if not config.endpoint or not config.auth_token:
            return []

        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {config.auth_token}",
                "Content-Type": "application/json"
            }

            # Query for assigned issues
            jql = "assignee = currentUser() AND status != Done"
            url = f"{config.endpoint}/rest/api/3/search"
            params = {"jql": jql, "maxResults": 50}

            async with session.get(url, headers=headers, params=params, timeout=config.timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._convert_jira_to_dast_format(data.get("issues", []))

        return []

    async def _sync_github_issues(self, config: AdapterConfig) -> List[Dict]:
        """Sync issues from GitHub"""
        if not config.endpoint or not config.auth_token:
            return []

        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"token {config.auth_token}",
                "Accept": "application/vnd.github.v3+json"
            }

            # Get assigned issues
            url = f"{config.endpoint}/issues"
            params = {"assignee": "user", "state": "open", "per_page": 50}

            async with session.get(url, headers=headers, params=params, timeout=config.timeout) as response:
                if response.status == 200:
                    issues = await response.json()
                    return self._convert_github_to_dast_format(issues)

        return []

    async def _sync_legacy_dast(self, config: AdapterConfig) -> List[Dict]:
        """Sync from legacy DAST implementation"""
        # This would connect to existing DAST database or API
        try:
            # Simulate legacy DAST data format
            legacy_tasks = [
                {
                    "id": "legacy_001",
                    "title": "Legacy Task 1",
                    "description": "Description from legacy system",
                    "priority": "high",
                    "status": "in_progress",
                    "created_date": "2025-05-29T10:00:00Z"
                }
            ]

            return self._convert_legacy_to_dast_format(legacy_tasks)

        except Exception as e:
            print(f"Legacy DAST sync error: {e}")
            return []

    async def _sync_trello_cards(self, config: AdapterConfig) -> List[Dict]:
        """Sync cards from Trello"""
        if not config.endpoint or not config.auth_token:
            return []

        # Trello API implementation would go here
        return []

    async def _sync_generic_api(self, config: AdapterConfig) -> List[Dict]:
        """Generic API sync for unknown systems"""
        if not config.endpoint:
            return []

        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {config.auth_token}"} if config.auth_token else {}

            async with session.get(config.endpoint, headers=headers, timeout=config.timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._convert_generic_to_dast_format(data)

        return []

    # ========================================
    # 📤 PUSH IMPLEMENTATIONS
    # ========================================

    async def _push_to_jira(self, config: AdapterConfig, task_data: Dict) -> bool:
        """Push task to Jira"""
        if not config.endpoint or not config.auth_token:
            return False

        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {config.auth_token}",
                "Content-Type": "application/json"
            }

            # Convert DAST task to Jira format
            jira_task = self._convert_dast_to_jira_format(task_data)

            url = f"{config.endpoint}/rest/api/3/issue"

            async with session.post(url, headers=headers, json=jira_task, timeout=config.timeout) as response:
                return response.status in [200, 201]

    async def _push_to_github(self, config: AdapterConfig, task_data: Dict) -> bool:
        """Push task to GitHub as issue"""
        if not config.endpoint or not config.auth_token:
            return False

        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"token {config.auth_token}",
                "Accept": "application/vnd.github.v3+json"
            }

            # Convert DAST task to GitHub issue format
            github_issue = self._convert_dast_to_github_format(task_data)

            url = f"{config.endpoint}/issues"

            async with session.post(url, headers=headers, json=github_issue, timeout=config.timeout) as response:
                return response.status in [200, 201]

    async def _push_to_legacy_dast(self, config: AdapterConfig, task_data: Dict) -> bool:
        """Push task to legacy DAST system"""
        try:
            # Convert to legacy format and store
            legacy_task = self._convert_dast_to_legacy_format(task_data)
            # In real implementation, this would write to legacy database
            return True
        except Exception:
            return False

    async def _push_to_generic_api(self, config: AdapterConfig, task_data: Dict) -> bool:
        """Generic API push"""
        if not config.endpoint:
            return False

        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {config.auth_token}"} if config.auth_token else {}

            async with session.post(config.endpoint, headers=headers, json=task_data, timeout=config.timeout) as response:
                return response.status in [200, 201]

    # ========================================
    # 🔄 FORMAT CONVERTERS
    # ========================================

    def _convert_jira_to_dast_format(self, jira_issues: List[Dict]) -> List[Dict]:
        """Convert Jira issues to DAST format"""
        dast_tasks = []

        for issue in jira_issues:
            dast_task = {
                "id": f"jira_{issue['key']}",
                "title": issue['fields']['summary'],
                "description": issue['fields'].get('description', ''),
                "priority": self._map_jira_priority(issue['fields'].get('priority', {}).get('name', 'Medium')),
                "status": self._map_jira_status(issue['fields']['status']['name']),
                "tags": ["jira", issue['fields']['issuetype']['name'].lower()],
                "context": {
                    "source": "jira",
                    "external_id": issue['key'],
                    "external_url": issue['self']
                },
                "created_at": issue['fields']['created']
            }
            dast_tasks.append(dast_task)

        return dast_tasks

    def _convert_github_to_dast_format(self, github_issues: List[Dict]) -> List[Dict]:
        """Convert GitHub issues to DAST format"""
        dast_tasks = []

        for issue in github_issues:
            labels = [label['name'] for label in issue.get('labels', [])]

            dast_task = {
                "id": f"github_{issue['number']}",
                "title": issue['title'],
                "description": issue.get('body', ''),
                "priority": self._map_github_priority(labels),
                "status": "pending",  # GitHub issues are typically open
                "tags": ["github"] + labels,
                "context": {
                    "source": "github",
                    "external_id": issue['number'],
                    "external_url": issue['html_url']
                },
                "created_at": issue['created_at']
            }
            dast_tasks.append(dast_task)

        return dast_tasks

    def _convert_legacy_to_dast_format(self, legacy_tasks: List[Dict]) -> List[Dict]:
        """Convert legacy DAST tasks to new format"""
        dast_tasks = []

        for task in legacy_tasks:
            dast_task = {
                "id": f"legacy_{task['id']}",
                "title": task['title'],
                "description": task.get('description', ''),
                "priority": task.get('priority', 'medium'),
                "status": task.get('status', 'pending'),
                "tags": ["legacy"] + task.get('tags', []),
                "context": {
                    "source": "legacy_dast",
                    "external_id": task['id'],
                    "migrated": True
                },
                "created_at": task.get('created_date', datetime.now().isoformat())
            }
            dast_tasks.append(dast_task)

        return dast_tasks

    def _convert_generic_to_dast_format(self, generic_data: Any) -> List[Dict]:
        """Convert generic API data to DAST format"""
        if isinstance(generic_data, list):
            return [self._convert_single_generic_item(item) for item in generic_data]
        elif isinstance(generic_data, dict):
            return [self._convert_single_generic_item(generic_data)]
        else:
            return []

    def _convert_single_generic_item(self, item: Dict) -> Dict:
        """Convert single generic item to DAST format"""
        return {
            "id": f"generic_{item.get('id', 'unknown')}",
            "title": item.get('title', item.get('name', 'Untitled')),
            "description": item.get('description', ''),
            "priority": item.get('priority', 'medium'),
            "status": item.get('status', 'pending'),
            "tags": ["external"] + item.get('tags', []),
            "context": {
                "source": "generic_api",
                "original_data": item
            },
            "created_at": item.get('created_at', datetime.now().isoformat())
        }

    def _convert_dast_to_jira_format(self, dast_task: Dict) -> Dict:
        """Convert DAST task to Jira format"""
        return {
            "fields": {
                "project": {"key": "TASK"},  # Would be configurable
                "summary": dast_task['title'],
                "description": dast_task.get('description', ''),
                "issuetype": {"name": "Task"},
                "priority": {"name": self._map_dast_to_jira_priority(dast_task.get('priority', 'medium'))}
            }
        }

    def _convert_dast_to_github_format(self, dast_task: Dict) -> Dict:
        """Convert DAST task to GitHub issue format"""
        return {
            "title": dast_task['title'],
            "body": dast_task.get('description', ''),
            "labels": dast_task.get('tags', [])
        }

    def _convert_dast_to_legacy_format(self, dast_task: Dict) -> Dict:
        """Convert DAST task to legacy format"""
        return {
            "id": dast_task['id'],
            "title": dast_task['title'],
            "description": dast_task.get('description', ''),
            "priority": dast_task.get('priority', 'medium'),
            "status": dast_task.get('status', 'pending'),
            "tags": dast_task.get('tags', []),
            "created_date": dast_task.get('created_at', datetime.now().isoformat())
        }

    # ========================================
    # 🗺️ PRIORITY & STATUS MAPPING
    # ========================================

    def _map_jira_priority(self, jira_priority: str) -> str:
        """Map Jira priority to DAST priority"""
        mapping = {
            "Highest": "critical",
            "High": "high",
            "Medium": "medium",
            "Low": "low",
            "Lowest": "low"
        }
        return mapping.get(jira_priority, "medium")

    def _map_jira_status(self, jira_status: str) -> str:
        """Map Jira status to DAST status"""
        mapping = {
            "To Do": "pending",
            "In Progress": "in_progress",
            "In Review": "blocked",
            "Done": "completed",
            "Closed": "completed"
        }
        return mapping.get(jira_status, "pending")

    def _map_github_priority(self, labels: List[str]) -> str:
        """Map GitHub labels to DAST priority"""
        priority_labels = {
            "critical": "critical",
            "high": "high",
            "medium": "medium",
            "low": "low",
            "urgent": "critical",
            "bug": "high"
        }

        for label in labels:
            if label.lower() in priority_labels:
                return priority_labels[label.lower()]

        return "medium"

    def _map_dast_to_jira_priority(self, dast_priority: str) -> str:
        """Map DAST priority to Jira priority"""
        mapping = {
            "critical": "Highest",
            "high": "High",
            "medium": "Medium",
            "low": "Low"
        }
        return mapping.get(dast_priority, "Medium")

    # ========================================
    # 🚦 RATE LIMITING & CACHING
    # ========================================

    def _check_rate_limit(self, adapter_name: str, rate_limit: int) -> bool:
        """Check if request is within rate limit"""
        current_time = time.time()

        if adapter_name not in self.rate_limiters:
            self.rate_limiters[adapter_name] = []

        # Remove old requests (older than 1 minute)
        self.rate_limiters[adapter_name] = [
            req_time for req_time in self.rate_limiters[adapter_name]
            if current_time - req_time < 60
        ]

        # Check if we're under the limit
        if len(self.rate_limiters[adapter_name]) >= rate_limit:
            return False

        # Add current request
        self.rate_limiters[adapter_name].append(current_time)
        return True

    def _get_rate_limit_remaining(self, adapter_name: str, rate_limit: int) -> int:
        """Get remaining rate limit for adapter"""
        if adapter_name not in self.rate_limiters:
            return rate_limit

        return rate_limit - len(self.rate_limiters[adapter_name])

    def _get_from_cache(self, cache_key: str, ttl: int) -> Optional[Any]:
        """Get item from cache if not expired"""
        if cache_key in self.request_cache:
            cached_item = self.request_cache[cache_key]
            if time.time() - cached_item["timestamp"] < ttl:
                return cached_item["data"]

        return None

    def _cache_result(self, cache_key: str, data: Any, ttl: int):
        """Cache result with timestamp"""
        self.request_cache[cache_key] = {
            "data": data,
            "timestamp": time.time()
        }

        # Clean old cache entries
        current_time = time.time()
        expired_keys = [
            key for key, value in self.request_cache.items()
            if current_time - value["timestamp"] > ttl * 2  # Keep cache for 2x TTL
        ]

        for key in expired_keys:
            del self.request_cache[key]

    # ========================================
    # 🔄 BULK OPERATIONS
    # ========================================

    async def sync_all_adapters(self) -> Dict[str, Any]:
        """Sync all registered adapters"""
        results = {}

        for adapter_name, adapter_info in self.adapters.items():
            try:
                sync_function = adapter_info["instance"]["sync_tasks"]
                tasks = await sync_function()
                results[adapter_name] = {
                    "status": "success",
                    "task_count": len(tasks),
                    "tasks": tasks
                }
            except Exception as e:
                results[adapter_name] = {
                    "status": "error",
                    "error": str(e),
                    "task_count": 0
                }

        return results

    async def get_adapter_status_all(self) -> Dict[str, Any]:
        """Get status of all adapters"""
        statuses = {}

        for adapter_name, adapter_info in self.adapters.items():
            try:
                status_function = adapter_info["instance"]["get_status"]
                status = await status_function()
                statuses[adapter_name] = status
            except Exception as e:
                statuses[adapter_name] = {
                    "name": adapter_name,
                    "status": "error",
                    "error": str(e)
                }

        return statuses
