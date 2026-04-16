// Frontend renderer script - runs in the browser context
const API_URL = "http://127.0.0.1:5000";

document.addEventListener("DOMContentLoaded", () => {
  const clickButton = document.getElementById("clickMeBtn");
  const responseMessage = document.getElementById("responseMessage");

  if (clickButton) {
    clickButton.addEventListener("click", async () => {
      try {
        responseMessage.textContent = "Sending request...";
        responseMessage.style.color = "blue";

        const response = await fetch(`${API_URL}/api/click`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ timestamp: new Date().toISOString() }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        responseMessage.textContent = `Response: ${data.message} (${data.status})`;
        responseMessage.style.color = "green";
      } catch (error) {
        responseMessage.textContent = `Error: Could not reach API. Make sure the Flask server is running. (${error.message})`;
        responseMessage.style.color = "red";
        console.error("API call failed:", error);
      }
    });
  }
});