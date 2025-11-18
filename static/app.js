document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("promptForm");
  const input = document.getElementById("promptInput");
  const historyDiv = document.getElementById("history");
  let activeThinkingEl = null;
  let activeResponseEl = null;
  let initialMessagesRendered = false;

  // Create WinBox windows for the two panels, if WinBox is available
  if (window.WinBox) {
    const chatPanel = document.getElementById("chatPanel");

    if (chatPanel) {
      chatPanel.style.display = "block";
      new WinBox({
        title: "Chat",
        x: "8%",
        y: "6%",
        width: "70%",
        height: "75%",
        background: "#101820",
        mount: chatPanel,
      });
    }
  }

  // Initialize Socket.IO client
  const socket = io();

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const prompt = input.value.trim();
    if (!prompt) return;

    // Create a new message block with its own collapsible thinking area
    const msgWrapper = document.createElement("div");
    msgWrapper.className = "msg-assistant";

    const header = document.createElement("div");
    header.innerHTML = `<strong>assistant:</strong>`;

    const responseDiv = document.createElement("div");
    responseDiv.className = "response-body";

    const thinkingToggle = document.createElement("button");
    thinkingToggle.type = "button";
    thinkingToggle.textContent = "Show thinking";
    thinkingToggle.className = "thinking-toggle";

    const thinkingDiv = document.createElement("div");
    thinkingDiv.className = "thinking-body";
    thinkingDiv.style.display = "none";
    thinkingDiv.style.whiteSpace = "pre-wrap";

    thinkingToggle.addEventListener("click", () => {
      const isHidden = thinkingDiv.style.display === "none";
      thinkingDiv.style.display = isHidden ? "block" : "none";
      thinkingToggle.textContent = isHidden ? "Hide thinking" : "Show thinking";
    });

    msgWrapper.appendChild(header);
    msgWrapper.appendChild(thinkingToggle);
    msgWrapper.appendChild(thinkingDiv);
    msgWrapper.appendChild(responseDiv);
    historyDiv.appendChild(msgWrapper);

    activeResponseEl = responseDiv;
    activeThinkingEl = thinkingDiv;

    // Emit event to start streaming over Socket.IO
    socket.emit("start_stream", { prompt });
  });

  // Handle incremental stream chunks
  socket.on("stream_chunk", (data) => {
    try {
      if (data.chunks) {
        data.chunks.forEach((c) => {
          if (c.thinking) {
            if (activeThinkingEl) {
              activeThinkingEl.textContent = (activeThinkingEl.textContent || "") + c.thinking;
            }
          }
          if (c.text) {
            if (activeResponseEl) {
              activeResponseEl.textContent = activeResponseEl.textContent + c.text;
            }
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
      const messages = full.messages || [];

      // On the very first completion, render any system/user messages
      // that the server sent (initial context) once at the top.
      if (!initialMessagesRendered) {
        messages.forEach((m) => {
          if (m.role === "assistant") return;
          const el = document.createElement("div");
          el.className = "msg-" + m.role;
          el.innerHTML = `<strong>${m.role}:</strong> ${m.text}`;
          historyDiv.appendChild(el);
        });
        initialMessagesRendered = true;
      }

      input.value = "";
      activeThinkingEl = null;
      activeResponseEl = null;
    } catch (err) {
      console.error("Failed to handle stream_complete", err, full);
    }
  });

  socket.on("stream_error", (err) => {
    if (activeThinkingEl) {
      activeThinkingEl.style.display = "block";
      activeThinkingEl.textContent = err && err.error ? err.error : "Stream error";
    }
  });
});
