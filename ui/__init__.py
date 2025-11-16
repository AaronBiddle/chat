# Export abstract base class for typing and extension
from .interface import WebUIClass

# Export concrete implementation
from .impl import FlaskWebUI

__all__ = [
    "WebUIClass",
    "FlaskWebUI",
]
