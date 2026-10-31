from __future__ import annotations

from collections import deque
from typing import Deque


class Conversation:
    """
    Manages recent conversation messages in memory.

    Nothing is written to a database or file.
    """

    def __init__(self, max_history_messages: int = 12):
        if max_history_messages < 2:
            raise ValueError(
                "Conversation history must allow at least 2 messages."
            )

        self._messages: Deque[dict[str, str]] = deque(
            maxlen=max_history_messages
        )

    def add(self, role: str, content: str) -> None:
        if role not in {"user", "assistant"}:
            raise ValueError(
                "Role must be 'user' or 'assistant'."
            )

        content = content.strip()

        if not content:
            return

        self._messages.append(
            {
                "role": role,
                "content": content,
            }
        )

    def get_messages(self) -> list[dict[str, str]]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages.clear()

    def __len__(self) -> int:
        return len(self._messages)