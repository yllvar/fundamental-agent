"""
Conversation Manager
Dict-based user conversation state — not SQLite, not Redis, not a queue
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any


class ConversationManager:
    """Simple in-memory conversation state per user"""

    def __init__(self, max_history: int = 5, idle_minutes: int = 30):
        self._users: Dict[str, Dict] = {}
        self.max_history = max_history
        self.idle_minutes = idle_minutes
        self.logger = logging.getLogger(__name__)

    def get_or_create(self, user_id: str) -> Dict:
        """Get or create a user conversation record"""
        if user_id not in self._users:
            self._users[user_id] = {
                "history": [],
                "preferences": {"pairs": []},
                "last_active": datetime.now(),
                "created_at": datetime.now(),
            }
        return self._users[user_id]

    def add_exchange(self, user_id: str, user_msg: str, assistant_msg: str):
        """Add a user/assistant exchange to history"""
        user = self.get_or_create(user_id)
        user["history"].append({
            "role": "user",
            "content": user_msg,
            "timestamp": datetime.now().isoformat(),
        })
        user["history"].append({
            "role": "assistant",
            "content": assistant_msg,
            "timestamp": datetime.now().isoformat(),
        })
        user["last_active"] = datetime.now()

        if len(user["history"]) > self.max_history * 2:
            user["history"] = user["history"][-self.max_history * 2:]

    def get_history(self, user_id: str) -> List[Dict]:
        """Get conversation history for a user"""
        user = self.get_or_create(user_id)
        return user["history"]

    def set_preference(self, user_id: str, key: str, value: Any):
        """Set a user preference"""
        user = self.get_or_create(user_id)
        user["preferences"][key] = value

    def get_preferences(self, user_id: str) -> Dict:
        """Get user preferences"""
        return self.get_or_create(user_id)["preferences"]

    def cleanup_idle(self):
        """Remove idle users to free memory"""
        now = datetime.now()
        idle_ids = [
            uid for uid, data in self._users.items()
            if (now - data["last_active"]) > timedelta(minutes=self.idle_minutes)
        ]
        for uid in idle_ids:
            del self._users[uid]
        if idle_ids:
            self.logger.info(f"Cleaned up {len(idle_ids)} idle conversation(s)")

    @property
    def active_users(self) -> int:
        return len(self._users)
