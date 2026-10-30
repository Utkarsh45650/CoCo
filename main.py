"""COCO entry point: terminal input -> Groq chat -> local speech output."""
from coco.ai.groq_client import GroqChatClient
from coco.audio.speaker import Speaker
from coco.config import load_config


def main() -> None:
    config = load_config()
    ai = GroqChatClient(
        api_key=config.groq_api_key,
        model=config.groq_model,
        max_history_messages=config.max_history_messages,
        max_reply_tokens=config.max_reply_tokens,
    )
    speaker = Speaker(voice=config.speaker_voice, speed=config.speaker_speed)

    print("\nCOCO is ready. Type a message and press Enter.")
    print("Commands: /reset clears in-memory conversation; /quit exits.\n")

    while True:
        try:
            user_text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nCOCO: Goodbye!")
            break

        if not user_text:
            continue
        if user_text.lower() in {"/quit", "/exit"}:
            print("COCO: Goodbye!")
            break
        if user_text.lower() == "/reset":
            ai.reset_conversation()
            reply = "Let's start fresh!"
            print(f"COCO: {reply}\n")
            speaker.speak(reply)
            continue

        try:
            reply = ai.reply(user_text)
        except Exception as exc:
            # Details are printed for local debugging, not spoken aloud.
            print(f"COCO API error: {exc}")
            reply = "I can't answer right now. Please try again in a moment."
            print(f"COCO: {reply}\n")
            try:
                speaker.speak(reply)
            except Exception as audio_exc:
                print(f"Audio playback error: {audio_exc}")
            continue

        print(f"\nCOCO: {reply}\n")
        try:
            speaker.speak(reply)
        except Exception as exc:
            print(f"Audio playback error: {exc}")
            print("Check eSpeak NG and the Pi's audio output.")


if __name__ == "__main__":
    main()
