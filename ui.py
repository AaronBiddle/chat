from flask import Flask, render_template, request, jsonify
from typing import List

from ai_client import Streamer, StreamViewer
from schemas import Message


app = Flask(__name__, static_folder="static", template_folder="templates")


# In-memory conversation storage (simple, not persisted)
messages: List[Message] = [Message(role="system", text="You are Kimi.")]


@app.route("/")
def index():
    # Render a simple UI showing the current conversation
    return render_template("index.html", messages=[m.dict() for m in messages])


@app.route("/reply", methods=["POST"])
def reply():
    """Accept a JSON payload with `prompt` and return aggregated response.

    This is intentionally simple: it calls the existing Streamer to obtain
    streaming events and then uses StreamViewer.render_and_aggregate to get
    the final text and any "thinking" tokens. The aggregated result is
    returned as JSON.
    """
    data = request.get_json(force=True)
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "empty prompt"}), 400

    # Add user message
    messages.append(Message(role="user", text=prompt))

    # Build and print the API payload that's sent to the streamer so you
    # can verify exactly what the remote API receives.
    api_messages = []
    for m in messages:
        try:
            r = getattr(m, "role")
            t = getattr(m, "text")
            api_messages.append({"role": r, "content": t})
        except Exception:
            if isinstance(m, dict):
                content = m.get("content", m.get("text"))
                api_messages.append({"role": m.get("role"), "content": content})
            else:
                continue

    print("\nMessages sent to streamer:")
    for m in api_messages:
        print(m)

    # Call the streamer and aggregate the response
    stream = Streamer.stream_response(messages)
    agg = StreamViewer.render_and_aggregate(stream, show_thinking=True)

    # Extract thinking and visible text. Only append non-thinking (visible)
    # text to the conversation history per your preference. The thinking
    # tokens are still returned to the client but not stored as assistant
    # messages unless visible text exists.
    thinking = agg.get("thinking", "") if isinstance(agg, dict) else ""
    text = agg.get("text", "") if isinstance(agg, dict) else ""
    assistant_text = text.strip()

    # Append assistant message only if visible (non-thinking) text exists.
    if assistant_text:
        messages.append(Message(role="assistant", text=assistant_text))

    return jsonify({
        "thinking": thinking,
        "text": text,
        "assistant_text": assistant_text,
        "messages": [m.dict() for m in messages],
    })


if __name__ == "__main__":
    # Run in debug mode by default for quick iteration
    app.run(host="127.0.0.1", port=5000, debug=True)
