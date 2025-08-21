"""
Data Manager for Health Advisor Plugin

This module handles all data operations with strict HIPAA compliance and security measures.
It implements:
- Secure data storage and encryption
- Access control and audit logging
- Data retention policies
- HIPAA-compliant data handling
"""

import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import json
import uuid

from .encryption import EncryptionManager
from .storage import SecureStorage
from .audit import AuditLogger
from .models import UserData, DiagnosticSession, HealthRecord
from .retention import RetentionManager

logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the data manager with configuration"""
        self.config = config or {}
        
        # Initialize core components
        self.encryption = EncryptionManager(config.get('encryption', {}))
        self.storage = SecureStorage(
            encryption_manager=self.encryption,
            config=config.get('storage', {})
        )
        self.audit = AuditLogger(config.get('audit', {}))
        self.retention = RetentionManager(config.get('retention', {}))
        
        logger.info("DataManager initialized with all components")

    async def store_health_record(
        self,
        user_id: str,
        record_data: Dict[str, Any],
        record_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Securely store a health record with HIPAA compliance

        Args:
            user_id: Unique identifier for the user
            record_data: The health record data to store
            record_type: Type of health record (e.g., 'diagnostic', 'measurement')
            metadata: Additional metadata about the record

        Returns:
            record_id: Unique identifier for the stored record
        """
        try:
            # Generate unique record ID
            record_id = str(uuid.uuid4())
            
            # Create record with metadata
            record = HealthRecord(
                record_id=record_id,
                user_id=user_id,
                record_type=record_type,
                data=record_data,
                metadata=metadata or {},
                created_at=datetime.utcnow()
            )

            # Encrypt sensitive data
            encrypted_record = self.encryption.encrypt_record(record)
            
            # Store encrypted record
            await self.storage.store_record(encrypted_record)
            
            # Log the operation
            await self.audit.log_operation(
                operation_type="store_health_record",
                user_id=user_id,
                record_id=record_id,
                metadata={
                    "record_type": record_type,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

            return record_id

        except Exception as e:
            logger.error(f"Error storing health record: {str(e)}")
            await self.audit.log_error(
                error_type="store_health_record_error",
                user_id=user_id,
                details=str(e)
            )
            raise

    async def retrieve_health_record(
        self,
        user_id: str,
        record_id: str,
        requester_id: str,
        purpose: str
    ) -> Dict[str, Any]:
        """
        Retrieve a health record with access control and audit logging

        Args:
            user_id: ID of the user whose record is being accessed
            record_id: ID of the record to retrieve
            requester_id: ID of the entity requesting access
            purpose: Purpose for accessing the record

        Returns:
            The decrypted health record
        """
        try:
            # Verify access permission
            if not await self._verify_access(user_id, requester_id, purpose):
                raise PermissionError("Access denied")

            # Retrieve encrypted record
            encrypted_record = await self.storage.get_record(record_id)
            
            # Decrypt record
            record = self.encryption.decrypt_record(encrypted_record)
            
            # Log access
            await self.audit.log_operation(
                operation_type="retrieve_health_record",
                user_id=user_id,
                record_id=record_id,
                metadata={
                    "requester_id": requester_id,
                    "purpose": purpose,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

            return record.data

        except Exception as e:
            logger.error(f"Error retrieving health record: {str(e)}")
            await self.audit.log_error(
                error_type="retrieve_health_record_error",
                user_id=user_id,
                details=str(e)
            )
            raise

    async def update_health_record(
        self,
        user_id: str,
        record_id: str,
        updates: Dict[str, Any],
        requester_id: str,
        reason: str
    ) -> None:
        """
        Update a health record while maintaining version history

        Args:
            user_id: ID of the user whose record is being updated
            record_id: ID of the record to update
            updates: The updates to apply to the record
            requester_id: ID of the entity making the update
            reason: Reason for the update
        """
        try:
            # Verify update permission
            if not await self._verify_access(user_id, requester_id, "update"):
                raise PermissionError("Update access denied")

            # Retrieve current record
            current_record = await self.storage.get_record(record_id)
            
            # Create new version with updates
            updated_record = current_record.create_new_version(updates)
            
            # Encrypt and store updated record
            encrypted_record = self.encryption.encrypt_record(updated_record)
            await self.storage.store_record(encrypted_record)
            
            # Log update
            await self.audit.log_operation(
                operation_type="update_health_record",
                user_id=user_id,
                record_id=record_id,
                metadata={
                    "requester_id": requester_id,
                    "reason": reason,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

        except Exception as e:
            logger.error(f"Error updating health record: {str(e)}")
            await self.audit.log_error(
                error_type="update_health_record_error",
                user_id=user_id,
                details=str(e)
            )
            raise

    async def delete_health_record(
        self,
        user_id: str,
        record_id: str,
        requester_id: str,
        reason: str
    ) -> None:
        """
        Mark a health record for deletion according to retention policies

        Args:
            user_id: ID of the user whose record is being deleted
            record_id: ID of the record to delete
            requester_id: ID of the entity requesting deletion
            reason: Reason for deletion
        """
        try:
            # Verify deletion permission
            if not await self._verify_access(user_id, requester_id, "delete"):
                raise PermissionError("Deletion access denied")

            # Mark record for deletion based on retention policy
            await self.retention.mark_for_deletion(record_id, reason)
            
            # Log deletion request
            await self.audit.log_operation(
                operation_type="delete_health_record",
                user_id=user_id,
                record_id=record_id,
                metadata={
                    "requester_id": requester_id,
                    "reason": reason,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

        except Exception as e:
            logger.error(f"Error marking record for deletion: {str(e)}")
            await self.audit.log_error(
                error_type="delete_health_record_error",
                user_id=user_id,
                details=str(e)
            )
            raise

    async def _verify_access(
        self,
        user_id: str,
        requester_id: str,
        purpose: str
    ) -> bool:
        """
        Verify access permissions for a given operation
        
        Args:
            user_id: ID of the user whose data is being accessed
            requester_id: ID of the entity requesting access
            purpose: Purpose of the access request
            
        Returns:
            bool: Whether access is granted
        """
        # TODO: Implement proper access control logic
        # For now, basic check that requester is user or system
        return requester_id in (user_id, "system")
