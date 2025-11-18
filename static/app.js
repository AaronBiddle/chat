document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("promptForm");
  const input = document.getElementById("promptInput");
  const historyDiv = document.getElementById("history");
  const thinkingDiv = document.getElementById("thinking");
  const responseDiv = document.getElementById("response");

  // Create WinBox windows for the two panels, if WinBox is available
  if (window.WinBox) {
    const conversationPanel = document.getElementById("conversationPanel");
    const responsePanel = document.getElementById("responsePanel");

    if (conversationPanel) {
      conversationPanel.style.display = "block";
      new WinBox({
        title: "Conversation",
        x: "2%",
        y: "4%",
        width: "45%",
        height: "70%",
        background: "#101820",
        mount: conversationPanel,
      });
    }

    if (responsePanel) {
      responsePanel.style.display = "block";
      new WinBox({
        title: "Latest Response",
        x: "53%",
        y: "8%",
        width: "40%",
        height: "60%",
        background: "#182635",
        mount: responsePanel,
      });
    }
  }

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
