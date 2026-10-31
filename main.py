from __future__ import annotations

import sys

from config.settings import load_settings
from coco.ai.groq_client import GroqChatClient
from coco.audio.microphone import Microphone
from coco.audio.speaker import Speaker


def print_banner() -> None:
    print()
    print("=" * 52)
    print("              COCO AI COMPANION")
    print("=" * 52)
    print("Type a message or use a compatible microphone.")
    print("Commands: /reset, /help, /quit")
    print("=" * 52)
    print()


def read_keyboard_input() -> str:
    try:
        return input("You: ").strip()
    except EOFError:
        return "/quit"


def get_user_input(microphone: Microphone | None) -> str:
    while True:
        print("\nChoose input:")
        print("  1. Keyboard")
        print("  2. Microphone")
        print("  q. Quit")

        try:
            choice = input("Selection: ").strip().lower()
        except EOFError:
            return "/quit"

        if choice in {"q", "quit", "exit"}:
            return "/quit"

        if choice == "1":
            return read_keyboard_input()

        if choice == "2":
            if microphone is None:
                print(
                    "Microphone mode is disabled. "
                    "Use keyboard mode instead."
                )
                continue

            try:
                text = microphone.transcribe()

                if not text:
                    print(
                        "No usable speech was transcribed. "
                        "Please try again or use the keyboard."
                    )
                    continue

                print(f"\nRecognised: {text}")

                confirm = input(
                    "Send this message to COCO? [Y/n]: "
                ).strip().lower()

                if confirm in {"", "y", "yes"}:
                    return text

                print("Message discarded.")

            except Exception as exc:
                print(f"\nMicrophone error: {exc}")
                print(
                    "You can still use keyboard input."
                )

            continue

        print("Invalid selection. Choose 1, 2, or q.")


def main() -> int:
    try:
        settings = load_settings()
    except Exception as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1

    try:
        ai = GroqChatClient(
            api_key=settings.groq_api_key,
            model=settings.groq_model,
            max_reply_tokens=settings.max_reply_tokens,
            max_history_messages=settings.max_history_messages,
        )
    except Exception as exc:
        print(
            f"Could not initialise the AI client: {exc}",
            file=sys.stderr,
        )
        return 1

    speaker = Speaker(
        model_path=settings.piper_model_path,
        enabled=settings.enable_tts,
    )

    microphone = None

    if settings.enable_microphone:
        microphone = Microphone(
            model_path=settings.vosk_model_path,
            sample_rate=settings.mic_sample_rate,
            max_seconds=settings.mic_max_seconds,
            end_silence_seconds=(
                settings.mic_end_silence_seconds
            ),
        )

    print_banner()

    if not settings.enable_tts:
        print("Speech output is disabled.")

    elif not settings.piper_model_path.is_file():
        print(
            "Warning: Piper voice model not found. "
            "COCO will show text responses without speaking."
        )

    if not settings.enable_microphone:
        print("Microphone input is disabled in configuration.")

    print(
        "\nPrivacy note: messages sent to Groq are processed "
        "by the hosted AI service. Avoid entering personal "
        "or sensitive information."
    )

    while True:
        user_message = get_user_input(microphone)

        if not user_message:
            continue

        command = user_message.strip().lower()

        if command in {"/quit", "/exit"}:
            print("COCO: Goodbye! See you next time.")
            break

        if command == "/help":
            print(
                "\nCommands:\n"
                "  /help  - show commands\n"
                "  /reset - clear temporary conversation history\n"
                "  /quit  - exit COCO\n"
            )
            continue

        if command == "/reset":
            ai.reset_conversation()
            print("COCO: Let's start a new conversation!")
            continue

        try:
            answer = ai.chat(user_message)

        except Exception as exc:
            print(
                "\nAI request failed. Check your internet "
                "connection, API key, model availability, "
                "account limits and provider status."
            )
            print(f"Details: {exc}")
            continue

        print(f"\nCOCO: {answer}\n")

        if settings.enable_tts:
            try:
                speaker.speak(answer)
            except Exception as exc:
                print(
                    "Speech output failed, but you can read "
                    "the response above."
                )
                print(f"Audio details: {exc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())