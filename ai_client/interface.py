from . import _implementation as _implementation

def call_ai(prompt: str) -> str:
    """Public interface for callers. Forwards to the private implementation."""
    return _implementation.call_ai(prompt)