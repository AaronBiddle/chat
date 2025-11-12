from ai_client.interface import call_ai


def main() -> None:
    prompt = "Hi."
    # Receive the StreamResponse from the ai client. We'll build a viewer
    # later; for now we just obtain the response and do nothing with it.
    stream_response = call_ai(prompt)
    # Intentionally do nothing with `stream_response` for now.


if __name__ == "__main__":
    main()
