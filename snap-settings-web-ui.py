from flask import Flask, request, render_template_string, redirect
import json
import subprocess

# make sure to allow reboot
# sudo visudo
# pi ALL=(ALL) NOPASSWD: /sbin/reboot

app = Flask(__name__)
SETTINGS_FILE = "snap-settings.json"

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
        # Update settings from form input
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


        # Save updated settings
        save_settings(settings)

        # Check if reboot was requested
        if request.form.get("action") == "reboot":
            subprocess.Popen(["sudo", "reboot"])
            return "Rebooting...<br><br><a href='/'>Go to Snap Control Panel</a>"

        return redirect("/")

    return render_template_string(TEMPLATE, settings=settings)

# --- HTML Template ---

TEMPLATE = """
<!doctype html>
<head>
<title>Snap Settings</title>
<style>
body {
    font-family: helvetica, arial, sans-serif;
}
</style>
</head>
<h1>Snap Control Panel</h1>
<form method="post">
  {% for key, value in settings.items() %}
    {% if value is mapping %}
      <fieldset>
        <legend>{{ key }}</legend>
        {% for subkey, subvalue in value.items() %}
          <label>{{ subkey }}:
            <input type="text" name="{{ key }}.{{ subkey }}" value="{{ subvalue }}">
          </label><br>
        {% endfor %}
      </fieldset>
    {% elif value is boolean %}
      <label>
        <input type="checkbox" name="{{ key }}" {% if value %}checked{% endif %}>
        {{ key }}
      </label><br>
    {% else %}
      <label>{{ key }}:
        <input type="text" name="{{ key }}" value="{{ value }}">
      </label><br>
    {% endif %}
  {% endfor %}
  <button type="submit" name="action" value="save">Save</button>
  <button type="submit" name="action" value="reboot" onclick="return confirm('Are you sure you want to reboot Snap?');">Save and Reboot</button>
</form>
"""

# --- Main ---

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
