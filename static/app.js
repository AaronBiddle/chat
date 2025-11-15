document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("promptForm");
  const input = document.getElementById("promptInput");
  const historyDiv = document.getElementById("history");
  const thinkingDiv = document.getElementById("thinking");
  const responseDiv = document.getElementById("response");

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const prompt = input.value.trim();
    if (!prompt) return;

    thinkingDiv.textContent = "Thinking...";
    responseDiv.textContent = "";

    // Use EventSource with GET query param for SSE streaming
    const url = "/stream?prompt=" + encodeURIComponent(prompt);
    const es = new EventSource(url);

    let text_acc = "";

    es.onmessage = (evt) => {
      try {
        const data = JSON.parse(evt.data);

        // Update thinking area incrementally (join chunk thinking tokens)
        if (data.chunks) {
          data.chunks.forEach((c) => {
            if (c.thinking) {
              thinkingDiv.textContent = (thinkingDiv.textContent || "") + c.thinking;
            }
            if (c.text) {
              responseDiv.textContent = responseDiv.textContent + c.text;
              text_acc += c.text;
            }
          });
        }

        if (data.is_final) {
          // Finalize: close EventSource and refresh history
          es.close();

          // Refresh conversation history by fetching messages (read-only)
          fetch("/messages")
            .then((r) => r.json())
            .then((full) => {
              historyDiv.innerHTML = "";
              (full.messages || []).forEach((m) => {
                const el = document.createElement("div");
                el.className = "msg-" + m.role;
                el.innerHTML = `<strong>${m.role}:</strong> ${m.text}`;
                historyDiv.appendChild(el);
              });
            })
            .catch(() => {});

          input.value = "";
        }
      } catch (err) {
        console.error("Failed to parse SSE data", err, evt.data);
      }
    };

    es.onerror = (err) => {
      thinkingDiv.textContent = "Stream error";
      es.close();
    };
  });
});
