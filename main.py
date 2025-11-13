from ai_client import Streamer, StreamViewer
from schemas import Message


def main() -> None:
    prompt = "Hi."
    # Build conversation messages as a list of Message objects
    messages = [
        Message(role="system", text="You are Kimi."),
        Message(role="user", text=prompt),
    ]

    # Get streaming response using the Moonshot implementation
    stream_response = Streamer.stream_response(messages)
    # Render it using the console viewer
    StreamViewer.render(stream_response, show_thinking=True)


if __name__ == "__main__":
    main()
