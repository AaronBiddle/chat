from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from typing import List
import json

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


@app.route("/stream", methods=["GET", "POST"])
def stream_reply():
    """Stream incremental events to the browser using Server-Sent Events (SSE).

    Accepts either GET with `?prompt=...` or POST with JSON `{prompt: ...}`.
    The endpoint will append the user message, call the Streamer, and yield
    events as JSON payloads. When the stream ends, if any visible text was
    produced it is appended as an assistant message.
    """
    if request.method == "POST":
        data = request.get_json(force=True)
        prompt = data.get("prompt", "")
    else:
        prompt = request.args.get("prompt", "")

    if not prompt:
        return jsonify({"error": "empty prompt"}), 400

    # Add user message
    messages.append(Message(role="user", text=prompt))

    # Build and print API payload for verification
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

    print("\nMessages sent to streamer (SSE):")
    for m in api_messages:
        print(m)

    def event_stream():
        stream = Streamer.stream_response(messages)
        text_buf = []
        thinking_buf = []

        for ev in stream:
            # ev is a pydantic model; convert to plain dict for JSON
            try:
                payload = ev.dict()
            except Exception:
                # best-effort fallback
                payload = {"chunks": [], "is_final": getattr(ev, "is_final", False)}

            # Yield the SSE data frame
            yield f"data: {json.dumps(payload)}\n\n"

            # Accumulate visible text and thinking tokens
            for c in payload.get("chunks", []):
                if c.get("thinking"):
                    thinking_buf.append(c.get("thinking"))
                if c.get("text"):
                    text_buf.append(c.get("text"))

            if payload.get("is_final"):
                # On final, append assistant visible text only (if present)
                assistant_text = "".join(text_buf).strip()
                if assistant_text:
                    messages.append(Message(role="assistant", text=assistant_text))
                break

    return Response(stream_with_context(event_stream()), mimetype="text/event-stream")


@app.route("/messages", methods=["GET"])
def get_messages():
    """Return the current conversation messages without modifying state.

    This is a read-only endpoint intended for the UI to refresh conversation
    history after streaming completes. It avoids re-posting prompts which
    previously caused duplicate entries.
    """
    return jsonify({"messages": [m.dict() for m in messages]})


if __name__ == "__main__":
    # Run in debug mode by default for quick iteration
    app.run(host="127.0.0.1", port=5000, debug=True)
