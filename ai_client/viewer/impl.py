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
        import sys

        thinking_open = False
        thinking_closed = False
        saw_text = False
        any_final = False

        for event in events:
            for c in event.chunks:
                # Stream thinking tokens incrementally.
                if c.thinking and not thinking_closed and show_thinking:
                    if not thinking_open:
                        # Open framed thinking block.
                        print("----------")
                        print("Begin thinking")
                        print("----------------")
                        thinking_open = True

                    # Write thinking fragment without newline and flush so it
                    # appears progressively.
                    print(c.thinking, end="", flush=True)

                # When visible text arrives, close thinking block (if open)
                # and stream text tokens.
                if c.text:
                    if thinking_open and not thinking_closed:
                        # Close the thinking block cleanly before printing text
                        print()  # end current thinking line
                        print("----------")
                        print("End thinking")
                        print("--------------")
                        thinking_closed = True

                    # Stream visible text
                    print(c.text, end="", flush=True)
                    saw_text = True

            if event.is_final:
                any_final = True

        # If thinking was opened but never closed (no visible text arrived),
        # close it now so framing is complete.
        if thinking_open and not thinking_closed:
            print()  # finish thinking line
            print("----------")
            print("End thinking")
            print("--------------")

        # If we printed any visible text, ensure we end the line before final
        # marker; otherwise final marker will appear after the thinking block.
        if saw_text:
            print()

        if any_final:
            print("-- end of stream --")
