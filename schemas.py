from typing import Optional, List, Union
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class StreamChunk(BaseModel):
    """A single chunk (token or text fragment) emitted by the streaming API.

    Fields:
      - text: the text content of the chunk (decoded).
      - index: optional sequence index for ordering.
      - delta: optional raw delta payload when applicable (kept generic).
      - role: optional role (e.g., 'assistant' or 'user') if present on this chunk.
    """

    text: Optional[str] = Field(
        None,
        description=(
            "The text content of this chunk (optional). Some chunks may only contain "
            "thinking/internal tokens and therefore omit `text`."
        ),
    )
    index: Optional[int] = Field(None, description="Optional sequence index")
    delta: Optional[dict] = Field(None, description="Raw delta payload when available")
    role: Optional[str] = Field(None, description="Optional role for this chunk")
    thinking: Optional[str] = Field(
        None,
        description=(
            "Optional thinking/internal text for this chunk. "
            "If present, consumers can treat this string the same way they treat `text` "
            "(e.g., render as internal reasoning)."
        ),
    )


class StreamEvent(BaseModel):
    """A richer event wrapper for stream messages.

    Use this when you want metadata attached to chunks (timestamps, ids, final flags).
    """

    chunks: List[StreamChunk] = Field(..., description="One or more chunks in this event")
    event_id: Optional[str] = Field(None, description="An optional event identifier")
    is_final: bool = Field(False, description="True if this event completes the stream")
    error: Optional[str] = Field(None, description="Error message if the event represents an error")


class Message(BaseModel):
    """A single message in a conversation.

    This model is a slightly higher-level wrapper than `StreamChunk` and can
    represent a complete message (with optional metadata and timestamp).
    """
    role: str = Field(..., description="Role such as 'user' or 'assistant'")
    text: str = Field(..., description="Decoded text content of the message")
    thinking: Optional[str] = Field(None, description="Optional internal/thinking text")

