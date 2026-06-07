import subprocess
import json
import time
import sys
import argparse
import psutil
from flask_cors import CORS
from flask import Flask, Response, render_template_string, request, send_from_directory

use_rocm = True

app = Flask(__name__)
CORS(app)

# Serve static JS and CSS files
@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('js', filename, mimetype='text/javascript')

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory('css', filename, mimetype='text/css')

# --- DASHBOARD HTML (CSS moved to external file, JS moved to external files) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GPU Extreme Cockpit Widget</title>
    <link rel="stylesheet" href="/css/dashboard.css?{{ col }}{{ widget_size }}{{ width }}">
</head>
<body>
    {% if show_form %}
    <div id="config-form-container">
        <form action="/" method="get">
            <div class="form-group">
                <label>Cols:</label>
                <select name="col">
                    <option value="1" {% if col == 1 %}selected{% endif %}>1</option>
                    <option value="2" {% if col == 2 %}selected{% endif %}>2</option>
                    <option value="4" {% if col == 4 %}selected{% endif %}>4</option>
                </select>
            </div>
            <div class="form-group">
                <label>Widget Size:</label>
                <input type="text" name="widget_size" value="{{ widget_size }}" style="width: 80px;">
            </div>
            <div class="form-group">
                <label>Test:</label>
                <select name="test">
                    <option value="false" {% if test == 'false' %}selected{% endif %}>Off</option>
                    <option value="true" {% if test == 'true' %}selected{% endif %}>On</option>
                </select>
            </div>
            <div class="form-group">
                <label>Int (s):</label>
                <input type="number" name="interval" value="{{ interval }}" style="width: 40px;">
            </div>
            <input type="hidden" name="form" value="true">
            <button type="submit">Apply</button>
        </form>
    </div>
    {% endif %}
    <div id="gpu-extreme-cockpit-v4" style="--cockpit-width: {{ widget_size }}; --form-width: {{ width }}px; --grid-cols: repeat({{ col }}, 1fr);">
        <div class="grid">
            <div class="card" id="card-temp">
                <div class="card-content">
                    <span class="label">Temp</span>
                    <span class="val" id="v-temp">--</span>
                    <div class="bar-bg"><div id="b-temp" class="bar-fill c-temp"></div></div>
                </div>
            </div>
            <div class="card" id="card-power">
                <div class="card-content">
                    <span class="label">Power</span>
                    <span class="val" id="v-power">--</span>
                    <div class="bar-bg"><div id="b-power" class="bar-fill"></div></div>
                </div>
            </div>
            <div class="card" id="card-gpu">
                <div class="card-content">
                    <span class="label">GPU</span>
                    <span class="val" id="v-gpu">--</span>
                    <div class="bar-bg"><div id="b-gpu" class="bar-fill c-gpu"></div></div>
                </div>
            </div>
            <div class="card" id="card-vram">
                <div class="card-content">
                    <span class="label">VRAM</span>
                    <span class="val" id="v-vram">--</span>
                    <div class="bar-bg"><div id="b-vram" class="bar-fill c-vram"></div></div>
                </div>
            </div>

            <div class="card" id="card-cpu">
                <div class="card-content">
                    <span class="label">CPU</span>
                    <span class="val" id="v-cpu">--</span>
                    <div id="cpu-cores-container" class="cpu-cores-container">
                        <!-- CPU Cores werden hier dynamisch eingefügt -->
                    </div>
                </div>
            </div>
        </div>
        <div style="text-align:center; margin-top:20px; font-size:0.6rem; color:#444;" id="status-text">Connecting...</div>
    </div>

    <script type="module">
        import { SweatDropletEffect } from '/js/effects/SweatDropletEffect.js';
        import { FireEffect } from '/js/effects/FireEffect.js';
        import { TemperatureStoveEffect } from '/js/effects/TemperatureStoveEffect.js';
        import { PowerFlashEffect } from '/js/effects/PowerFlashEffect.js';
        import { GpuUsageEffect } from '/js/effects/GpuUsageEffect.js';
        import { VramBloatEffect } from '/js/effects/VramBloatEffect.js';
        import { DashboardManager } from '/js/DashboardManager.js';

        const urlParams = new URLSearchParams(window.location.search);
        const sweatAnimIntervalMs = 50;
        const bloatAnimIntervalMs = 20;
        const bloatSequenceLength = 2000;
        const bloatThreshold = 60;
        const powerThresholdMin = 55;
        const powerThresholdMax = 80;
        const fireThresholdLow = 40;
        const fireThresholdHigh = 80;

        // Initialize all effects
        const fireEffect = new FireEffect('card-temp');
        const temperatureStoveEffect = new TemperatureStoveEffect(fireThresholdLow, fireThresholdHigh, 'card-temp', 'v-temp', 'b-temp');
        temperatureStoveEffect.setFireEffect(fireEffect);
        const powerFlashEffect = new PowerFlashEffect(powerThresholdMin, powerThresholdMax, 'card-power', 'v-power', 'b-power');
        const gpuUsageEffect = new GpuUsageEffect('card-gpu', 'v-gpu', 'b-gpu');
        const vramBloatEffect = new VramBloatEffect(bloatAnimIntervalMs, bloatSequenceLength, bloatThreshold, 'card-vram', 'v-vram', 'b-vram');
        const sweatDropletEffect = new SweatDropletEffect(sweatAnimIntervalMs,'card-gpu');

        // Initialize Dashboard Manager
        const dashboard = new DashboardManager(
            temperatureStoveEffect,
            powerFlashEffect,
            gpuUsageEffect,
            vramBloatEffect,
            sweatDropletEffect
        );
    </script>
</body>
</html>
"""

# --- BACKEND LOGIC ---
def get_cpu_data() -> dict:
    """Ermittelt CPU-Statistiken inkl. Anzahl Kerne und Threads"""
    try:
        # Anzahl der logischen Kerne
        num_cores = psutil.cpu_count(logical=True)
        
        # Anzahl der physischen Kerne
        num_physical_cores = psutil.cpu_count(logical=False)
        
        # CPU-Auslastung insgesamt
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # CPU-Auslastung pro Kern (nur bei mehr als einem Kern)
        if num_cores > 1:
            cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
        else:
            cpu_per_core = [cpu_percent]
        
        # Anzahl der Threads pro Kern (berechnet aus logischen und physischen Kernen)
        num_threads_per_core = num_cores // num_physical_cores if num_physical_cores > 0 else 1
        
        # Struktur für die Rückgabe
        data = {
            "num_cores": num_cores,
            "num_physical_cores": num_physical_cores,
            "num_threads_per_core": num_threads_per_core,
            "cpu_percent": cpu_percent,
            "cpu_per_core": cpu_per_core
        }
        return data
    except Exception as e:
        return {
            "error": f"Fehler bei der CPU-Statistik-Erhebung: {e}"
        }

def get_real_gpu_data() -> dict:
    global use_rocm

    if use_rocm:
        try:
            cmd = "rocm-smi --showmemuse --showpower --showtemp --showuse --json"
            result = subprocess.check_output(cmd, shell=True, text=True)
            data = json.loads(result)
            startup = False
            return data
        except Exception as e:
            use_rocm = False
            print(f"[WARN] rocm-smi konnte nicht gestartet werden: {e}", file=sys.stderr)

    try:
        cmd = (
            "nvidia-smi "
            "--query-gpu=temperature.gpu,power.draw,utilization.gpu,"
            "memory.used,memory.total "
            "--format=csv,noheader,nounits"
        )
        out = subprocess.check_output(cmd, shell=True, text=True).strip()

        # CSV‑String → einzelne Werte (keine Einrückung, alles durch Komma getrennt)
        temp, power, util, mem_used, mem_total = [float(v) for v in out.split(',')]
        
        # Prozentualen Speicherverbrauch berechnen (auf ganze Zahl runden)
        mem_percent = int(round((mem_used / mem_total) * 100)) if mem_total > 0 else 0

        # Das gleiche JSON‑Schema wie bei rocm-smi
        data = {
            "card0": {
                "Temperature (Sensor edge) (C)": f"{temp:.1f}",
                "Current Socket Graphics Package Power (W)": f"{power:.3f}",
                "GPU use (%)": f"{util:.0f}",
                "GPU Memory Allocated (VRAM%)": f"{mem_percent}",
                "Memory Activity": "N/A"            # rocm‑smi liefert dort "N/A"
            }
        }
        return data

    except Exception as e:
        return {
            "error": f"Kein GPU‑Monitoring‑Tool verfügbar: {e}"
        }

def get_simulated_data(start_time):
    elapsed = time.time() - start_time
    cycle_time = 15.0
    time_in_cycle = elapsed % cycle_time
    progress = (time_in_cycle / 7.5) if time_in_cycle < 7.5 else (1.0 - ((time_in_cycle - 7.5) / 7.5))
    return {
        "card0": {
            "Temperature (Sensor edge) (C)": str(30 + (progress * 55)),
            "Current Socket Graphics Package Power (W)": str(10 + (progress * 80)),
            "GPU use (%)": str(progress * 100),
            "GPU Memory Allocated (VRAM%)": str(50 + (progress * 45))
        }
    }

@app.route('/')
def index():
    col = int(request.args.get('col', 2))
    show_form = request.args.get('form', 'false').lower() == 'true'
    width = int(request.args.get('width', 520))
    test = request.args.get('test', 'false')
    interval = int(request.args.get('interval', 2))
    widget_size = request.args.get('widget_size')
    if not widget_size:
        widget_size = f"{width}px"
    return render_template_string(
        HTML_TEMPLATE,
        col=col,
        width=width,
        show_form=show_form,
        test=test,
        interval=interval,
        widget_size=widget_size
    )

@app.route('/stream')
def stream():
    is_test = request.args.get('test') == 'true'
    interval = int(request.args.get('interval', 2))
    def event_stream():
        sim_start_time = time.time()
        while True:
            gpu_data = get_simulated_data(sim_start_time) if is_test else get_real_gpu_data()
            cpu_data = get_cpu_data()
            
            # Kombiniere GPU- und CPU-Daten
            combined_data = {
                "gpu": gpu_data,
                "cpu": cpu_data
            }
            
            yield f"data: {json.dumps(combined_data)}\n\n"
            time.sleep(interval)
    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/stats-quick')
def stats_quick():
    """Ein einfacher Endpunkt für die WebUI-Funktion (ohne SSE-Overhead)"""
    try:
        # Wir nutzen deine bestehende Logik
        gpu_data = get_real_gpu_data()
        cpu_data = get_cpu_data()
        
        # Kombiniere GPU- und CPU-Daten
        combined_data = {
            "gpu": gpu_data,
            "cpu": cpu_data
        }
        
        # Falls es einen Fehler gibt, liefern wir ein leeres Dict
        if "error" in gpu_data or "error" in cpu_data:
            return {"error": "No data"}, 500
        return combined_data
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='GPU Extreme Dashboard')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8090, help='Port to listen on (default: 8090)')
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, threaded=True)
