from ai_client import Streamer, StreamViewer
from schemas import Message


def main() -> None:
    # Start conversation with a system instruction
    messages = [Message(role="system", text="You are Kimi.")]

    print("Interactive prompt. Type 'q' to quit.")
    while True:
        prompt = input("User prompt (or 'q' to quit): ")
        if prompt is None:
            break
        if prompt.strip().lower() == "q":
            print("Exiting.")
            break

        # Add the user's message to the conversation
        messages.append(Message(role="user", text=prompt))

        # Show the messages that will be sent to the streaming API
        print("\nMessages sent to streamer:")
        for m in messages:
            try:
                print(m.dict())
            except Exception:
                print(str(m))

        # Stream the response and render + aggregate
        stream_response = Streamer.stream_response(messages)
        agg = StreamViewer.render_and_aggregate(stream_response, show_thinking=True)

        # Extract aggregated visible text and add as assistant message
        assistant_text = agg.get("text", "") if isinstance(agg, dict) else ""
        messages.append(Message(role="assistant", text=assistant_text))

        print("\nAssistant response aggregated text:")
        print(assistant_text)


if __name__ == "__main__":
    main()
