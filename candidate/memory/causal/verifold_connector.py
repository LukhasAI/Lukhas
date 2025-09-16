"""

#TAG:memory
#TAG:causal
#TAG:neuroplastic
#TAG:colony


VeriFold Connector
==================

Connection interface to VeriFold replay chain for secure session
and activity replay across the LUKHAS ecosystem.

Features:
- Chain integration
- Secure replay sessions
- Cross-service continuity
- Verification protocols
"""


class VeriFoldConnector:
    """Interface to VeriFold replay chain"""

    def __init__(self, config):
        self.config = config
        self.chain_endpoint = config.get("verifold_endpoint", "https://verifold.lukhas.ai")
        self.connection_pool = {}
        self.max_retries = config.get("max_retries", 3)
        self.timeout = config.get("timeout", 30)
        self.api_key = config.get("api_key")
        self.session_cache = {}

    def connect_to_chain(self):
        """Establish connection to VeriFold chain"""
        import time

        import requests

        connection_id = f"conn_{int(time.time())}"

        try:
            # Establish connection to VeriFold chain
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}" if self.api_key else ""
            }

            response = requests.post(
                f"{self.chain_endpoint}/api/v1/connect",
                headers=headers,
                json={"connection_id": connection_id, "client_type": "lukhas_memory"},
                timeout=self.timeout
            )

            if response.status_code == 200:
                connection_data = response.json()
                self.connection_pool[connection_id] = {
                    "status": "active",
                    "session_token": connection_data.get("session_token"),
                    "chain_height": connection_data.get("chain_height", 0),
                    "connected_at": time.time()
                }
                return connection_id
            else:
                raise Exception(f"Failed to connect to VeriFold chain: {response.status_code}")

        except Exception as e:
            print(f"VeriFold connection failed: {e}")
            return None

    def submit_replay_session(self, session_data):
        """Submit session data to VeriFold chain"""
        import hashlib
        import json
        import time

        import requests

        # Generate session hash for integrity
        session_hash = hashlib.sha256(
            json.dumps(session_data, sort_keys=True).encode()
        ).hexdigest()

        # Find active connection
        active_conn = None
        for conn_id, conn_data in self.connection_pool.items():
            if conn_data.get("status") == "active":
                active_conn = conn_data
                break

        if not active_conn:
            # Try to establish new connection
            conn_id = self.connect_to_chain()
            if not conn_id:
                return {"status": "error", "message": "No active connection"}
            active_conn = self.connection_pool[conn_id]

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {active_conn['session_token']}"
            }

            payload = {
                "session_id": session_data.get("session_id"),
                "session_hash": session_hash,
                "memory_folds": session_data.get("memory_folds", []),
                "causal_chains": session_data.get("causal_chains", []),
                "timestamp": time.time(),
                "metadata": session_data.get("metadata", {})
            }

            response = requests.post(
                f"{self.chain_endpoint}/api/v1/sessions",
                headers=headers,
                json=payload,
                timeout=self.timeout
            )

            if response.status_code == 201:
                result = response.json()
                self.session_cache[session_data.get("session_id")] = {
                    "chain_id": result.get("chain_id"),
                    "block_hash": result.get("block_hash"),
                    "submitted_at": time.time()
                }
                return {"status": "success", "chain_id": result.get("chain_id")}
            else:
                return {"status": "error", "message": f"Submission failed: {response.status_code}"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def retrieve_replay_data(self, session_id):
        """Retrieve replay data from VeriFold chain"""
        import requests

        # Check cache first
        if session_id in self.session_cache:
            cached_data = self.session_cache[session_id]
            chain_id = cached_data.get("chain_id")
        else:
            return {"status": "error", "message": "Session not found in cache"}

        # Find active connection
        active_conn = None
        for conn_data in self.connection_pool.values():
            if conn_data.get("status") == "active":
                active_conn = conn_data
                break

        if not active_conn:
            return {"status": "error", "message": "No active connection"}

        try:
            headers = {
                "Authorization": f"Bearer {active_conn['session_token']}"
            }

            response = requests.get(
                f"{self.chain_endpoint}/api/v1/sessions/{session_id}",
                headers=headers,
                timeout=self.timeout
            )

            if response.status_code == 200:
                replay_data = response.json()
                return {
                    "status": "success",
                    "session_id": session_id,
                    "chain_id": chain_id,
                    "replay_data": replay_data,
                    "retrieved_at": self._get_timestamp()
                }
            elif response.status_code == 404:
                return {"status": "error", "message": "Session not found on chain"}
            else:
                return {"status": "error", "message": f"Retrieval failed: {response.status_code}"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def verify_chain_integrity(self):
        """Verify VeriFold chain integrity"""
        import requests

        # Find active connection
        active_conn = None
        for conn_data in self.connection_pool.values():
            if conn_data.get("status") == "active":
                active_conn = conn_data
                break

        if not active_conn:
            return {"status": "error", "message": "No active connection"}

        try:
            headers = {
                "Authorization": f"Bearer {active_conn['session_token']}"
            }

            # Get chain info
            response = requests.get(
                f"{self.chain_endpoint}/api/v1/chain/info",
                headers=headers,
                timeout=self.timeout
            )

            if response.status_code != 200:
                return {"status": "error", "message": "Failed to get chain info"}

            chain_info = response.json()

            # Verify latest blocks
            blocks_response = requests.get(
                f"{self.chain_endpoint}/api/v1/chain/blocks/latest/10",
                headers=headers,
                timeout=self.timeout
            )

            if blocks_response.status_code != 200:
                return {"status": "error", "message": "Failed to get latest blocks"}

            blocks = blocks_response.json()

            # Verify block chain integrity
            integrity_score = self._verify_block_chain(blocks)

            return {
                "status": "success",
                "chain_height": chain_info.get("height", 0),
                "total_blocks": len(blocks),
                "integrity_score": integrity_score,
                "last_block_hash": blocks[0].get("hash") if blocks else None,
                "verified_at": self._get_timestamp()
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _verify_block_chain(self, blocks):
        """Verify integrity of block chain"""
        if not blocks or len(blocks) < 2:
            return 1.0  # Single block or empty chain is valid

        valid_connections = 0
        total_connections = len(blocks) - 1

        for i in range(len(blocks) - 1):
            current_block = blocks[i]
            previous_block = blocks[i + 1]

            # Verify hash chain
            if current_block.get("previous_hash") == previous_block.get("hash"):
                valid_connections += 1

        return valid_connections / total_connections if total_connections > 0 else 1.0

    def _get_timestamp(self):
        """Get current timestamp"""
        import time
        return time.time()
