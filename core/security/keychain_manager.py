#!/usr/bin/env python3
"""
macOS Keychain Manager for Secure API Key Storage
=================================================

Provides secure storage and retrieval of API keys using macOS Keychain.
Keys are encrypted by the system and protected by FileVault.

Security Features:
- System-level encryption via macOS Keychain
- FileVault integration
- No plaintext keys in environment or files
- Automatic fallback to environment variables

Usage:
    from core.security.keychain_manager import KeychainManager

    # Store API key (one-time setup)
    KeychainManager.set_key("JULES_API_KEY", "your-key-here")

    # Retrieve API key (automatic in code)
    key = KeychainManager.get_key("JULES_API_KEY")

    # Delete API key
    KeychainManager.delete_key("JULES_API_KEY")
"""
from __future__ import annotations

import logging
import os
import subprocess

logger = logging.getLogger(__name__)


class KeychainManager:
    """
    Secure API key management using macOS Keychain.

    Keys are stored in the 'login' keychain with service name 'lukhas-ai'
    and are encrypted by the operating system.
    """

    SERVICE_NAME = "lukhas-ai"

    @classmethod
    def set_key(cls, key_name: str, key_value: str) -> bool:
        """
        Store API key securely in macOS Keychain.

        Args:
            key_name: Environment variable name (e.g., "JULES_API_KEY")
            key_value: The API key value to store

        Returns:
            True if successful, False otherwise

        Example:
            >>> KeychainManager.set_key("JULES_API_KEY", "jules-abc123")
            True
        """
        try:
            # Delete existing entry first (ignore errors)
            subprocess.run(
                [
                    "security",
                    "delete-generic-password",
                    "-s", cls.SERVICE_NAME,
                    "-a", key_name,
                ],
                capture_output=True,
                check=False  # Don't raise if key doesn't exist
            )

            # Add new key to keychain
            result = subprocess.run(
                [
                    "security",
                    "add-generic-password",
                    "-s", cls.SERVICE_NAME,
                    "-a", key_name,
                    "-w", key_value,
                    "-U",  # Update if exists
                ],
                capture_output=True,
                text=True,
                check=True
            )

            logger.info(f"Successfully stored {key_name} in macOS Keychain")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to store {key_name} in Keychain: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error storing {key_name}: {e}")
            return False

    @classmethod
    def get_key(cls, key_name: str, fallback_to_env: bool = True) -> str | None:
        """
        Retrieve API key from macOS Keychain with environment variable fallback.

        Args:
            key_name: Environment variable name (e.g., "JULES_API_KEY")
            fallback_to_env: If True, fall back to environment variable

        Returns:
            API key value or None if not found

        Example:
            >>> key = KeychainManager.get_key("JULES_API_KEY")
            >>> if key:
            ...     print("Key found!")
        """
        try:
            # Try to retrieve from keychain
            result = subprocess.run(
                [
                    "security",
                    "find-generic-password",
                    "-s", cls.SERVICE_NAME,
                    "-a", key_name,
                    "-w",  # Output password only
                ],
                capture_output=True,
                text=True,
                check=True
            )

            key_value = result.stdout.strip()
            if key_value:
                logger.debug(f"Retrieved {key_name} from macOS Keychain")
                return key_value

        except subprocess.CalledProcessError:
            # Key not found in keychain
            logger.debug(f"{key_name} not found in macOS Keychain")

        except Exception as e:
            logger.warning(f"Error accessing Keychain for {key_name}: {e}")

        # Fallback to environment variable
        if fallback_to_env:
            env_value = os.getenv(key_name)
            if env_value:
                logger.debug(f"Using {key_name} from environment variable")
                return env_value

        return None

    @classmethod
    def delete_key(cls, key_name: str) -> bool:
        """
        Delete API key from macOS Keychain.

        Args:
            key_name: Environment variable name to delete

        Returns:
            True if successful, False otherwise

        Example:
            >>> KeychainManager.delete_key("JULES_API_KEY")
            True
        """
        try:
            subprocess.run(
                [
                    "security",
                    "delete-generic-password",
                    "-s", cls.SERVICE_NAME,
                    "-a", key_name,
                ],
                capture_output=True,
                text=True,
                check=True
            )

            logger.info(f"Deleted {key_name} from macOS Keychain")
            return True

        except subprocess.CalledProcessError as e:
            if "could not be found" in e.stderr:
                logger.warning(f"{key_name} not found in Keychain")
            else:
                logger.error(f"Failed to delete {key_name}: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting {key_name}: {e}")
            return False

    @classmethod
    def list_keys(cls) -> list[str]:
        """
        List all LUKHAS API keys stored in Keychain.

        Returns:
            List of key names (account names)

        Example:
            >>> keys = KeychainManager.list_keys()
            >>> print(keys)
            ['JULES_API_KEY', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY']
        """
        try:
            result = subprocess.run(
                [
                    "security",
                    "dump-keychain",
                ],
                capture_output=True,
                text=True,
                check=True
            )

            # Parse output for our service name
            keys = []
            lines = result.stdout.split('\n')
            in_lukhas_entry = False

            for line in lines:
                if f'"{cls.SERVICE_NAME}"' in line:
                    in_lukhas_entry = True
                elif in_lukhas_entry and '"acct"' in line:
                    # Extract account name
                    parts = line.split('"acct"<blob>=')
                    if len(parts) > 1:
                        account = parts[1].strip().strip('"')
                        keys.append(account)
                    in_lukhas_entry = False

            return keys

        except Exception as e:
            logger.error(f"Error listing keys: {e}")
            return []

    @classmethod
    def has_key(cls, key_name: str) -> bool:
        """
        Check if a key exists in Keychain.

        Args:
            key_name: Key name to check

        Returns:
            True if key exists, False otherwise

        Example:
            >>> if KeychainManager.has_key("JULES_API_KEY"):
            ...     print("Jules API key is configured")
        """
        return cls.get_key(key_name, fallback_to_env=False) is not None


# Convenience functions for common API keys
def get_jules_api_key() -> str | None:
    """
    Get Jules API key from Keychain or environment.

    Since Jules is a Google service (jules.googleapis.com), this function
    will also check GOOGLE_API_KEY as a fallback if JULES_API_KEY is not found.
    """
    key = KeychainManager.get_key("JULES_API_KEY")
    if not key:
        # Fallback to GOOGLE_API_KEY since Jules is a Google service
        key = KeychainManager.get_key("GOOGLE_API_KEY")
    return key


def get_openai_api_key() -> str | None:
    """Get OpenAI API key from Keychain or environment."""
    return KeychainManager.get_key("OPENAI_API_KEY")


def get_anthropic_api_key() -> str | None:
    """Get Anthropic API key from Keychain or environment."""
    return KeychainManager.get_key("ANTHROPIC_API_KEY")


def get_google_api_key() -> str | None:
    """Get Google API key from Keychain or environment."""
    return KeychainManager.get_key("GOOGLE_API_KEY")


def get_perplexity_api_key() -> str | None:
    """Get Perplexity API key from Keychain or environment."""
    return KeychainManager.get_key("PERPLEXITY_API_KEY")


# List of all supported API keys
SUPPORTED_API_KEYS = [
    "JULES_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY",
    "PERPLEXITY_API_KEY",
    "LUKHAS_API_TOKEN",
    "LUKHAS_ID_SECRET",
]
