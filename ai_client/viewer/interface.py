from abc import ABC, abstractmethod
from typing import Iterable, Dict
from schemas import StreamEvent


class StreamViewerClass(ABC):
    """Abstract base for rendering streaming events.

    Implementations consume an iterable of StreamEvent objects which may be
    produced incrementally by a Streamer.
    """

    @staticmethod
    @abstractmethod
    def render(events: Iterable[StreamEvent], show_thinking: bool = True) -> None:
        """Render streaming events to some output.

        Args:
            events: Iterable of StreamEvent objects (may be a generator).
            show_thinking: Whether to display internal thinking tokens.
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def render_and_aggregate(
        events: Iterable[StreamEvent], show_thinking: bool = True
    ) -> Dict[str, str]:
        """Render streaming events and return aggregated output.

        Implementations should behave like `render` but also return a dictionary
        with two keys:
            - 'thinking': concatenated internal thinking tokens (if any)
            - 'text': concatenated final text tokens

        Args:
            events: Iterable of StreamEvent objects (may be a generator).
            show_thinking: Whether to include internal thinking tokens in the
                aggregation.

        Returns:
            Dict[str, str]: mapping with keys 'thinking' and 'text'.
        """
        raise NotImplementedError
