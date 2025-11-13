from ai_client import Streamer, StreamViewer


def main() -> None:
    prompt = "Hi."
    # Get streaming response using the Moonshot implementation
    stream_response = Streamer.stream_response(prompt)
    # Render it using the console viewer
    StreamViewer.render(stream_response, show_thinking=True)


if __name__ == "__main__":
    main()
