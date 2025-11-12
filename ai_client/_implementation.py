import os
from typing import List
from dotenv import find_dotenv, load_dotenv
import openai

from .schemas import StreamResponse, StreamEvent, StreamChunk


_env_path = find_dotenv()
if _env_path:
    load_dotenv(_env_path)

# Read Moonshot API key from environment
_MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY")

# Create an OpenAI client configured for Moonshot (keeps the public API stable)
client = openai.Client(
    base_url="https://api.moonshot.ai/v1",
    api_key=_MOONSHOT_API_KEY,
)


def call_ai_stream(prompt: str) -> StreamResponse:
    """Call the Chat Completions API and return a StreamResponse representing
    the streaming output.

    On any error we return a small fallback StreamResponse so callers can
    remain simple while the streaming UX is iterated separately.
    """
    # Hardcode the role for now; once we accept a full conversation we can
    # derive roles from the passed messages. Streaming responses here are the
    # assistant's output, so default to 'assistant'.
    role = "assistant"

    try:
        stream = client.chat.completions.create(
            model="kimi-k2-thinking",
            messages=[
                {"role": "system", "content": "You are Kimi."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1024 * 32,
            stream=True,
            temperature=1.0,
        )

        events: List[StreamEvent] = []
        index = 0
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
                events.append(
                    StreamEvent(chunks=[sc], event_id=None, is_final=False, error=None)
                )
                index += 1

        # Mark the last event as final if we produced any.
        if events:
            events[-1].is_final = True

        return StreamResponse(request_id=None, events=events, model="kimi-k2-thinking", meta=None)

    except Exception:
        # Resilient fallback: produce a short placeholder StreamResponse.
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
        # Return a minimal StreamResponse; request_id/meta are optional.
        return StreamResponse(request_id=None, events=[fallback_event], model=None, meta=None)