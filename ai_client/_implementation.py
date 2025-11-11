import os
from dotenv import find_dotenv, load_dotenv
import openai

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


def call_ai(prompt: str) -> None:
    """Call the Chat Completions API via the configured `client`.

    This attempts to use the streaming API and assemble the response. On any
    error (network, library differences, etc.) we fall back to the original
    stubbed response so calling code remains simple while you iterate.
    """
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

        parts: list[str] = []
        thinking = False
        for chunk in stream:
            if chunk.choices:
                choice = chunk.choices[0]
                if choice.delta and hasattr(choice.delta, "reasoning_content"):
                    if not thinking:
                        thinking = True
                        print("=============Start Reasoning=============")
                    print(getattr(choice.delta, "reasoning_content"), end="")
                if choice.delta and choice.delta.content:
                    if thinking:
                        thinking = False
                        print("\n=============End Reasoning=============")
                    print(choice.delta.content, end="")

    except Exception:
        # Keep the original stub as a resilient fallback.
        print("Hello — this is a placeholder AI response. Next: wire up a real API.")