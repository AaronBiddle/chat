from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from schemas import Message


class WebUIClass(ABC):
    """Abstract base for web user interfaces.

    Implementations provide web-based interaction with the AI client,
    managing conversation state and rendering responses. This allows
    different web frameworks (Flask, FastAPI, etc.) to be swapped
    without changing the interface contract.
    """

    @abstractmethod
    def __init__(self, initial_messages: Optional[List[Message]] = None):
        """Initialize the web UI with optional starting conversation.

        Args:
            initial_messages: Optional list of Message objects to start with.
                If None, implementations should initialize with a default
                system message or empty conversation.
        """
        raise NotImplementedError

    @abstractmethod
    def get_messages(self) -> List[Message]:
        """Return the current conversation history.

        Returns:
            List[Message]: Current messages in the conversation.
        """
        raise NotImplementedError

    @abstractmethod
    def add_message(self, message: Message) -> None:
        """Add a message to the conversation history.

        Args:
            message: Message object to append to conversation.
        """
        raise NotImplementedError

    @abstractmethod
    def clear_messages(self) -> None:
        """Clear all messages from the conversation history."""
        raise NotImplementedError

    @abstractmethod
    def run(self, host: str = "127.0.0.1", port: int = 5000, debug: bool = True) -> None:
        """Start the web server.

        Args:
            host: Host address to bind to.
            port: Port number to listen on.
            debug: Whether to run in debug mode.
        """
        raise NotImplementedError

    @abstractmethod
    def get_app(self) -> Any:
        """Return the underlying web application instance.

        This allows access to the framework-specific app object for
        advanced configuration or testing.

        Returns:
            The web framework's application instance (e.g., Flask app).
        """
        raise NotImplementedError
