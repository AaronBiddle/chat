from abc import ABC, abstractmethod
from typing import Iterator
from schemas import StreamEvent


class Streamer(ABC):
    """Abstract base for streaming AI clients.

    Implementations provide stateless streaming methods that yield
    StreamEvent objects as tokens/events arrive. This allows viewers to
    consume streaming output incrementally.
    """

    @staticmethod
    @abstractmethod
    def stream_response(prompt: str) -> Iterator[StreamEvent]:
        """Yield StreamEvent objects for the given prompt.

        Implementations should yield events as they are received from the
        underlying API. On error, an implementation may yield a final
        error event and then return.
        """
        raise NotImplementedError
