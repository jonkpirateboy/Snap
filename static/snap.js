// snap.js

function updateStatus() {
  fetch("/api/status")
    .then(response => response.json())
    .then(data => {
      updateLed("status-led-now", data.status);
      updateLed("status-led-today", data.average_status);
      triggerSyncAnimation();

      // 🔧 Lägg till Bootstrap-bakgrund på <body>
      const body = document.body;
      if (body) {
        body.className = "";
        const bgMap = {
          very_expensive: "alert-danger",
          expensive: "alert-danger",
          ok: "alert-warning",
          cheap: "alert-success",
          very_cheap: "alert-success"
        };
        body.classList.add(bgMap[data.status] || "alert-light");
      }
    });
}


function updateLed(id, status) {
  const led = document.getElementById(id);
  const text = document.getElementById(id + "-text");

  let color = "";
  let label = "";

  if (status === "very_expensive") {
    color = "red"; label = "Very Expensive";
  } else if (status === "expensive") {
    color = "orange"; label = "Expensive";
  } else if (status === "ok") {
    color = "orange"; label = "OK";
  } else if (status === "cheap") {
    color = "green"; label = "Cheap";
  } else {
    color = "green"; label = "Very Cheap";
  }

  if (led) {
    led.className = `status-led ${color} on`;
  }
  if (text) {
    text.textContent = label;
  }
}

function triggerSyncAnimation() {
  const led = document.getElementById("sync-led");
  const text = document.getElementById("sync-text");
  if (led && text) {
    led.classList.add("on");
    text.textContent = "Syncing...";
    setTimeout(() => {
      led.classList.remove("on");
      text.textContent = "Sync";
    }, 1000);
  }
}

window.addEventListener("DOMContentLoaded", () => {
  updateStatus();
  setInterval(updateStatus, 60000); // every 60 seconds
});

// Update status info box
const energyEl = document.getElementById("current-energy");
const labelEl = document.getElementById("status-label");
const alertEl = document.getElementById("status-alert");

if (energyEl) energyEl.textContent = data.current_energy.toFixed(2);

if (labelEl) {
  const labels = {
    very_expensive: "Very Expensive",
    expensive: "Expensive",
    ok: "OK",
    cheap: "Cheap",
    very_cheap: "Very Cheap"
  };
  labelEl.textContent = labels[data.status] || data.status;
}
