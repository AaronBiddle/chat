"""Thin entry point for running the web UI server.

This script instantiates the FlaskWebUI implementation and runs it.
It serves as a simple executable entry point that delegates all logic
to the implementation.
"""

from ui import FlaskWebUI


def main() -> None:
    """Initialize and run the web UI server."""
    web_ui = FlaskWebUI()
    web_ui.run(host="127.0.0.1", port=5000, debug=True)


if __name__ == "__main__":
    main()
