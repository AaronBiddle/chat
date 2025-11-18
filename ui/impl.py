from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from typing import List, Optional, Any, Dict
import json

from ai_client import Streamer, StreamViewer
from schemas import Message
from .interface import WebUIClass


class FlaskWebUI(WebUIClass):
    """Flask-based web UI implementation.

    Provides HTTP endpoints for chat interaction including both
    aggregated responses and server-sent event streaming. Maintains
    in-memory conversation state.
    """

    def __init__(self, initial_messages: Optional[List[Message]] = None):
        """Initialize Flask web UI with conversation state.

        Args:
            initial_messages: Optional starting messages. If None, defaults
                to a system message defining the assistant persona.
        """
        self.app = Flask(__name__, static_folder="../static", template_folder="../templates")
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Initialize conversation history
        if initial_messages is None:
            self.messages: List[Message] = [Message(role="system", text="You are Kimi.")]
        else:
            self.messages = list(initial_messages)

        # Register routes
        self._register_routes()

    def get_messages(self) -> List[Message]:
        """Return current conversation history."""
        return self.messages

    def add_message(self, message: Message) -> None:
        """Add a message to conversation history."""
        self.messages.append(message)

    def clear_messages(self) -> None:
        """Clear all messages from conversation."""
        self.messages.clear()

    def run(self, host: str = "127.0.0.1", port: int = 5000, debug: bool = True) -> None:
        """Start the Flask development server."""
        # Use SocketIO's run method to support WebSocket transport
        self.socketio.run(self.app, host=host, port=port, debug=debug)

    def get_app(self) -> Flask:
        """Return the Flask application instance."""
        return self.app

    def _register_routes(self) -> None:
        """Register all Flask routes. Internal implementation detail."""
        
        @self.app.route("/")
        def index():
            """Render the main chat interface."""
            return render_template("index.html", messages=[m.dict() for m in self.messages])

        @self.app.route("/reply", methods=["POST"])
        def reply():
            """Accept a JSON payload with `prompt` and return aggregated response.

            This endpoint calls the Streamer to obtain streaming events and uses
            StreamViewer.render_and_aggregate to get the final text and thinking
            tokens. The aggregated result is returned as JSON.
            """
            data = request.get_json(force=True)
            prompt = data.get("prompt", "")
            if not prompt:
                return jsonify({"error": "empty prompt"}), 400

            # Add user message
            self.messages.append(Message(role="user", text=prompt))

            # Build and print the API payload for verification
            api_messages = self._build_api_messages()
            print("\nMessages sent to streamer:")
            for m in api_messages:
                print(m)

            # Call the streamer and aggregate the response
            stream = Streamer.stream_response(self.messages)
            agg = StreamViewer.render_and_aggregate(stream, show_thinking=True)

            # Extract thinking and visible text
            thinking = agg.get("thinking", "") if isinstance(agg, dict) else ""
            text = agg.get("text", "") if isinstance(agg, dict) else ""
            assistant_text = text.strip()

            # Append assistant message only if visible text exists
            if assistant_text:
                self.messages.append(Message(role="assistant", text=assistant_text))

            return jsonify({
                "thinking": thinking,
                "text": text,
                "assistant_text": assistant_text,
                "messages": [m.dict() for m in self.messages],
            })

        # Socket.IO event handler for streaming replies
        @self.socketio.on("start_stream")
        def handle_start_stream(data):
            """Handle a new streaming request over Socket.IO.

            Expects payload: {"prompt": "..."}. Emits incremental
            "stream_chunk" events and a final "stream_complete" event
            with aggregated content.
            """
            prompt = (data or {}).get("prompt", "")
            if not prompt:
                emit("stream_error", {"error": "empty prompt"})
                return

            # Add user message
            self.messages.append(Message(role="user", text=prompt))

            # Build and print API payload for verification
            api_messages = self._build_api_messages()
            print("\nMessages sent to streamer (Socket.IO):")
            for m in api_messages:
                print(m)

            stream = Streamer.stream_response(self.messages)
            text_buf = []
            thinking_buf = []

            for ev in stream:
                try:
                    payload = ev.dict()
                except Exception:
                    payload = {"chunks": [], "is_final": getattr(ev, "is_final", False)}

                # Emit incremental chunk event
                emit("stream_chunk", payload)

                for c in payload.get("chunks", []):
                    if c.get("thinking"):
                        thinking_buf.append(c.get("thinking"))
                    if c.get("text"):
                        text_buf.append(c.get("text"))

                if payload.get("is_final"):
                    assistant_text = "".join(text_buf).strip()
                    if assistant_text:
                        self.messages.append(Message(role="assistant", text=assistant_text))

                    emit("stream_complete", {
                        "thinking": "".join(thinking_buf),
                        "text": "".join(text_buf),
                        "assistant_text": assistant_text,
                        "messages": [m.dict() for m in self.messages],
                    })
                    break

        @self.app.route("/messages", methods=["GET"])
        def get_messages():
            """Return current conversation messages without modifying state.

            Read-only endpoint for the UI to refresh conversation history
            after streaming completes.
            """
            return jsonify({"messages": [m.dict() for m in self.messages]})

    def _build_api_messages(self) -> List[Dict[str, str]]:
        """Build API-compatible message list. Internal helper method."""
        api_messages = []
        for m in self.messages:
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
        return api_messages
