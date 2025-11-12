from . import _implementation as _implementation
from .schemas import StreamResponse


def stream_ai(prompt: str) -> StreamResponse:
    """Public interface for callers. Forwards to the private implementation and
    returns a StreamResponse that represents the streaming result.
    """
    return _implementation.call_ai_stream(prompt)