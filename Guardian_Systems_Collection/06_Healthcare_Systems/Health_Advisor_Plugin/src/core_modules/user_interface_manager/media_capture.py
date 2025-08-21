"""
Media Capture Handler for Health Advisor Plugin

Handles capture and processing of images and videos for medical assessment,
ensuring HIPAA compliance and data security.
"""

import logging
from typing import Dict, Any, Optional, Tuple
from enum import Enum
import base64

logger = logging.getLogger(__name__)

class MediaType(Enum):
    IMAGE = "image"
    VIDEO = "video"

class MediaCaptureHandler:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize media capture handler with configuration"""
        self.config = config or {}
        self._supported_image_types = {'image/jpeg', 'image/png'}
        self._supported_video_types = {'video/mp4', 'video/webm'}
        self._max_image_size = 10 * 1024 * 1024  # 10MB
        self._max_video_size = 50 * 1024 * 1024  # 50MB
        logger.info("MediaCaptureHandler initialized")

    async def capture_media(
        self,
        prompt: str,
        media_type: str
    ) -> Tuple[bytes, str]:
        """
        Capture media (image/video) from the user

        Args:
            prompt: Instructions for the user about the media to capture
            media_type: Type of media to capture (image/video)

        Returns:
            Tuple of (media_data, media_mime_type)
        """
        try:
            # Display instructions to user
            capture_instructions = self._get_capture_instructions(media_type, prompt)
            logger.info(f"Requesting media capture: {media_type}")
            
            # In production, this would interface with the UI to capture media
            media_data, mime_type = await self._capture_from_device(media_type)
            
            # Validate the captured media
            self._validate_media(media_data, mime_type, media_type)
            
            # Process the media for optimal use
            processed_data = await self._process_media(media_data, mime_type)
            
            return processed_data, mime_type

        except Exception as e:
            logger.error(f"Error in media capture: {str(e)}")
            raise

    def _get_capture_instructions(self, media_type: str, prompt: str) -> str:
        """
        Get specific instructions for capturing different types of media
        """
        base_instructions = {
            MediaType.IMAGE.value: {
                "lighting": "Ensure good lighting",
                "focus": "Keep the camera steady and focused",
                "framing": "Center the area of concern in the frame",
                "background": "Use a plain background if possible"
            },
            MediaType.VIDEO.value: {
                "duration": "Record for at least 10 seconds",
                "movement": "Move slowly and steadily",
                "audio": "Minimize background noise if including audio",
                "framing": "Keep the area of concern in frame"
            }
        }

        media_specific = base_instructions.get(media_type, {})
        instructions = [prompt] + list(media_specific.values())
        return "\n- ".join(instructions)

    async def _capture_from_device(
        self,
        media_type: str
    ) -> Tuple[bytes, str]:
        """
        Interface with device camera/video capture
        This would be implemented based on the actual UI framework
        """
        # Placeholder implementation
        sample_data = b"Sample media data"
        mime_type = (
            "image/jpeg" if media_type == MediaType.IMAGE.value
            else "video/mp4"
        )
        return sample_data, mime_type

    def _validate_media(
        self,
        media_data: bytes,
        mime_type: str,
        media_type: str
    ) -> None:
        """
        Validate captured media meets requirements
        """
        # Check mime type
        if media_type == MediaType.IMAGE.value:
            if mime_type not in self._supported_image_types:
                raise ValueError(
                    f"Unsupported image type: {mime_type}. "
                    f"Supported types: {self._supported_image_types}"
                )
        else:
            if mime_type not in self._supported_video_types:
                raise ValueError(
                    f"Unsupported video type: {mime_type}. "
                    f"Supported types: {self._supported_video_types}"
                )

        # Check size
        size = len(media_data)
        max_size = (
            self._max_image_size if media_type == MediaType.IMAGE.value
            else self._max_video_size
        )
        if size > max_size:
            raise ValueError(
                f"Media size ({size} bytes) exceeds maximum allowed "
                f"({max_size} bytes)"
            )

    async def _process_media(self, media_data: bytes, mime_type: str) -> bytes:
        """
        Process captured media for optimal use
        - Compress if needed
        - Remove metadata
        - Optimize for medical assessment
        """
        # This would implement actual media processing
        # For now, return the original data
        return media_data

    def get_supported_formats(self, media_type: str) -> set:
        """
        Get supported formats for the specified media type
        """
        if media_type == MediaType.IMAGE.value:
            return self._supported_image_types
        return self._supported_video_types
