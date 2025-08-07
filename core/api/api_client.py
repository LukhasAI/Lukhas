"""
LUKHAS API Client SDK
Easy-to-use client for interacting with LUKHAS Enhanced API
"""

from typing import Dict, Any, Optional, List
import aiohttp
import asyncio
import json
from datetime import datetime
from enum import Enum


class LUKHASClient:
    """
    LUKHAS API Client for easy integration
    
    Example:
        async with LUKHASClient('http://localhost:8000', api_key='your-key') as client:
            # Consciousness query
            response = await client.consciousness.query("What is the meaning of existence?")
            
            # Store memory
            memory_id = await client.memory.store({"event": "Important meeting"})
            
            # Dream generation
            dream = await client.dream.generate("A world without limits")
    """
    
    def __init__(self, base_url: str, api_key: Optional[str] = None, 
                 jwt_token: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.jwt_token = jwt_token
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Sub-clients for different modules
        self.consciousness = ConsciousnessClient(self)
        self.memory = MemoryClient(self)
        self.governance = GovernanceClient(self)
        self.dream = DreamClient(self)
        self.auth = AuthClient(self)
        self.system = SystemClient(self)
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = {
            'Content-Type': 'application/json'
        }
        
        if self.jwt_token:
            headers['Authorization'] = f'Bearer {self.jwt_token}'
        elif self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
            
        return headers
        
    async def _request(self, method: str, endpoint: str, 
                      data: Optional[Dict[str, Any]] = None,
                      params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make HTTP request to API"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
            
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        async with self.session.request(
            method=method,
            url=url,
            headers=headers,
            json=data,
            params=params
        ) as response:
            response_data = await response.json()
            
            if response.status >= 400:
                error = response_data.get('error', response_data)
                raise APIError(
                    f"API Error: {error.get('message', 'Unknown error')}",
                    status_code=response.status,
                    response=response_data
                )
                
            return response_data
            
    async def process(self, operation: str, data: Dict[str, Any], 
                     context: Optional[Dict[str, Any]] = None,
                     options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generic process endpoint"""
        request_data = {
            'operation': operation,
            'data': data,
            'context': context,
            'options': options
        }
        
        return await self._request('POST', '/api/v2/process', data=request_data)


class ConsciousnessClient:
    """Consciousness module client"""
    
    def __init__(self, client: LUKHASClient):
        self.client = client
        
    async def query(self, query: str, awareness_level: float = 0.7,
                   include_emotional_context: bool = True) -> Dict[str, Any]:
        """Query consciousness system"""
        data = {
            'query': query,
            'awareness_level': awareness_level,
            'include_emotional_context': include_emotional_context
        }
        
        response = await self.client._request(
            'POST', 
            '/api/v2/consciousness/query',
            data=data
        )
        
        return response.get('result', response)


class MemoryClient:
    """Memory module client"""
    
    def __init__(self, client: LUKHASClient):
        self.client = client
        
    async def store(self, content: Dict[str, Any], 
                   memory_type: str = 'general') -> str:
        """Store memory"""
        data = {
            'action': 'store',
            'content': content,
            'memory_type': memory_type
        }
        
        response = await self.client._request(
            'POST',
            '/api/v2/memory/store',
            data=data
        )
        
        return response.get('result', {}).get('memory_id')
        
    async def retrieve(self, query: str, 
                      memory_type: str = 'general') -> List[Dict[str, Any]]:
        """Retrieve memories"""
        data = {
            'action': 'retrieve',
            'query': query,
            'memory_type': memory_type
        }
        
        response = await self.client._request(
            'POST',
            '/api/v2/memory/retrieve',
            data=data
        )
        
        return response.get('result', {}).get('results', [])
        
    async def search(self, query: str, 
                    memory_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search memories"""
        data = {
            'action': 'search',
            'query': query,
            'memory_type': memory_type
        }
        
        response = await self.client._request(
            'POST',
            '/api/v2/memory/search',
            data=data
        )
        
        return response.get('result', {}).get('results', [])
        
    async def update(self, query: str, content: Dict[str, Any],
                    memory_type: str = 'general') -> int:
        """Update memories"""
        data = {
            'action': 'update',
            'query': query,
            'content': content,
            'memory_type': memory_type
        }
        
        response = await self.client._request(
            'POST',
            '/api/v2/memory/update',
            data=data
        )
        
        return response.get('result', {}).get('updated_count', 0)


class GovernanceClient:
    """Governance/Guardian module client"""
    
    def __init__(self, client: LUKHASClient):
        self.client = client
        
    async def check_action(self, action_proposal: Dict[str, Any],
                          context: Optional[Dict[str, Any]] = None,
                          urgency: str = 'normal') -> Dict[str, Any]:
        """Check action with Guardian system"""
        data = {
            'action_proposal': action_proposal,
            'context': context or {},
            'urgency': urgency
        }
        
        response = await self.client._request(
            'POST',
            '/api/v2/governance/check',
            data=data
        )
        
        return response.get('result', response)


class DreamClient:
    """Dream/creativity module client"""
    
    def __init__(self, client: LUKHASClient):
        self.client = client
        
    async def generate(self, prompt: str, creativity_level: float = 0.8,
                      dream_type: str = 'creative') -> Dict[str, Any]:
        """Generate creative content"""
        data = {
            'prompt': prompt,
            'creativity_level': creativity_level,
            'dream_type': dream_type
        }
        
        response = await self.client._request(
            'POST',
            '/api/v2/dream/generate',
            data=data
        )
        
        return response.get('result', response)


class AuthClient:
    """Authentication client"""
    
    def __init__(self, client: LUKHASClient):
        self.client = client
        
    async def login(self, user_id: str, password: str,
                   ip_address: Optional[str] = None,
                   user_agent: Optional[str] = None) -> Dict[str, Any]:
        """Login and get session"""
        credentials = {
            'user_id': user_id,
            'auth_token': password,  # In production, hash this
            'ip_address': ip_address or 'unknown',
            'user_agent': user_agent or 'LUKHAS-Client/1.0'
        }
        
        response = await self.client._request(
            'POST',
            '/api/v2/auth/login',
            data=credentials
        )
        
        # Update client token if successful
        if 'jwt_token' in response:
            self.client.jwt_token = response['jwt_token']
            
        return response
        
    async def verify_mfa(self, session_id: str, method: str, code: str) -> Dict[str, Any]:
        """Verify MFA code"""
        data = {
            'session_id': session_id,
            'mfa_data': {
                'method': method,
                'code': code
            }
        }
        
        response = await self.client._request(
            'POST',
            '/api/v2/auth/mfa/verify',
            data=data
        )
        
        # Update token if new one provided
        if 'jwt_token' in response:
            self.client.jwt_token = response['jwt_token']
            
        return response
        
    async def setup_totp(self) -> Dict[str, Any]:
        """Setup TOTP MFA"""
        return await self.client._request('POST', '/api/v2/auth/mfa/setup/totp')


class SystemClient:
    """System information client"""
    
    def __init__(self, client: LUKHASClient):
        self.client = client
        
    async def health(self) -> Dict[str, Any]:
        """Get system health"""
        return await self.client._request('GET', '/api/v2/health')
        
    async def capabilities(self) -> Dict[str, Any]:
        """Get system capabilities"""
        return await self.client._request('GET', '/api/v2/capabilities')
        
    async def metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        return await self.client._request('GET', '/api/v2/metrics')


class APIError(Exception):
    """API Error exception"""
    
    def __init__(self, message: str, status_code: int = 500, 
                 response: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.response = response or {}
        super().__init__(self.message)


# Convenience functions for simple usage
async def create_client(base_url: str, api_key: Optional[str] = None) -> LUKHASClient:
    """Create and return an initialized client"""
    client = LUKHASClient(base_url, api_key=api_key)
    await client.__aenter__()
    return client


# Example usage
async def example_usage():
    """Example of using LUKHAS API client"""
    # Initialize client
    async with LUKHASClient('http://localhost:8000') as client:
        # Login
        auth_response = await client.auth.login('test_user', 'secure_password')
        print(f"Logged in: {auth_response}")
        
        # Query consciousness
        consciousness_response = await client.consciousness.query(
            "What is the nature of artificial consciousness?"
        )
        print(f"Consciousness says: {consciousness_response}")
        
        # Store a memory
        memory_id = await client.memory.store({
            'event': 'First successful API call',
            'timestamp': datetime.now().isoformat(),
            'emotion': 'excited'
        })
        print(f"Stored memory: {memory_id}")
        
        # Generate creative content
        dream = await client.dream.generate(
            "A future where AI and humans collaborate seamlessly"
        )
        print(f"Dream generated: {dream}")
        
        # Check system health
        health = await client.system.health()
        print(f"System health: {health}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())