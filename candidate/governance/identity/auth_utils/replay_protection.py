import logging
import streamlit as st
from typing import Optional
logger = logging.getLogger(__name__)
import time
from collections import deque


class ReplayProtection:
    """Tracks recent nonces to prevent replay attacks with timestamp-based expiration."""

    def __init__(self, max_nonce_history=1000, expiration_time=300):
        self.nonce_history = deque()
        self.nonce_set = set()
        self.max_nonce_history = max_nonce_history
        self.expiration_time = expiration_time
        self.device_nonces = {}  # device_id -> set of nonces

    def add_nonce(self, nonce, device_id=None):
        """Add a nonce to the history and ensure it is unique. Optionally track per device."""
        current_time = time.time()
        self._expire_old_nonces(current_time)

        if nonce in self.nonce_set:
            return False  # Replay detected

        self.nonce_history.append((nonce, current_time, device_id))
        self.nonce_set.add(nonce)

        if device_id:
            if device_id not in self.device_nonces:
                self.device_nonces[device_id] = set()
            self.device_nonces[device_id].add(nonce)

        if len(self.nonce_history) > self.max_nonce_history:
            old_nonce, _, old_device_id = self.nonce_history.popleft()
            self.nonce_set.remove(old_nonce)
            if old_device_id and old_device_id in self.device_nonces:
                self.device_nonces[old_device_id].discard(old_nonce)

        return True

    def is_replay(self, nonce, device_id=None):
        """Check if a nonce is a replay, optionally for a specific device."""
        if device_id and device_id in self.device_nonces:
            return nonce in self.device_nonces[device_id]
        return nonce in self.nonce_set

    def _expire_old_nonces(self, current_time):
        """Remove nonces that have expired based on the expiration time and log expiry events."""
        while self.nonce_history and current_time - self.nonce_history[0][1] > self.expiration_time:
            old_nonce, old_time, old_device_id = self.nonce_history.popleft()
            self.nonce_set.remove(old_nonce)
            if old_device_id and old_device_id in self.device_nonces:
                self.device_nonces[old_device_id].discard(old_nonce)
            logger.info(f"Nonce expired: {old_nonce} (device: {old_device_id}, time: {old_time})")