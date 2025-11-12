from abc import ABC, abstractmethod
from schemas import StreamResponse


class Viewer(ABC):
    """Abstract base for rendering streaming responses.
    
    Implementations provide stateless rendering methods that display
    StreamResponse objects to various outputs (console, GUI, file, etc).
    """
    
    @staticmethod
    @abstractmethod
    def render(resp: StreamResponse, show_thinking: bool = True) -> None:
        """Render a StreamResponse to some output.
        
        Args:
            resp: The StreamResponse to render.
            show_thinking: Whether to display internal reasoning/thinking content.
        """
        pass
