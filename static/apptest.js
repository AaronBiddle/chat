document.addEventListener("DOMContentLoaded", function () {
  // Simple demo: create a fake "assistant message" with a thinking toggle
  const historyDiv = document.getElementById("history");
  if (!historyDiv) return;

  const msgWrapper = document.createElement("div");
  msgWrapper.className = "msg-assistant";

  const header = document.createElement("div");
  header.innerHTML = "<strong>assistant:</strong>";

  const thinkingToggle = document.createElement("button");
  thinkingToggle.type = "button";
  thinkingToggle.textContent = "Show thinking";
  thinkingToggle.className = "thinking-toggle";

  const thinkingDiv = document.createElement("div");
  thinkingDiv.className = "thinking-body";
  thinkingDiv.style.display = "none";
  thinkingDiv.style.whiteSpace = "pre-wrap";

  const responseDiv = document.createElement("div");
  responseDiv.className = "response-body";

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

  // Simulate streamed thinking + response via a timer
  setTimeout(() => {
    thinkingDiv.textContent = "These are some inner thoughts that will stream in...";
    responseDiv.textContent = "This is the visible response text.";
  }, 1000);
});
