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

    # Call the streamer and aggregate the response
    stream = Streamer.stream_response(messages)
    agg = StreamViewer.render_and_aggregate(stream, show_thinking=True)

    assistant_text = agg.get("text", "") if isinstance(agg, dict) else ""
    # Append assistant message to conversation
    messages.append(Message(role="assistant", text=assistant_text))

    return jsonify({"thinking": agg.get("thinking"), "text": assistant_text, "messages": [m.dict() for m in messages]})


if __name__ == "__main__":
    # Run in debug mode by default for quick iteration
    app.run(host="127.0.0.1", port=5000, debug=True)
