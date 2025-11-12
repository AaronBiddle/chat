from typing import Optional, List
from pydantic import BaseModel, Field


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


class StreamResponse(BaseModel):
    """The full streaming response shape (for future use).

    This model represents the full response that a streaming operation may produce.
    It intentionally mirrors common chat-stream shapes: a sequence of events plus
    optional metadata about the request/response.
    """

    request_id: Optional[str] = Field(None, description="Original request id if available")
    events: List[StreamEvent] = Field(..., description="Ordered list of stream events")
    model: Optional[str] = Field(None, description="Model used to produce the stream")
    meta: Optional[dict] = Field(None, description="Additional metadata")
