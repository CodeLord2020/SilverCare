
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from dataclasses import dataclass
from typing import Dict
from datetime import datetime, timedelta
import asyncio




@dataclass
class TypingStatus:
    is_typing: bool
    last_typed: datetime


class TypingStatusManager:
    """Manages typing status for all active conversations"""
    _typing_status: Dict[str, Dict[str, TypingStatus]] = {}
    TYPING_TIMEOUT = 3  # seconds

    @classmethod
    def set_typing(cls, conversation_id: str, user_id: str):
        if conversation_id not in cls._typing_status:
            cls._typing_status[conversation_id] = {}
        
        cls._typing_status[conversation_id][user_id] = TypingStatus(
            is_typing=True,
            last_typed=datetime.now()
        )

    @classmethod
    def check_typing(cls, conversation_id: str, user_id: str) -> bool:
        if (conversation_id in cls._typing_status and 
            user_id in cls._typing_status[conversation_id]):
            status = cls._typing_status[conversation_id][user_id]
            if datetime.now() - status.last_typed > timedelta(seconds=cls.TYPING_TIMEOUT):
                status.is_typing = False
            return status.is_typing
        return False
    
    