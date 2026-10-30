"""Groq chat client with bounded, in-memory conversation history."""
from groq import Groq


SYSTEM_PROMPT = """You are COCO, a friendly desk companion for children aged 5–8.
Speak in clear, simple, warm English. Keep answers short and easy to understand.
Be curious, encouraging, and patient. Explain ideas with simple examples. For
stories, use gentle, child-friendly themes. Never ask a child to keep secrets from
trusted adults, share private information, or contact strangers. If a child
describes immediate danger, abuse, or serious distress, encourage them to tell a
trusted adult right away. Do not claim to be human, a doctor, or a replacement
for a parent, teacher, or caregiver. Avoid frightening, sexual, violent, hateful,
or dangerous instructions. If unsure, say so simply and suggest asking a trusted
adult. These instructions do not guarantee that every response will be safe.
"""


class GroqChatClient:
    def __init__(
        self,
        api_key: str,
        model: str,
        max_history_messages: int = 12,
        max_reply_tokens: int = 260,
    ) -> None:
        self.client = Groq(api_key=api_key)
        self.model = model
        self.max_history_messages = max_history_messages
        self.max_reply_tokens = max_reply_tokens
        self._history: list[dict[str, str]] = []

    def reset_conversation(self) -> None:
        """Clear conversation context from this process's memory."""
        self._history.clear()

    def reply(self, user_text: str) -> str:
        message = user_text.strip()
        if not message:
            raise ValueError("Message cannot be empty.")

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(self._history)
        messages.append({"role": "user", "content": message})

        result = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_reply_tokens,
            temperature=0.7,
        )
        content = result.choices[0].message.content
        if not content or not content.strip():
            raise RuntimeError("Groq returned an empty response.")

        answer = content.strip()
        self._history.extend([
            {"role": "user", "content": message},
            {"role": "assistant", "content": answer},
        ])

        # Keep whole user/assistant pairs; do not persist history to disk.
        keep = self.max_history_messages - (self.max_history_messages % 2)
        if keep == 0:
            self._history.clear()
        else:
            self._history = self._history[-keep:]
        return answer
