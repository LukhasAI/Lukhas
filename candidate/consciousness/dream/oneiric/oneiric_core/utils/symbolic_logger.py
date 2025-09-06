"""Minimal symbolic logger stub"""
import logging
logger = logging.getLogger(__name__)


class DreamLogger:
    def __init__(self):
        self.logs = []

    def log_dream(self, dream_data):
        self.logs.append(dream_data)

    def get_logs(self):
        return self.logs