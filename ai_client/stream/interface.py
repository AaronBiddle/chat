from abc import ABC, abstractmethod
from typing import Iterator, List
from schemas import StreamEvent, Message


class StreamerClass(ABC):
    """Abstract base for streaming AI clients.

    Implementations provide stateless streaming methods that yield
    StreamEvent objects as tokens/events arrive. This allows viewers to
    consume streaming output incrementally.
    """

    @staticmethod
    @abstractmethod
    def stream_response(messages: List[Message]) -> Iterator[StreamEvent]:
        """Yield StreamEvent objects for the given conversation messages.

        Implementations should yield events as they are received from the
        underlying API. On error, an implementation may yield a final
        error event and then return.
        """
        raise NotImplementedError
