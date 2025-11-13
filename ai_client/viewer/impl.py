from typing import Iterable, Dict, Tuple

from schemas import StreamEvent
from .interface import StreamViewerClass


class StreamViewer(StreamViewerClass):
    """Simple console viewer for streaming events.

    This is intentionally minimal: it prints event chunks in order. It
    distinguishes `thinking` fragments (internal reasoning) from visible
    `text` fragments. Later we can add a more advanced renderer (async,
    GUI, or rich/text styling).
    """
    
    @staticmethod
    def render(events, show_thinking: bool = True) -> None:
        """Render streaming events to stdout.

        This consumes the events in order and prints any `thinking` and
        `text` fields found on chunks. Events flagged `is_final` cause a
        newline and an end marker.
        """
        # Streamed rendering behavior:
        # - Print a thinking header the first time we see a thinking token
        #   (if show_thinking=True) and stream thinking tokens as they arrive.
        # - When the first visible text token arrives, close the thinking
        #   block (if open) and begin streaming visible text tokens.
        # - At the end, print the final marker if any event is final.
        # Delegate to the central consumer which performs identical
        # processing. We pass `print_output=True` since `render` prints but
        # doesn't return the aggregated strings.
        _, _, _ = StreamViewer._consume_events(events, show_thinking, print_output=True)

    @staticmethod
    def render_and_aggregate(
        events: Iterable[StreamEvent], show_thinking: bool = True
    ) -> Dict[str, str]:
        """Render streaming events to stdout and return aggregated strings.

        Returns a dict with keys `thinking` and `text` containing the
        concatenated thinking tokens and visible text respectively.
        """
        # Use central consumer, capturing aggregated fragments.
        thinking_joined, text_joined, _ = StreamViewer._consume_events(
            events, show_thinking, print_output=True
        )

        return {"thinking": thinking_joined, "text": text_joined}

    @staticmethod
    def _consume_events(
        events: Iterable[StreamEvent], show_thinking: bool, print_output: bool
    ) -> Tuple[str, str, bool]:
        """Core event consumer used by both render and render_and_aggregate.

        Args:
            events: Iterable of StreamEvent objects.
            show_thinking: Whether to include internal thinking tokens.
            print_output: If True, perform the same prints as the original
                implementations; otherwise operate silently and only aggregate.

        Returns:
            A tuple `(thinking, text, any_final)` where `thinking` and `text`
            are the concatenated fragments and `any_final` indicates if any
            event was final.
        """
        thinking_open = False
        thinking_closed = False
        saw_text = False
        any_final = False

        thinking_buf = []
        text_buf = []

        for event in events:
            for c in event.chunks:
                # Stream thinking tokens incrementally.
                if c.thinking and not thinking_closed and show_thinking:
                    if not thinking_open:
                        if print_output:
                            print("----------")
                            print("Begin thinking")
                            print("----------------")
                        thinking_open = True

                    if print_output:
                        print(c.thinking, end="", flush=True)
                    thinking_buf.append(c.thinking)

                # When visible text arrives, close thinking block (if open)
                # and stream text tokens.
                if c.text:
                    if thinking_open and not thinking_closed:
                        if print_output:
                            print()  # end current thinking line
                            print("----------")
                            print("End thinking")
                            print("--------------")
                        thinking_closed = True

                    if print_output:
                        print(c.text, end="", flush=True)
                    text_buf.append(c.text)
                    saw_text = True

            if event.is_final:
                any_final = True

        # If thinking was opened but never closed (no visible text arrived),
        # close it now so framing is complete.
        if thinking_open and not thinking_closed:
            if print_output:
                print()  # finish thinking line
                print("----------")
                print("End thinking")
                print("--------------")

        # If we printed any visible text, ensure we end the line before final
        # marker; otherwise final marker will appear after the thinking block.
        if saw_text and print_output:
            print()

        if any_final and print_output:
            print("-- end of stream --")

        return ("".join(thinking_buf), "".join(text_buf), any_final)
