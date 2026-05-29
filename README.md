# 🚀 GPU Extreme Dashboard & Cockpit

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)
![Platform](https://img.shields.io/badge/platform-AMD%20ROCm-red.svg)
![Integration](https://img.shields.io/badge/integration-Open--WebUI-orange.svg)

**GPU Extreme Dashboard** is a high-performance monitoring suite that transforms hardware telemetry into a visual experience. It is divided into two specialized modules: a **Visual Cockpit** for streamers (OBS) and a **Seamless Telemetry Integration** for Open-WebUI.

---

## 💎 Two Worlds

### 1. 🎨 Visual Cockpit (for OBS & Browsers)
A visually intense monitoring widget designed for streamers and enthusiasts. It utilizes dynamic CSS animations that react physically to your hardware load.
* **🔥 Extreme Visual Feedback:**
    * **VRAM Bloat & Pop:** The VRAM box expands during high load (Comic-style pop-and-shrink).
    * **Meltdown Mode:** At critical temperatures, the interface enters a red-tinted "shake" mode.
    * **Lightning Bursts:** Power spikes trigger visual lightning effects.
    * **Heat Effects:** Rising temperatures change the color intensity (Fire-effect).
* **⚡ Real-Time Updates:** Uses *Server-Sent Events (SSE)* for minimal latency and high performance.
* **🎮 Simulation Mode:** Integrated test mode to preview animations without actual GPU load.

### 2. 🧠 AI-OS Telemetry (for Open-WebUI)
Transform your LLM interface into a true Operating System. The WebUI function integrates GPU metrics directly into your chat workflow.
* **📟 Status Integration:** GPU temperature, power, load, and VRAM are displayed as elegant status messages directly above the chat input.
* **⚙️ Valve Configuration:** Server URL and update settings can be managed directly via the Open-WebUI interface.
* **🚀 Plug & Play:** Quick installation via JSON import.

---

## 📂 Project Structure

* `gpu-extreme-dashboard.py` – The core backend (Flask) providing the Visual Cockpit and the Telemetry API.
* `gpu-extreme-webui.py` – The Python function specifically for Open-WebUI integration.
* `gpu-extreme-webui.json` – The ready-to-use configuration file for instant import into Open-WebUI.

---

## 🛠️ Installation

### Prerequisites
* **Python 3.8+**
* **AMD GPU** with installed ROCm drivers (uses `rocm-smi` for data collection).
* **Flask** & **Flask-CORS** (required for WebUI communication).

### Setup
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/eisenfunk/gpu-extreme-dashboard.git
   cd gpu-extreme-dashboard
   ```
2. **Install Dependencies:**
   ```bash
   pip install flask flask-cors
   ```
3. **Start the Dashboard:**
    ```bash
    python gpu-extreme-dashboard.py
    ```
    The dashboard will be listening on `0.0.0.0:8090` by default. You can access it via `http://localhost:8090` or your local IP address.

    ### Command Line Arguments

    The dashboard supports the following command line arguments:

    | Argument | Default | Description |
    | :--- | :--- | :--- |
    | `--host` | `0.0.0.0` | Host address to bind to |
    | `--port` | `8090` | Port to listen on |

    **Examples:**
    ```bash
    # Start with custom port
    python gpu-extreme-dashboard.py --port 9000

    # Start with custom host and port
    python gpu-extreme-dashboard.py --host 127.0.0.1 --port 9000

    # Start with default settings
    python gpu-extreme-dashboard.py
    ```

---

## ⚙️ Configuration

### For the Visual Cockpit (URL Parameters)
Control the widget behavior directly via URL parameters in your browser or OBS:
| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `col` | Integer | `2` | Number of columns in the grid (1, 2, or 4). |
| `interval` | Float | `2` | Update interval in seconds. |
| `test` | Boolean | `false` | Enables Simulation Mode (ideal for testing animations). |
| `width` | Integer | `520` | Total width of the widget in pixels. |

**Example for a 4-column layout in test mode:**
`http://localhost:8090/?col=4&test=true&interval=1`

### For Open-WebUI (Valves)
1. Navigate to **Workspace** -> **Functions** in Open-WebUI.
2. Click **Import** and select `gpu-extreme-webui.json`.
3. Open the function settings (gear icon) to configure the `server_url`. 
   *(Note: If running in Docker, use `http://host.docker.internal:8090/stats-quick`)*.

---

## 🖥️ OBS Integration
1. Open OBS.
2. Add a new source: **Browser**.
3. Enter the URL: `http://localhost:8090/?col=4&interval=2` (or your custom configuration).
4. Set the width and height according to your layout.
5. **Done!** Your cockpit is live.

---

## ⚠️ Disclaimer
This tool reads hardware data via system commands. Use it at your own risk. Animations are purely decorative and do not affect hardware performance or cooling.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
_Developed with ❤️ for GPU Enthusiasts._
