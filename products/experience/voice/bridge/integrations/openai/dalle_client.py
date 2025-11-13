import logging
from datetime import timezone

logger = logging.getLogger(__name__)
"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: dalle_client.py
Advanced: dalle_client.py
Integration Date: 2025-05-31T07:55:29.370655
"""

import base64
import os
from datetime import datetime
from typing import Any, Optional

import aiohttp
from core.common import get_logger
from core.common.config import settings

logger = get_logger(__name__)


class DALLEClient:
    """
    Client for interacting with OpenAI's DALL-E image generation API.
    Provides async methods for generating and editing images.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "dall-e-3"):
        self.api_key = api_key or settings.OPENAI_API_KEY
        if not self.api_key:
            logger.warning(
                "No OpenAI API key provided. Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )

        self.model = model
        self.api_base = "https://api.openai.com/v1"
        self.session = None
        self.image_storage_path = os.path.join(os.getcwd(), "generated_images")

        # Create image storage directory if it doesn't exist
        if not os.path.exists(self.image_storage_path):
            os.makedirs(self.image_storage_path)

    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            )

    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "natural",
        n: int = 1,
    ) -> dict[str, Any]:
        """
        Generate an image using DALL-E

        Args:
            prompt: Text description of the desired image
            size: Image size (1024x1024, 1024x1792, 1792x1024)
            quality: Image quality (standard, hd)
            style: Image style (natural, vivid)
            n: Number of images to generate

        Returns:
            Dictionary containing URLs or base64 data of generated images
        """
        if not self.api_key:
            return {"error": "No API key provided"}

        try:
            await self._ensure_session()

            payload = {
                "model": self.model,
                "prompt": prompt,
                "n": n,
                "size": size,
                "quality": quality,
                "style": style,
                "response_format": "url",
            }

            logger.info(f"Generating image with DALL-E: {prompt[:50]}...")

            async with self.session.post(f"{self.api_base}/images/generations", json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"DALL-E API error: {response.status} - {error_text}")
                    return {
                        "error": f"API error: {response.status}",
                        "urls": [],
                    }

                data = await response.json()

                # Extract image URLs
                image_urls = [item["url"] for item in data.get("data", [])]

                # Save images locally
                saved_paths = []
                if image_urls:
                    saved_paths = await self._save_images_from_urls(image_urls, prompt)

                return {
                    "urls": image_urls,
                    "local_paths": saved_paths,
                    "prompt": prompt,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

        except Exception as e:
            logger.error(f"Error generating image: {e!s}")
            return {"error": str(e), "urls": []}

    async def _save_images_from_urls(self, urls: list[str], prompt: str) -> list[str]:
        """
        Download and save images from URLs

        Args:
            urls: List of image URLs
            prompt: Original prompt used to generate the images

        Returns:
            List of local file paths
        """
        saved_paths = []

        for i, url in enumerate(urls):
            try:
                # Create a filename based on prompt and timestamp
                timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                safe_prompt = "".join(c if c.isalnum() else "_" for c in prompt[:30])
                filename = f"{safe_prompt}_{timestamp}_{i}.png"
                filepath = os.path.join(self.image_storage_path, filename)

                # Download the image
                async with self.session.get(url) as response:
                    if response.status == 200:
                        with open(filepath, "wb") as f:
                            f.write(await response.read())
                        saved_paths.append(filepath)
                    else:
                        logger.error(f"Failed to download image from {url}: {response.status}")

            except Exception as e:
                logger.error(f"Error saving image: {e!s}")

        return saved_paths

    async def edit_image(
        self,
        image_path: str,
        mask_path: str,
        prompt: str,
        size: str = "1024x1024",
        n: int = 1,
    ) -> dict[str, Any]:
        """
            Edit an image using DALL-E

            Args:
                image_path: Path to the image to edit
                mask_path: Path to the mask that defines the edited area (black=keep,
        white=edit)
                prompt: Text description of the desired edit
                size: Image size
                n: Number of images to generate

            Returns:
                Dictionary containing URLs or base64 data of generated images
        """
        if not self.api_key:
            return {"error": "No API key provided"}

        if not os.path.exists(image_path):
            return {"error": f"Image file not found: {image_path}"}

        if not os.path.exists(mask_path):
            return {"error": f"Mask file not found: {mask_path}"}

        try:
            await self._ensure_session()

            # Read and encode the image and mask files
            with (
                open(image_path, "rb") as image_file,
                open(mask_path, "rb") as mask_file,
            ):
                image_data = base64.b64encode(image_file.read()).decode("utf-8")
                mask_data = base64.b64encode(mask_file.read()).decode("utf-8")

            # Prepare form data
            form_data = aiohttp.FormData()
            form_data.add_field("image", image_data)
            form_data.add_field("mask", mask_data)
            form_data.add_field("prompt", prompt)
            form_data.add_field("n", str(n))
            form_data.add_field("size", size)
            form_data.add_field("response_format", "url")

            logger.info(f"Editing image with DALL-E: {prompt[:50]}...")

            async with self.session.post(f"{self.api_base}/images/edits", data=form_data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"DALL-E API error: {response.status} - {error_text}")
                    return {
                        "error": f"API error: {response.status}",
                        "urls": [],
                    }

                data = await response.json()

                # Extract image URLs
                image_urls = [item["url"] for item in data.get("data", [])]

                # Save images locally
                saved_paths = []
                if image_urls:
                    saved_paths = await self._save_images_from_urls(image_urls, f"edit_{prompt}")

                return {
                    "urls": image_urls,
                    "local_paths": saved_paths,
                    "prompt": prompt,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

        except Exception as e:
            logger.error(f"Error editing image: {e!s}")
            return {"error": str(e), "urls": []}

    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
