document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("promptForm");
  const input = document.getElementById("promptInput");
  const historyDiv = document.getElementById("history");
  const thinkingDiv = document.getElementById("thinking");
  const responseDiv = document.getElementById("response");

  // Initialize Socket.IO client
  const socket = io();

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const prompt = input.value.trim();
    if (!prompt) return;

    thinkingDiv.textContent = "Thinking...";
    responseDiv.textContent = "";

    // Emit event to start streaming over Socket.IO
    socket.emit("start_stream", { prompt });
  });

  // Handle incremental stream chunks
  socket.on("stream_chunk", (data) => {
    try {
      if (data.chunks) {
        data.chunks.forEach((c) => {
          if (c.thinking) {
            thinkingDiv.textContent = (thinkingDiv.textContent || "") + c.thinking;
          }
          if (c.text) {
            responseDiv.textContent = responseDiv.textContent + c.text;
          }
        });
      }
    } catch (err) {
      console.error("Failed to handle stream_chunk", err, data);
    }
  });

  // Handle stream completion
  socket.on("stream_complete", (full) => {
    try {
      historyDiv.innerHTML = "";
      (full.messages || []).forEach((m) => {
        const el = document.createElement("div");
        el.className = "msg-" + m.role;
        el.innerHTML = `<strong>${m.role}:</strong> ${m.text}`;
        historyDiv.appendChild(el);
      });

      input.value = "";
    } catch (err) {
      console.error("Failed to handle stream_complete", err, full);
    }
  });

  socket.on("stream_error", (err) => {
    thinkingDiv.textContent = err && err.error ? err.error : "Stream error";
  });
});
