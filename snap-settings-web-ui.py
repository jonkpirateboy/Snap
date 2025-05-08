from flask import Flask, request, render_template_string, redirect
import json
import subprocess

app = Flask(__name__)
SETTINGS_FILE = "snap-settings.json"

# --- User-Friendly Labels ---

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

# --- Utility Functions ---

def load_settings():
    with open(SETTINGS_FILE) as f:
        return json.load(f)

def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# --- Routes ---

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
            subprocess.Popen(["sudo", "reboot"])
            return render_template_string(REBOOT_TEMPLATE)

        return redirect("/")

    return render_template_string(TEMPLATE, settings=settings, labels=LABELS)

# --- HTML Template ---

TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Snap Settings</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link 
    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" 
    rel="stylesheet"
  >
</head>
<body class="bg-light">
  <div class="container py-5">
    <h1 class="mb-4">Snap Control Panel</h1>
    <form method="post" class="bg-white p-4 rounded shadow-sm">
      {% for key, value in settings.items() %}
        {% if value is mapping %}
          <fieldset class="mb-3">
            <legend class="h5">
              {{ labels.get(key, {}).get('_label', key.replace('_', ' ').title()) }}
            </legend>
            <div class="row">
              {% for subkey, subvalue in value.items() %}
                <div class="mb-3 col-md-6">
                  <label class="form-label">{{ labels.get(key, {}).get(subkey, subkey) }}</label>
                  <input type="text" name="{{ key }}.{{ subkey }}" value="{{ subvalue }}" class="form-control">
                </div>
              {% endfor %}
            </div>
          </fieldset>
        {% elif value is boolean %}
          <div class="form-check form-switch mb-3">
            <input class="form-check-input" type="checkbox" name="{{ key }}" id="{{ key }}" {% if value %}checked{% endif %}>
            <label class="form-check-label" for="{{ key }}">{{ labels.get(key, key) }}</label>
          </div>
        {% else %}
          <div class="mb-3">
            <label class="form-label">{{ labels.get(key, key) }}</label>
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
</body>
</html>
"""

REBOOT_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Rebooting...</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link 
    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" 
    rel="stylesheet"
  >
  <style>
    .spinner {
      width: 3rem;
      height: 3rem;
    }
  </style>
</head>
<body class="bg-light">
  <div class="container py-5 text-center">
    <div class="alert alert-warning" role="alert">
      <h4 class="alert-heading mb-3">Rebooting...</h4>
      <div class="d-flex justify-content-center align-items-center mb-3">
        <div class="spinner-border spinner" role="status" aria-hidden="true"></div>
      </div>
      <p>The Snap device is rebooting. This page will automatically return once it's back online.</p>
      <a href="/" class="btn btn-secondary mt-3">Return manually</a>
    </div>
  </div>

  <script>
    function checkServer() {
      fetch("/", { method: "HEAD" })
        .then(() => {
          window.location.href = "/";
        })
        .catch(() => {
          setTimeout(checkServer, 5000); // retry every 5 seconds
        });
    }

    setTimeout(checkServer, 10000); // wait 10 seconds before first check
  </script>
</body>
</html>
"""

# --- Main ---

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
