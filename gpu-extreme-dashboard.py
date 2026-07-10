import subprocess
import json
import time
import sys
import os
import argparse
import psutil
from flask_cors import CORS
from flask import Flask, Response, render_template, request, send_from_directory

use_rocm = True
restart = True

app = Flask(__name__)
CORS(app)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('js', filename, mimetype='text/javascript')

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory('css', filename, mimetype='text/css')

def get_system_capacity_saturation():
    """
    Calculate the system capacity saturation based on CPU load metrics.
    
    The saturation represents the degree of system load relative to available
    CPU capacity, capped at 1.0 (100%).
    
    Returns:
        float: System capacity saturation between 0.0 and 1.0
        
    Formula:
        saturation = min(1.0, load_1min / physical_cores)
    """
    # Get the 1-minute load average
    load_avg = psutil.getloadavg()[0]
    
    # Get the number of physical CPU cores (not logical threads)
    physical_cores = psutil.cpu_count(logical=False)
    
    # Calculate saturation
    saturation = load_avg / physical_cores
    
    # Cap the saturation at 1.0 (100%)
    return min(1.0, saturation)

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
        
        # System capacity saturation calculation
        system_capacity_saturation = get_system_capacity_saturation()
        
        # Struktur für die Rückgabe
        data = {
            "num_cores": num_cores,
            "num_physical_cores": num_physical_cores,
            "num_threads_per_core": num_threads_per_core,
            "cpu_percent": cpu_percent,
            "cpu_per_core": cpu_per_core,
            "system_capacity_saturation": system_capacity_saturation
        }
        return data
    except Exception as e:
        return {
            "error": f"Fehler bei der CPU-Statistik-Erhebung: {e}"
        }

def _parse_amd_smi_process_vram() -> int | None:
    """
    Run `amd-smi process` and sum MEM_USAGE values across all processes.
    Returns VRAM usage as a percentage (0-100, integer) based on 128 GB total.
    Returns None if the command fails or parsing fails.
    """
    import re

    # Try multiple possible paths for amd-smi binary
    amd_smi_paths = ["/opt/rocm/bin/amd-smi", "amd-smi"]
    
    cmd = None
    for path in amd_smi_paths:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            cmd = [path, "process"]
            break
    
    if cmd is None:
        # Fallback to PATH lookup via shell=True
        cmd = ["amd-smi", "process"]

    try:
        result = subprocess.check_output(
            cmd, shell=False, text=True, stderr=subprocess.STDOUT
        )
    except Exception:
        return None

    total_bytes = 0.0
    for line in result.splitlines():
        match = re.search(r'MEM_USAGE:\s*([\d.]+)\s*(GB|MB|B)', line)
        if not match:
            continue
        try:
            value = float(match.group(1))
        except ValueError:
            continue
        unit = match.group(2).upper()
        if unit == "GB":
            total_bytes += value * (1024 ** 3)
        elif unit == "MB":
            total_bytes += value * (1024 ** 2)
        elif unit == "B":
            total_bytes += value

    TOTAL_VRAM_BYTES = 128 * (1024 ** 3)  # 128 GB in bytes
    percent = int((total_bytes / TOTAL_VRAM_BYTES) * 100) if TOTAL_VRAM_BYTES > 0 else 0
    return min(100, max(0, percent))


def get_real_gpu_data() -> dict:
    global use_rocm

    if use_rocm:
        try:
            # rocm-smi Aufruf bleibt unverändert, liefert u.a. "GPU Memory Allocated (VRAM%)": "99"
            cmd = "/opt/rocm/bin/rocm-smi --showmemuse --showpower --showtemp --showuse --json"
            result = subprocess.check_output(cmd, shell=True, text=True)
            data = json.loads(result)

            # amd-smi process zusätzlich ausführen für korrekten VRAM-Wert
            vram_percent = _parse_amd_smi_process_vram()
            if vram_percent is not None and "card0" in data:
                data["card0"]["GPU Memory Allocated (VRAM%)"] = str(vram_percent)

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
    # Füge einen Parameter hinzu, der anzeigt, dass das Skript neu gestartet wurde
    return render_template(
        'dashboard.html',
        col=col,
        width=width,
        show_form=show_form,
        test=test,
        interval=interval,
        widget_size=widget_size,
        restart=True
    )

@app.route('/stream')
def stream():
    is_test = request.args.get('test') == 'true'
    interval = int(request.args.get('interval', 2))
    def event_stream():
        global restart
        sim_start_time = time.time()
        while True:
            gpu_data = get_simulated_data(sim_start_time) if is_test else get_real_gpu_data()
            cpu_data = get_cpu_data()
            
            # Kombiniere GPU- und CPU-Daten
            combined_data = {
                "gpu": gpu_data,
                "cpu": cpu_data
            }
            
            # Prüfe auf reload-Flag im JSON
            global last_json_data
            if restart == True:
                # Wenn reload=True, sende ein spezielles Signal an den Browser
                reload_data = {
                    "reload": True,
                    "data": combined_data
                }
                yield f"data: {json.dumps(reload_data)}\n\n"
                restart = False
            else:
                yield f"data: {json.dumps(combined_data)}\n\n"
            
            last_json_data = combined_data
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
