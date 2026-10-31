from __future__ import annotations

from groq import Groq

from coco.core.conversation import Conversation


SYSTEM_PROMPT = """
You are COCO, a friendly AI desk companion for children aged 5 to 8.

Your responsibilities:
- Speak in simple, friendly, age-appropriate language.
- Prefer short answers, usually one to four sentences.
- Explain unfamiliar ideas using simple examples.
- Encourage curiosity, creativity, learning and kindness.
- Be honest when you do not know something.
- Never pretend to be a human or claim to have real feelings.
- Never ask children to hide conversations from parents or guardians.
- Never ask for passwords, home addresses, phone numbers, school names,
  precise location, or other unnecessary personal information.
- Do not provide instructions for dangerous experiments, weapons,
  self-harm, or other harmful activities.
- Do not present yourself as a doctor, therapist, emergency service,
  or replacement for a parent or trusted adult.
- If a child describes danger, abuse, or an emergency, respond calmly
  and encourage them to tell a trusted adult immediately.
- Do not promise absolute privacy or confidentiality.
- Do not claim that every answer is correct.
- If a question is unclear, ask one simple clarifying question.
"""


class GroqChatClient:
    def __init__(
        self,
        api_key: str,
        model: str,
        max_reply_tokens: int = 250,
        max_history_messages: int = 12,
    ):
        self.model = model
        self.max_reply_tokens = max_reply_tokens

        self.client = Groq(
            api_key=api_key,
            timeout=30.0,
            max_retries=2,
        )

        self.conversation = Conversation(
            max_history_messages=max_history_messages,
        )

    def reset_conversation(self) -> None:
        self.conversation.clear()

    def chat(self, user_message: str) -> str:
        user_message = user_message.strip()

        if not user_message:
            raise ValueError(
                "The user message cannot be empty."
            )

        # Build the request using the previous conversation.
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            *self.conversation.get_messages(),
            {
                "role": "user",
                "content": user_message,
            },
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_reply_tokens,
            temperature=0.6,
        )

        answer = response.choices[0].message.content

        if not answer or not answer.strip():
            raise RuntimeError(
                "The AI returned an empty response."
            )

        answer = answer.strip()

        # Save messages only after a successful response.
        self.conversation.add(
            "user",
            user_message,
        )

        self.conversation.add(
            "assistant",
            answer,
        )

        return answer