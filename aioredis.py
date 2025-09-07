"""
Mock aioredis module
===================
Provides basic aioredis compatibility for LUKHAS modules when aioredis is not available.
"""

class MockRedis:
    """Mock Redis client for development/testing"""
    
    def __init__(self, *args, **kwargs):
        self.data = {}
        
    async def get(self, key):
        """Mock get operation"""
        return self.data.get(key)
        
    async def set(self, key, value, ex=None):
        """Mock set operation"""
        self.data[key] = value
        return True
        
    async def delete(self, key):
        """Mock delete operation"""
        if key in self.data:
            del self.data[key]
            return 1
        return 0
        
    async def close(self):
        """Mock close operation"""
        pass
        
    async def wait_closed(self):
        """Mock wait_closed operation"""  
        pass

# Mock the main aioredis functions
async def create_redis_pool(*args, **kwargs):
    """Mock create_redis_pool"""
    return MockRedis()

async def create_connection(*args, **kwargs):
    """Mock create_connection"""
    return MockRedis()

def from_url(url, **kwargs):
    """Mock from_url"""
    return MockRedis()

# Mock Redis class
Redis = MockRedis

__version__ = "mock-1.0.0"