# chat (minimal)

This tiny project demonstrates a minimal pattern for calling an AI from a small application.

Structure
- `main.py` — small runner that calls the public `ai_client.call_ai` function and prints the single response.
- `ai_client/__init__.py` — public package interface (re-exports `call_ai`).
- `ai_client/_implementation.py` — private implementation (currently a stubbed response).

Usage

Make sure you have Python installed (3.8+ recommended). From the project root (`c:\Projects\chat`) run:

```powershell
python c:\Projects\chat\main.py
```

Expected output (one-line AI response):

```
Hello — this is a placeholder AI response. Next: wire up a real API.
```

Notes
- The implementation is intentionally a stub so you can focus on design and flow. Later you can replace `_implementation.py` with a real HTTP client or other provider and keep the public API stable.
- To change the package API surface, edit `ai_client/__init__.py` and consider adding `__all__` to control what gets exported.
