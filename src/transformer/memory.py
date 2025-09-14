from typing import Dict, List
from datetime import datetime
import json
import os

class LocalConversationMemory:
    def __init__(self, storage_file: str = "local_conversations.json"):
        self.storage_file = storage_file
        self.conversations: Dict[str, List[Dict]] = {}
        self._load_conversations()

    def _load_conversations(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    self.conversations = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.conversations = {}

    def _save_conversations(self):
        with open(self.storage_file, 'w') as f:
            json.dump(self.conversations, f, indent=2)

    def get_conversation_history(self, user: str) -> List[Dict]:
        return self.conversations.get(user, [])

    def add_message(self, user: str, role: str, content: str):
        if user not in self.conversations:
            self.conversations[user] = []

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }

        self.conversations[user].append(message)
        self._save_conversations()

    def add_user_message(self, user: str, content: str):
        self.add_message(user, "user", content)

    def add_assistant_message(self, user: str, content: str):
        self.add_message(user, "assistant", content)

    def clear_conversation(self, user: str):
        if user in self.conversations:
            del self.conversations[user]
            self._save_conversations()

    def get_messages_for_api(self, user: str, user_role: str) -> tuple[str, List[Dict]]:
        history = self.get_conversation_history(user)

        # Enhanced system message for better responses
        system_content = f"You are an expert University counselor AI assistant helping a university {user_role} who name is {user}. Provide detailed, thoughtful, and comprehensive responses. Give specific advice, explanations, and actionable suggestions. Be thorough in your responses while remaining supportive and professional."

        messages = []

        # Add conversation history (excluding timestamps and system messages)
        for msg in history:
            if msg["role"] in ["user", "assistant"]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        return system_content, messages