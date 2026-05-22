import subprocess
import json
import time
from flask_cors import CORS
from flask import Flask, Response, render_template_string, request

app = Flask(__name__)
CORS(app)

# --- DASHBOARD HTML & CSS ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GPU Extreme Cockpit Widget</title>
    <style>
        body {
            background: transparent;
            color: #eee;
            font-family: 'Segoe UI', sans-serif;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            overflow: hidden;
        }
        #gpu-extreme-cockpit-v4 {
            background: #050505;
            color: #eee;
            padding: 25px;
            border-radius: 20px;
            width: {{ widget_size }};
            transition: width 0.3s ease;
            box-sizing: border-box;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat({{ col }}, 1fr);
            gap: 15px;
        }
        .card {
            background: hsl(0, 0%, calc(10% + var(--bg-lightness, 0%)));
            padding: 15px;
            border-radius: var(--br, 12px);
            position: relative;
            border: 1px solid #333;
            transition: background-color 0.15s, box-shadow 0.15s, transform 0.3s ease-out, border-radius 0.3s ease-out, border-color 0.2s;
            overflow: hidden;
        }
        .card-content {
            position: relative;
            z-index: 2;
            /* Hier nutzen wir die CSS Variablen für die Skalierung */
            transform: scale(var(--app-bx, 1), var(--app-by, 1)) rotate(var(--rot, 0deg)) translate(var(--tx, 0px), var(--ty, 0px));
            transition: none !important;
        }
        .label { font-size: 0.65rem; color: #666; text-transform: uppercase; display: block; margin-bottom: 5px; }
        .val { font-size: 1.4rem; font-weight: bold; display: block; margin-bottom: 10px; }
        .bar-bg { background: #222; height: 8px; border-radius: 4px; width: 100%; overflow: visible; position: relative; }
        .bar-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.1s linear, background-color 0.3s ease;
        }
        #b-power {
            --glow-blur: 0px;
            --glow-opacity: 0;
            --glow-color: rgba(0, 212, 255, 1);
            box-shadow: 0 0 var(--glow-blur) var(--glow-color);
            transition: background-color 0.3s ease, box-shadow 0.2s ease-out, filter 0.2s ease-out, transform 0.1s ease-out;
        }
        .state-lightning #b-power {
            background-color: #ffffff !important;
            box-shadow: 0 0 25px 10px rgba(255, 255, 255, 0.9),
                        0 0 40px 15px rgba(0, 212, 255, 0.7) !important;
            filter: brightness(3) !important;
        }
        #config-form-container {
            background: #1a1a1a; padding: 15px; border-radius: 12px; margin-bottom: 20px;
            border: 1px solid #444; width: {{ width }}px; box-sizing: border-box;
        }
        .form-group { display: inline-block; margin-right: 10px; font-size: 0.8rem; }
        input, select { background: #333; border: 1px solid #555; color: white; padding: 5px; border-radius: 4px; }
        button { background: #00d4ff; border: none; padding: 5px 15px; border-radius: 4px; cursor: pointer; font-weight: bold; }
        
        @keyframes meltdown-shake { 0%, 100% { transform: translate(0,0); } 25% { transform: translate(4px, -4px); } 50% { transform: translate(-4px, 4px); } 75% { transform: translate(4px, 4px); } }
        .state-meltdown { animation: meltdown-shake 0.05s infinite !important; background-color: #4a0000; box-shadow: 0 0 30px #ff0000 !important; border-color: #ff0000 !important; }
        @keyframes lightning-burst { 0% { background-color: #1a1a1a; } 50% { background-color: #ffffff; } 100% { background-color: #1a1a1a; } }
        .state-lightning { animation: lightning-burst 0.12s ease-out !important; }
        .droplet { position: absolute; background: rgba(255, 255, 255, 0.5); width: 4px; height: 12px; border-radius: 50%; top: -15px; pointer-events: none; z-index: 5; animation: drip 0.8s linear forwards; }
        @keyframes drip { to { transform: translateY(160px); opacity: 0; } }
        .c-temp { background: #00d4ff; }
        .c-gpu { background: #9c27b0; }
        .c-vram { background: #e91e63; }
    </style>
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
            </div >
            <div class="form-group">
                <label>Widget Size:</label>
                <input type="text" name="widget_size" value="{{ widget_size }}" style="width: 80px;">
            </div >
            <div class="form-group">
                <label>Test:</label>
                <select name="test">
                    <option value="false" {% if test == 'false' %}selected{% endif %}>Off</option>
                    <option value="true" {% if test == 'true' %}selected{% endif %}>On</option>
                </select>
            </div >
            <div class="form-group">
                <label>Int (s):</label>
                <input type="number" name="interval" value="{{ interval }}" style="width: 40px;">
            </div >
            <input type="hidden" name="form" value="true">
            <button type="submit">Apply</button>
        </form>
    </div >
    {% endif %}
    <div id="gpu-extreme-cockpit-v4">
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
        </div>
        <div style="text-align:center; margin-top:20px; font-size:0.6rem; color:#444;" id="status-text">Connecting...</div>
    </div>

    <script>
        let currentDropsPerSecond = 0;
        let powerFlashTimeout = null;
        let vramShakeInterval = null;
        
        const urlParams = new URLSearchParams(window.location.search);
        const animIntervalMs = (parseFloat(urlParams.get('interval')) || 2) * 1000;

        // VRAM State Management
        let vramState = {
            intensity: 0,
            baseBx: 1, // Die langsame Bloat-Skalierung
            baseBy: 1,
            startTime: 0
        };

        class FireEffect {
            constructor(elementId) {
                this.el = document.getElementById(elementId);
                this.intensity = 0;
                this.isFlashing = false;
                this.COLOR_0 = { r: 255, g: 50, b: 0 };
                this.COLOR_100 = { r: 100, g: 0, b: 140 };
                this._updateBaseColor();
                this._triggerGasFlash();
            }
            setIntensity(tIntensity) { this.intensity = Math.max(0, Math.min(1, tIntensity)); }
            _lerp(start, end, t) { return start * (1 - t) + end * t; }
            _getGlobalBrightness(t) {
                if (t <= 0.8) { const phase = (t / 0.8) * (Math.PI / 2); return Math.sin(phase); }
                return 1.0;
            }
            _updateBaseColor() {
                if (this.isFlashing) { setTimeout(() => this._updateBaseColor(), 5); return; }
                const t = this.intensity;
                const globalLuminance = this._getGlobalBrightness(t);
                let r = this._lerp(this.COLOR_0.r, this.COLOR_100.r, t);
                let g = this._lerp(this.COLOR_0.g, this.COLOR_100.g, t);
                let b = this._lerp(this.COLOR_0.b, this.COLOR_100.b, t);
                const chaos = this._lerp(30, 60, t);
                r += (Math.random() - 0.5) * chaos;
                g += (Math.random() - 0.5) * chaos;
                b += (Math.random() - 0.5) * chaos;
                r *= globalLuminance; g *= globalLuminance; b *= globalLuminance;
                this.el.style.backgroundColor = `rgb(${Math.round(Math.max(0, Math.min(255, r)))}, ${Math.round(Math.max(0, Math.min(255, g)))}, ${Math.round(Math.max(0, Math.min(255, b)))})`;
                const nextTick = Math.random() * (this._lerp(170, 20, t) - this._lerp(80, 5, t)) + this._lerp(80, 5, t);
                setTimeout(() => this._updateBaseColor(), nextTick);
            }
            _triggerGasFlash() {
                const t = this.intensity;
                const flashChance = this._lerp(0.3, 0.05, t);
                if (Math.random() < flashChance) {
                    this.isFlashing = true;
                    const flashDuration = this._lerp(80, 5, t);
                    const localFlashBrightness = this._lerp(1.0, 0.5, t);
                    let rBase = this._lerp(255, 220, t);
                    let gBase = this._lerp(255, 100, t);
                    let bBase = this._lerp(200, 20, t);
                    const drift = (Math.random() - 0.5) * 60;
                    const lightningScale = Math.sqrt(this._getGlobalBrightness(t));
                    let r = (rBase + drift) * localFlashBrightness * lightningScale;
                    let g = (gBase + drift) * localFlashBrightness * lightningScale;
                    let b = (bBase + drift) * localFlashBrightness * lightningScale;
                    this.el.style.backgroundColor = `rgb(${Math.round(Math.max(0, Math.min(255, r)))}, ${Math.round(Math.max(0, Math.min(255, g)))}, ${Math.round(Math.max(0, Math.min(255, b)))})`;
                    setTimeout(() => { this.isFlashing = false; }, flashDuration);
                }
                setTimeout(() => this._triggerGasFlash(), this._lerp(200, 10, t));
            }
        }

        function createSweat(cardId) {
            const card = document.getElementById(cardId);
            if (!card) return;
            const drop = document.createElement('div');
            drop.className = 'droplet';
            drop.style.left = Math.random() * 90 + '%';
            drop.style.animationDelay = (Math.random() * 0.2) + 's';
            card.appendChild(drop);
            setTimeout(() => drop.remove(), 1000);
        }

        function managePowerFlash(pVal) {
            const threshold = 50;
            const baseLine = 55;
            const maxLine = 85;
            const card = document.getElementById('card-power');
            const bPower = document.getElementById('b-power');
            const vPower = document.getElementById('v-power');
            let pIntensity = Math.max(0, Math.min((pVal - baseLine) / (maxLine - baseLine), 1));
            const saturation = 100 * (1 - pIntensity);
            const lightness = 50 + (50 * pIntensity);
            vPower.innerText = pVal.toFixed(1) + "W";
            bPower.style.width = Math.min((pVal / 90 * 100), 100) + "%";
            bPower.style.backgroundColor = `hsl(200, ${saturation}%, ${lightness}%)`;
            bPower.style.setProperty('--glow-blur', (pIntensity * 15) + 'px');
            bPower.style.setProperty('--glow-opacity', pIntensity);
            bPower.style.setProperty('--glow-color', `rgba(0, 212, 255, ${pIntensity})`);
            if (pVal < threshold) {
                card.classList.remove('state-lightning');
                card.style.transform = 'rotate(0deg)';
                if (powerFlashTimeout) { clearTimeout(powerFlashTimeout); powerFlashTimeout = null; }
                return;
            }
            if (powerFlashTimeout) return;
            const runFlashCycle = () => {
                const randomAngle = (Math.random() * 20 - 10);
                card.classList.remove('state-lightning');
                void card.offsetWidth;
                card.classList.add('state-lightning');
                card.style.transform = `rotate(${randomAngle}deg)`;
                setTimeout(() => { card.style.transform = 'rotate(0deg)'; card.classList.remove('state-lightning'); }, 150);
                const minGap = 110 * (1 - pIntensity) + 40;
                const maxGap = (2000 - 1000 * pIntensity) * (1 - pIntensity) + 50;
                powerFlashTimeout = setTimeout(runFlashCycle, Math.random() * (maxGap - minGap) + minGap);
            };
            runFlashCycle();
        }

        function manageTemperaturStove(tVal) {
            const minTemp = 40;
            const maxTemp = 80;
            let tIntensity = Math.min(Math.max((tVal - minTemp) / (maxTemp - minTemp), 0), 1);
            tempCard.setIntensity(tIntensity);
            document.getElementById('v-temp').innerText = tVal.toFixed(1) + "°C";
            document.getElementById('b-temp').style.width = Math.min(tVal, 100) + "%";
            const hue = 200 - ((tVal - 30) * (200 / 65));
            document.getElementById('b-temp').style.backgroundColor = `hsl(${hue}, 100%, 50%)`;
            const cTempCard = document.getElementById('card-temp');
            if (tVal > maxTemp) cTempCard.classList.add('state-meltdown'); else cTempCard.classList.remove('state-meltdown');
        }

        function manageGPUUsage(gVal) {
            document.getElementById('v-gpu').innerText = gVal.toFixed(0) + "%";
            document.getElementById('b-gpu').style.width = Math.min(gVal, 100) + "%";
            currentDropsPerSecond = gVal >= 70 ? 2 + (((gVal - 70) / 30) * 28) : 0;
        }   

        function manageVRAMBloat(vVal) {
            document.getElementById('v-vram').innerText = vVal.toFixed(0) + "%";
            document.getElementById('b-vram').style.width = Math.min(vVal, 100) + "%";
            const cVramCard = document.getElementById('card-vram');
            const cVramContent = cVramCard.querySelector('.card-content');
            
            if (vVal > 70) {
                const intensity = (vVal - 70) / 30;
                vramState.intensity = intensity;
                
                // 1. Die "Base" Skalierung (das langsame Bloaten)
                const bloomFactor = Math.sqrt(intensity);
                vramState.baseBx = 1 + (0.2 * bloomFactor);
                vramState.baseBy = 1 + (0.8 * bloomFactor);

                // 2. Gegenmaßnahme für den Inhalt: 
                // WICHTIG: Wir skalieren den Inhalt NUR gegen den Base-Wert.
                // Dadurch bleibt die Schrift stabil, auch wenn die Box poppt/schrumpft.
                const contentBx = 1 / vramState.baseBx;
                const contentBy = 1 / vramState.baseBy;
                cVramContent.style.setProperty('--app-bx', contentBx);
                cVramContent.style.setProperty('--app-by', contentBy);

                // Radius & Background (basierend auf Base-Bloat)
                const brPercent = 8 + (intensity * 42);
                cVramCard.style.setProperty('--br', brPercent + '%');
                cVramCard.style.setProperty('--bg-lightness', (intensity * 15) + "%");
                cVramCard.classList.add('state-pressure');

                if (!vramShakeInterval) {
                    vramState.startTime = Date.now();
                    vramShakeInterval = setInterval(() => {
                        const now = Date.now();
                        let elapsed = now - vramState.startTime;

                        if (elapsed >= animIntervalMs) {
                            vramState.startTime = now;
                            elapsed = 0;
                        }

                        const ratio = elapsed / animIntervalMs;
                        let curBx, curBy;

                        // --- PHASE LOGIC (Comic Style) ---
                        if (ratio < 0.8) {
                            // 1. Normal Bloat
                            curBx = vramState.baseBx;
                            curBy = vramState.baseBy;
                        } else if (ratio < 0.9) {
                            // 2. POP (+20%)
                            curBx = vramState.baseBx * 1.2;
                            curBy = vramState.baseBy * 1.2;
                        } else if (ratio < 0.95) {
                            // 3. SHRINK (auf 0% Intensität -> Scale 1.0)
                            curBx = 1.0;
                            curBy = 1.0;
                        } else {
                            // 4. OVERSHOOT (auf -10% Intensität -> Scale 0.9)
                            curBx = 0.9;
                            curBy = 0.9;
                        }

                        // --- JITTER (Nur in der Normal-Phase für knackiges Gefühl) ---
                        const shakePower = vramState.intensity * vramState.intensity;
                        const isJittering = (ratio < 0.8);
                        const jitterScale = isJittering ? (1 - (shakePower * 0.08 * Math.sin(now / 40))) : 1;
                        
                        const finalBx = curBx * jitterScale;
                        const finalBy = curBy * jitterScale;

                        // Rattle Werte
                        const rot = (Math.random() * 4 - 2) * shakePower * (isJittering ? 1 : 0.2);
                        const tx = (Math.random() * 4 - 2) * shakePower * (isJittering ? 1 : 0.2);
                        const ty = (Math.random() * 4 - 2) * shakePower * (isJittering ? 1 : 0.2);

                        // Apply to Card
                        cVramCard.style.transform = `scale(${finalBx}, ${finalBy})`;

                        // Apply to Content (Rotation/Translation)
                        cVramContent.style.setProperty('--rot', rot + 'deg');
                        cVramContent.style.setProperty('--tx', tx + 'px');
                        cVramContent.style.setProperty('--ty', ty + 'px');

                    }, 50);
                }
            } else {
                // RESET
                vramState.intensity = 0;
                vramState.baseBx = 1;
                vramState.baseBy = 1;
                cVramCard.classList.remove('state-pressure');
                cVramCard.style.transform = 'scale(1, 1)';
                cVramCard.style.setProperty('--br', '12px');
                cVramCard.style.setProperty('--bg-lightness', '0%');
                if (vramShakeInterval) {
                    clearInterval(vramShakeInterval);
                    vramShakeInterval = null;
                }
                cVramContent.style.setProperty('--app-bx', '1');
                cVramContent.style.setProperty('--app-by', '1');
                cVramContent.style.setProperty('--rot', '0deg');
                cVramContent.style.setProperty('--tx', '0px');
                cVramContent.style.setProperty('--ty', '0px');
            }
        }

        function updateDashboard(data) {
            if (data.error) {
                document.getElementById('status-text').innerText = "Error: " + data.error;
                return;
            }
            const c0 = data.card0;
            manageTemperaturStove(parseFloat(c0["Temperature (Sensor edge) (C)"]));
            managePowerFlash(parseFloat(c0["Current Socket Graphics Package Power (W)"]));
            manageGPUUsage(parseFloat(c0["GPU use (%)"]));
            manageVRAMBloat(parseFloat(c0["GPU Memory Allocated (VRAM%)"]));
        }

        const tempCard = new FireEffect('card-temp');
        setInterval(() => {
            if (currentDropsPerSecond > 0) {
                const intervalMs = 50;
                const dropsToSpawnThisTick = (currentDropsPerSecond / 1000) * intervalMs;
                for (let i = 0; i < Math.floor(dropsToSpawnThisTick); i++) { createSweat('card-gpu'); }
                if (Math.random() < (dropsToSpawnThisTick % 1)) { createSweat('card-gpu'); }
            }
        }, 50);

        const eventSource = new EventSource(`/stream?interval=${urlParams.get('interval') || 2}&test=${urlParams.get('test') || 'false'}`);
        eventSource.onmessage = (e) => updateDashboard(JSON.parse(e.data));
        eventSource.onerror = () => document.getElementById('status-text').innerText = "Connection lost...";
    </script>
</body>
</html>
"""

# --- BACKEND LOGIC ---
def get_real_gpu_data():
    try:
        cmd = "rocm-smi --showmemuse --showpower --showtemp --showuse --json"
        result = subprocess.check_output(cmd, shell=True)
        return json.loads(result)
    except Exception as e:
        return {"error": str(e)}

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
            data = get_simulated_data(sim_start_time) if is_test else get_real_gpu_data()
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(interval)
    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/stats-quick')
def stats_quick():
    """Ein einfacher Endpunkt für die WebUI-Funktion (ohne SSE-Overhead)"""
    try:
        # Wir nutzen deine bestehende Logik
        data = get_real_gpu_data()
        # Falls es einen Fehler gibt, liefern wir ein leeres Dict
        if "error" in data:
            return {"error": "No data"}, 500
        return data
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090, threaded=True)
