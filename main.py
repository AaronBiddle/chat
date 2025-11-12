from ai_client import MoonshotStreamer, ConsoleStreamViewer


def main() -> None:
    prompt = "Hi."
    # Get streaming response using the Moonshot implementation
    stream_response = MoonshotStreamer.stream_response(prompt)
    # Render it using the console viewer
    ConsoleStreamViewer.render(stream_response, show_thinking=True)


if __name__ == "__main__":
    main()
