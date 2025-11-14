document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("promptForm");
  const input = document.getElementById("promptInput");
  const historyDiv = document.getElementById("history");
  const thinkingDiv = document.getElementById("thinking");
  const responseDiv = document.getElementById("response");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const prompt = input.value.trim();
    if (!prompt) return;

    thinkingDiv.textContent = "Thinking...";
    responseDiv.textContent = "";

    try {
      const res = await fetch("/reply", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });

      if (!res.ok) {
        const err = await res.json();
        thinkingDiv.textContent = "Error: " + (err.error || res.statusText);
        return;
      }

      const data = await res.json();

      thinkingDiv.textContent = data.thinking || "";
      responseDiv.textContent = data.text || "";

      // Refresh conversation history
      historyDiv.innerHTML = "";
      (data.messages || []).forEach((m) => {
        const el = document.createElement("div");
        el.className = "msg-" + m.role;
        el.innerHTML = `<strong>${m.role}:</strong> ${m.text}`;
        historyDiv.appendChild(el);
      });

      input.value = "";
    } catch (err) {
      thinkingDiv.textContent = "Network error";
    }
  });
});
