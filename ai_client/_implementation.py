import os
import openai

client = openai.Client(
    base_url="https://api.moonshot.cn/v1",
    api_key=os.getenv("MOONSHOT_API_KEY"),
)


def call_ai(prompt: str) -> str:
    """Private implementation (stub for now)."""
    return "Hello — this is a placeholder AI response. Next: wire up a real API."