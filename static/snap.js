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
      console.log("Chart data:", data.raw_hours);
      if (data.raw_hours) {
        renderChart(data.raw_hours);
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

if (energyEl) energyEl.textContent = data.current_energy.toFixed(2).replace('.', ',');

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

// Chart
let chart;

function renderChart(data) {
  const canvas = document.getElementById("priceChart");
  if (!canvas) return;

  const ctx = canvas.getContext('2d');

  const labels = data.map(item => {
    const date = new Date(item.startsAt);
    return !isNaN(date) ? date.getHours().toString().padStart(2, "0") + ":00" : "??";
  });

  const prices = data.map(item => item.total ?? null);

  if (chart) chart.destroy(); // Reset existing chart

  chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels,
        datasets: [{
        label: 'kr/kWh',
        data: prices,
        segment: {
            borderColor: ctx => {
            const y = ctx.p0.parsed.y;
            if (y > 2.0) return 'red';
            if (y > 1.5) return 'orange';
            if (y > 1.0) return 'gold';
            if (y > 0.5) return 'green';
            return 'lightgreen';
            }
        },
        pointBackgroundColor: prices.map(y => {
            if (y > 2.0) return 'red';
            if (y > 1.5) return 'orange';
            if (y > 1.0) return 'gold';
            if (y > 0.5) return 'green';
            return 'lightgreen';
        }),
        backgroundColor: 'rgba(0,0,0,0)', // no fill
        fill: false,
        tension: 0.3,
        pointRadius: 5
        }]
    },
    options: {
        animation: false,
        responsive: true,
        plugins: {
        legend: {
            labels: {
            usePointStyle: true,
            pointStyle: 'line',
            color: '#000'
            }
        },
        tooltip: {
            mode: 'nearest',
            intersect: false,
            displayColors: false,
            callbacks: {
                label: function(context) {
                return `${context.parsed.y.toFixed(2).replace('.', ',')} kr/kWh`;
                }
            }
        }
        },
        scales: {
        y: {
            beginAtZero: true,
            title: {
            display: true,
            text: 'kr/kWh'
            }
        },
        x: {
            title: {
            display: true,
            text: 'Hour'
            }
        }
        }
    }
    });

}
