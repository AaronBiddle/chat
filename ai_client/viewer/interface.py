from abc import ABC, abstractmethod
from typing import Iterable
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
