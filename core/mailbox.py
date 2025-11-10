"""Bridge module for core.mailbox → labs.core.mailbox"""
from __future__ import annotations

from labs.core.mailbox import MailBox, MessageHandler, create_mailbox

__all__ = ["MailBox", "MessageHandler", "create_mailbox"]
