from flask import Flask, request, render_template_string, redirect, jsonify
import json
import subprocess
from snap_core import get_status, load_settings

app = Flask(__name__)
SETTINGS_FILE = "snap-settings.json"

LABELS = {
    "tibber_api_key": "Tibber API Key",
    "wiz_hostname": "Wiz Hostname",
    "wiz_fallback_ip": "Wiz Fallback IP",
    "home_index": "Home Index",
    "led": "Enable LED",
    "wiz": "Enable Wiz",
    "price_breakpoints": {
        "_label": "Price Breakpoints",
        "very_expensive": "Very Expensive Threshold",
        "expensive": "Expensive Threshold",
        "ok": "OK Price Threshold",
        "cheap": "Cheap Price Threshold"
    }
}

def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/", methods=["GET", "POST"])
def index():
    settings = load_settings()

    if request.method == "POST":
        for key in settings:
            if isinstance(settings[key], bool):
                settings[key] = request.form.get(key) == "on"
            elif isinstance(settings[key], dict):
                for subkey in settings[key]:
                    form_key = f"{key}.{subkey}"
                    if form_key in request.form:
                        settings[key][subkey] = float(request.form[form_key])
            else:
                original_value = settings[key]
                new_value = request.form.get(key, original_value)
                if isinstance(original_value, int):
                    settings[key] = int(new_value)
                elif isinstance(original_value, float):
                    settings[key] = float(new_value)
                else:
                    settings[key] = new_value

        save_settings(settings)

        if request.form.get("action") == "reboot":
          status = get_status()
          html = render_template_string(REBOOT_TEMPLATE, settings=settings, labels=LABELS, status=status)
          subprocess.Popen(["sudo", "reboot"])
          return html

        return redirect("/")

    status = get_status()

    return render_template_string(TEMPLATE, settings=settings, labels=LABELS, status=status)

@app.route("/api/status")
def api_status():
    status = get_status()
    return jsonify(status)

TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Snap</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="{{ url_for('static', filename='snap.css') }}">
</head>
{% set body_bg_class = {
  "very_expensive": "alert-danger",
  "expensive": "alert-danger",
  "ok": "alert-warning",
  "cheap": "alert-success",
  "very_cheap": "alert-success"
}[status.status] if status.status else "alert-light" %}

<body class="{{ body_bg_class }}">
  <div class="container py-5">
    <h1 class="mb-4">Snap Control Panel</h1>

    <ul class="nav nav-tabs" id="snapTab" role="tablist">
      <li class="nav-item" role="presentation">
        <button class="nav-link active" id="status-tab" data-bs-toggle="tab" data-bs-target="#status" type="button" role="tab">Status</button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link" id="settings-tab" data-bs-toggle="tab" data-bs-target="#settings" type="button" role="tab">Settings</button>
      </li>
    </ul>

    <div class="tab-content mt-4" id="snapTabContent">

      <!-- STATUS TAB -->
      <div class="tab-pane fade show active" id="status" role="tabpanel">
        {% if status.error %}
          <div class="alert alert-danger">Error fetching status: {{ status.error }}</div>
        {% else %}
          <div class="alert alert-light">
            <strong>Current energy:</strong> <span id="current-energy">{{ status.current_energy_display }}</span> kr/kWh<br>
            <strong>Status:</strong>
            <span id="status-label" class="badge">
              {{ status.status.replace('_', ' ').title() }}
            </span>
          </div>

          <div class="mt-4 bg-black text-white p-4 rounded shadow-sm">
            <p>
              <span class="status-led green on" id="status-led-now"></span>
              <span id="status-led-now-text">Loading...</span> (Right now)
            </p>

            <p>
              <span class="status-led green on" id="status-led-today"></span>
              <span id="status-led-today-text">Loading...</span> (Today)
            </p>

            <p id="sync-status">
              <span class="status-led blue" id="sync-led"></span>
              <span id="sync-text">Sync</span>
            </p>
          </div>

          <div class="alert alert-light mt-4">
            <canvas id="priceChart" responsive="true"></canvas>
          </div>

        {% endif %}
      </div>

      <!-- SETTINGS TAB -->
      <div class="tab-pane fade" id="settings" role="tabpanel">
        <form method="post" class="alert alert-light mt-4 p-4 bg-white">
          {% for key, value in settings.items() %}
            {% if value is mapping %}
              <fieldset class="mb-3">
                <legend class="h5">
                  {{ labels.get(key, {}).get('_label', key.replace('_', ' ').title()) }}
                </legend>
                <div class="row">
                  {% for subkey, subvalue in value.items() %}
                    {% if subkey != '_label' %}
                      <div class="mb-3 col-md-6">
                        <label class="form-label">
                          {{ labels.get(key, {}).get(subkey, subkey.replace('_', ' ').title()) }}
                        </label>
                        <input type="text" name="{{ key }}.{{ subkey }}" value="{{ subvalue }}" class="form-control">
                      </div>
                    {% endif %}
                  {% endfor %}
                </div>
              </fieldset>
            {% elif value is boolean %}
              <div class="form-check form-switch mb-3">
                <input class="form-check-input" type="checkbox" name="{{ key }}" id="{{ key }}" {% if value %}checked{% endif %}>
                <label class="form-check-label" for="{{ key }}">{{ labels.get(key, key.replace('_', ' ').title()) }}</label>
              </div>
            {% else %}
              <div class="mb-3">
                <label class="form-label">{{ labels.get(key, key.replace('_', ' ').title()) }}</label>
                <input type="text" name="{{ key }}" value="{{ value }}" class="form-control">
              </div>
            {% endif %}
          {% endfor %}
          <div class="d-flex gap-2 mt-4">
            <button type="submit" name="action" value="save" class="btn btn-primary">Save</button>
            <button type="submit" name="action" value="reboot" class="btn btn-danger"
              onclick="return confirm('Are you sure you want to reboot Snap?');">
              Save and Reboot
            </button>
          </div>
        </form>
      </div>

      <small class="github"><a href="https://github.com/jonkpirateboy/Snap" target="_blank">GitHub</a></small>

    </div>
  </div>

  <!-- Bootstrap JS for tabs -->
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script src="{{ url_for('static', filename='snap.js') }}"></script>

</body>
</html>
"""

REBOOT_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Rebooting snap...</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="{{ url_for('static', filename='snap.css') }}">
</head>
{% set body_bg_class = {
  "very_expensive": "alert-danger",
  "expensive": "alert-danger",
  "ok": "alert-warning",
  "cheap": "alert-success",
  "very_cheap": "alert-success"
}[status.status] if status.status else "alert-light" %}

<body class="{{ body_bg_class }}">
  <div class="container py-5 text-center">
    <div class="alert alert-light p-4" role="alert">
      <h4 class="alert-heading mb-3">Rebooting...</h4>
      <div class="d-flex justify-content-center align-items-center mb-3">
        <div class="spinner-border spinner" role="status" aria-hidden="true"></div>
      </div>
      <p>The Snap device is rebooting. This page will automatically return once it's back online.</p>
      <a href="/" class="btn btn-secondary mt-3">Return manually</a>
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
  <script src="{{ url_for('static', filename='snap.js') }}"></script>
  <script>
    function checkServer() {
      fetch("/", { method: "HEAD" })
        .then(() => window.location.href = "/")
        .catch(() => setTimeout(checkServer, 5000));
    }
    setTimeout(checkServer, 10000);
  </script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
