from schemas import StreamResponse
from .interface import Viewer


class ConsoleStreamViewer(Viewer):
    """Simple console viewer for StreamResponse objects.

    This is intentionally minimal: it prints stream chunks in order. It
    distinguishes `thinking` fragments (internal reasoning) from visible
    `text` fragments. Later we can add a more advanced renderer (async,
    GUI, or rich/text styling).
    """
    
    @staticmethod
    def render(resp: StreamResponse, show_thinking: bool = True) -> None:
        """Render a StreamResponse to stdout.

        This consumes the events in order and prints any `thinking` and
        `text` fields found on chunks. Events flagged `is_final` cause a
        newline and an end marker.
        """
        for event in resp.events:
            for chunk in event.chunks:
                # Print thinking/internal content if enabled.
                if chunk.thinking and show_thinking:
                    print(f"[thinking]{chunk.thinking}", end="")

                # Print visible text content.
                if chunk.text:
                    print(chunk.text, end="")

            # When an event is final we end with a newline and a marker.
            if event.is_final:
                print("\n-- end of stream --")

        # Ensure we end with a newline.
        print()
