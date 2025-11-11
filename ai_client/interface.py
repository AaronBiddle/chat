from . import _implementation as _implementation

def call_ai(prompt: str) -> None:
    """Public interface for callers. Forwards to the private implementation."""
    _implementation.call_ai(prompt)