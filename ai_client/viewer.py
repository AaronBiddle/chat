from typing import Optional
from schemas import StreamResponse, StreamEvent, StreamChunk


class StreamResponseViewer:
    """Simple console viewer for StreamResponse objects.

    This is intentionally minimal: it prints stream chunks in order. It
    distinguishes `thinking` fragments (internal reasoning) from visible
    `text` fragments. Later we can add a more advanced renderer (async,
    GUI, or rich/text styling).
    """

    def __init__(self, show_thinking: bool = True) -> None:
        self.show_thinking = show_thinking

    def render(self, resp: StreamResponse) -> None:
        """Render a StreamResponse to stdout.

        This consumes the events in order and prints any `thinking` and
        `text` fields found on chunks. Events flagged `is_final` cause a
        newline and an end marker.
        """
        for event in resp.events:
            for chunk in event.chunks:
                # Print thinking/internal content if enabled.
                if chunk.thinking and self.show_thinking:
                    print(f"[thinking]{chunk.thinking}", end="")

                # Print visible text content.
                if chunk.text:
                    print(chunk.text, end="")

            # When an event is final we end with a newline and a marker.
            if event.is_final:
                print("\n-- end of stream --")

        # Ensure we end with a newline.
        print()


def view_stream(resp: StreamResponse, show_thinking: Optional[bool] = True) -> None:
    """Convenience function for quick one-off viewing.

    `show_thinking` accepts None for callers that want to signal "use the
    viewer's default"; normalize it to a boolean before calling the viewer.
    """
    if show_thinking is None:
        show = True
    else:
        show = bool(show_thinking)

    StreamResponseViewer(show_thinking=show).render(resp)
