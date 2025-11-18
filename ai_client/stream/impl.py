import os
from typing import List, Iterator
from dotenv import find_dotenv, load_dotenv
import openai

from schemas import StreamEvent, StreamChunk, Message
from .interface import StreamerClass


_env_path = find_dotenv()
if _env_path:
    load_dotenv(_env_path)

# Read Moonshot API key from environment
_MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY")

# Create an OpenAI client configured for Moonshot (keeps the public API stable)
_client = openai.Client(
    base_url="https://api.moonshot.ai/v1",
    api_key=_MOONSHOT_API_KEY,
)


class Streamer(StreamerClass):
    """Moonshot AI streaming implementation.

    Stateless streamer that calls the Moonshot API and yields StreamEvent objects
    as they arrive.
    """
    
    @staticmethod
    def stream_response(messages: List[Message]) -> Iterator[StreamEvent]:
        """Call the Chat Completions API and yield StreamEvent objects
        representing the streaming output as they arrive.

        Accepts a list of `Message` objects (conversation history). These are
        converted to the underlying API format (dicts with `role` and
        `content`) before sending.
        """
        # Streaming responses here are the assistant's output, so default to
        # 'assistant' for chunk role metadata unless the API provides one.
        role = "assistant"

        # Convert provided `Message` objects to the API message format. Support
        # both `Message` instances and plain dicts for convenience.
        api_messages = []
        for m in messages:
            try:
                # pydantic model: has 'role' and 'text'
                r = getattr(m, "role")
                t = getattr(m, "text")
                api_messages.append({"role": r, "content": t})
            except Exception:
                # Fallback for plain dicts passed in mistakenly
                if isinstance(m, dict):
                    # prefer 'content' if present, otherwise 'text'
                    content = m.get("content", m.get("text"))
                    api_messages.append({"role": m.get("role"), "content": content})
                else:
                    # Skip unknown entries
                    continue

        # If no API key is configured, do not call the remote API.
        # Yield a clear error event so the UI can surface it, instead of
        # falling back to a generic placeholder assistant message.
        if not _MOONSHOT_API_KEY:
            yield StreamEvent(
                chunks=[],
                event_id=None,
                is_final=True,
                error="Moonshot API key is not configured. Set MOONSHOT_API_KEY in your environment.",
            )
            return

        try:
            stream = _client.chat.completions.create(
                model="kimi-k2-thinking",
                messages=api_messages,
                max_tokens=1024 * 32,
                stream=True,
                temperature=1.0,
            )

            index = 0
            yielded_any = False
            for chunk in stream:
                # Each chunk may contain one or more deltas; the client library
                # shapes these objects differently, so we defensively probe fields.
                if chunk.choices:
                    choice = chunk.choices[0]
                    delta_obj = getattr(choice, "delta", None)

                    thinking_text = None
                    text = None
                    raw_delta = None

                    if delta_obj is not None:
                        # Try common attributes used in streaming payloads.
                        thinking_text = getattr(delta_obj, "reasoning_content", None)
                        text = getattr(delta_obj, "content", None)
                        # Best-effort raw delta capture (may be an object)
                        try:
                            raw_delta = delta_obj.__dict__
                        except Exception:
                            raw_delta = None

                    sc = StreamChunk(
                        text=text, index=index, delta=raw_delta, role=role, thinking=thinking_text
                    )
                    ev = StreamEvent(chunks=[sc], event_id=None, is_final=False, error=None)
                    yield ev
                    yielded_any = True
                    index += 1

            # Signal end of stream: yield an empty final event so viewers
            # can display a final marker.
            if yielded_any:
                yield StreamEvent(chunks=[], event_id=None, is_final=True, error=None)
                return

            # No events produced; yield a final empty event to indicate completion
            yield StreamEvent(chunks=[], event_id=None, is_final=True, error=None)
            return

        except Exception as e:
            # On error, yield a final event carrying the error message so
            # callers can display it, rather than emitting placeholder text.
            yield StreamEvent(
                chunks=[],
                event_id=None,
                is_final=True,
                error=str(e),
            )
            return
