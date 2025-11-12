from abc import ABC, abstractmethod
from schemas import StreamResponse


class Streamer(ABC):
    """Abstract base for streaming AI clients.
    
    Implementations provide stateless streaming methods that generate
    StreamResponse objects from prompts.
    """
    
    @staticmethod
    @abstractmethod
    def stream_response(prompt: str) -> StreamResponse:
        """Generate a streaming response for the given prompt.
        
        Args:
            prompt: The user prompt to send to the AI service.
            
        Returns:
            A StreamResponse containing all streaming events and chunks.
        """
        pass
