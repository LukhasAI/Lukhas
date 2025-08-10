"""
Unified integration layer for LUKHAS PWM
========================================
Minimal implementation to support system component integration.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Callable

logger = logging.getLogger(__name__)


class Integration:
    """Basic integration component for legacy compatibility"""
    
    def __init__(self):
        self.active = False
        self.data_stores = {}
        
    async def start(self):
        self.active = True
        logger.info("Integration component started")
    
    async def stop(self):
        self.active = False
        logger.info("Integration component stopped")
    
    async def store_data(self, key: str, data: Any):
        """Store data in integration layer"""
        self.data_stores[key] = data
        logger.debug(f"Data stored: {key}")
    
    async def get_data(self, key: str) -> Any:
        """Get data from integration layer"""
        return self.data_stores.get(key)


class UnifiedIntegration:
    """Unified integration layer for system coordination"""
    
    def __init__(self):
        self.active = False
        self.components = {}
        self.message_handlers = {}
        self.data_stores = {}
        
    async def start(self):
        """Start unified integration"""
        self.active = True
        logger.info("UnifiedIntegration started")
    
    async def stop(self):
        """Stop unified integration"""
        self.active = False
        # Stop all components
        for component_id, component in self.components.items():
            if hasattr(component, 'stop'):
                try:
                    await component.stop()
                except Exception as e:
                    logger.error(f"Error stopping component {component_id}: {e}")
        self.components.clear()
        logger.info("UnifiedIntegration stopped")
    
    def register_component(self, component_id: str, handler: Callable):
        """Register a system component with message handler"""
        self.message_handlers[component_id] = handler
        logger.debug(f"Component registered: {component_id}")
    
    def unregister_component(self, component_id: str):
        """Unregister a system component"""
        if component_id in self.message_handlers:
            del self.message_handlers[component_id]
            logger.debug(f"Component unregistered: {component_id}")
    
    async def send_message(self, component_id: str, message: Dict[str, Any]):
        """Send message to registered component"""
        if component_id in self.message_handlers:
            handler = self.message_handlers[component_id]
            try:
                await handler(message)
                logger.debug(f"Message sent to {component_id}")
            except Exception as e:
                logger.error(f"Error sending message to {component_id}: {e}")
        else:
            logger.warning(f"No handler found for component: {component_id}")
    
    async def store_data(self, key: str, data: Any):
        """Store data in unified storage"""
        self.data_stores[key] = data
        logger.debug(f"Data stored: {key}")
    
    async def get_data(self, key: str) -> Any:
        """Get data from unified storage"""
        return self.data_stores.get(key)
    
    async def broadcast_message(self, message: Dict[str, Any]):
        """Broadcast message to all registered components"""
        for component_id, handler in self.message_handlers.items():
            try:
                await handler(message)
                logger.debug(f"Broadcast message sent to {component_id}")
            except Exception as e:
                logger.error(f"Error broadcasting to {component_id}: {e}")
    
    def get_registered_components(self) -> List[str]:
        """Get list of registered components"""
        return list(self.message_handlers.keys())
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get system integration status"""
        return {
            "active": self.active,
            "registered_components": len(self.message_handlers),
            "data_stores": len(self.data_stores),
            "components": list(self.message_handlers.keys())
        }


# Export main classes
__all__ = ['Integration', 'UnifiedIntegration']