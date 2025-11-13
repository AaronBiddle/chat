import os
from typing import List, Iterator
from dotenv import find_dotenv, load_dotenv
import openai

from schemas import StreamEvent, StreamChunk
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
    def stream_response(prompt: str) -> Iterator[StreamEvent]:
        """Call the Chat Completions API and yield StreamEvent objects
        representing the streaming output as they arrive.
        """
        # Hardcode the role for now; once we accept a full conversation we can
        # derive roles from the passed messages. Streaming responses here are the
        # assistant's output, so default to 'assistant'.
        role = "assistant"

        try:
            stream = _client.chat.completions.create(
                model="kimi-k2-thinking",
                messages=[
                    {"role": "system", "content": "You are Kimi."},
                    {"role": "user", "content": prompt},
                ],
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

        except Exception:
            # Resilient fallback: yield a short placeholder final event.
            fallback_chunk = StreamChunk(
                text=(
                    "Hello — this is a placeholder AI response. Next: wire up a real API."
                ),
                index=0,
                delta=None,
                role=role,
                thinking=None,
            )
            fallback_event = StreamEvent(chunks=[fallback_chunk], event_id=None, is_final=True, error=None)
            yield fallback_event
            return
