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

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique message identifier")
    role: Optional[str] = Field(None, description="Role such as 'user' or 'assistant'")
    text: Optional[str] = Field(None, description="Decoded text content of the message")
    index: Optional[int] = Field(None, description="Sequence index within the conversation")
    delta: Optional[dict] = Field(None, description="Optional raw/delta payload")
    thinking: Optional[str] = Field(None, description="Optional internal/thinking text")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="UTC timestamp for the message")
    metadata: Optional[dict] = Field(None, description="Optional freeform metadata for this message")


class Conversation(BaseModel):
    """A container for an AI conversation.

    Responsibilities:
      - hold the ordered list of `Message` objects
      - track participants, metadata, timestamps
      - provide helpers to add/query messages
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique conversation id")
    title: Optional[str] = Field(None, description="Optional human-readable title")
    participants: List[str] = Field(default_factory=list, description="List of participant identifiers")
    messages: List[Message] = Field(default_factory=list, description="Ordered list of messages in the conversation")
    metadata: Optional[dict] = Field(None, description="Optional arbitrary metadata for the conversation")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation time (UTC)")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last-updated time (UTC)")
    model_name: Optional[str] = Field(None, description="Optional model name used for this conversation")
    is_archived: bool = Field(False, description="Whether this conversation is archived/read-only")

    def add_message(self, message: Union[Message, dict]) -> Message:
        """Append a message to the conversation.

        Accepts either a `Message` instance or a dict that can be used to construct one.
        The message `index` will be set if not provided; `updated_at` is updated.
        """

        if isinstance(message, dict):
            msg = Message(**message)
        elif isinstance(message, Message):
            msg = message
        else:
            raise TypeError("message must be a Message or dict")

        if msg.index is None:
            msg.index = len(self.messages)

        self.messages.append(msg)
        self.updated_at = datetime.utcnow()
        return msg

    def get_history(self, limit: Optional[int] = None) -> List[Message]:
        """Return conversation history.

        If `limit` is provided return the most recent `limit` messages.
        """

        if limit is None:
            return list(self.messages)
        if limit <= 0:
            return []
        return list(self.messages[-limit:])

    def to_dict(self, include_messages: bool = True) -> dict:
        """Serialize conversation to a plain dict. Optionally exclude messages."""

        data = self.dict()
        if not include_messages:
            data.pop("messages", None)
        return data


