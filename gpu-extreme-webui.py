import requests
import json
from typing import Optional, Dict, Any

class Filter:
    class Type(str):
        FILTER = "filter"

    class Valves(dict):
        # Diese Variablen erscheinen als Einstellung in Open WebUI
        server_url: str = "http://localhost:8090/stats-quick"
        update_on_inlet: bool = True

    def __init__(self):
        self.valves = self.Valves()

    async def inlet(self, body: Dict[str, Any], __event_emitter__: Any = None) -> Dict[str, Any]:
        """
        Wird beim Senden einer Nachricht aufgerufen.
        """
        if __event_emitter__ is not None and self.valves.update_on_inlet:
            try:
                # 1. Daten von der konfigurierbaren URL abrufen
                response = requests.get(self.valves.server_url, timeout=3)
                
                if response.status_code == 200:
                    data = response.json()
                    gpu = data.get("card0", {})
                    
                    if gpu:
                        # 2. Werte extrahieren (inklusive Power!)
                        temp = gpu.get("Temperature (Sensor edge) (C)", "??")
                        pwr = gpu.get("Current Socket Graphics Package Power (W)", "??")
                        load = gpu.get("GPU use (%)", "??")
                        vram = gpu.get("GPU Memory Allocated (VRAM%)", "??")
                        
                        # 3. Schön formatierten Status-String bauen
                        # Format: 🌡️ 55°C | ⚡ 120W | 🚀 20% | 💾 4GB
                        status_msg = f"🌡️ {temp}°C | ⚡ {pwr}W | 🚀 {load}% | 💾 {vram}%"
                        
                        await __event_emitter__({
                            "type": "status",
                            "data": {
                                "description": status_msg,
                                "status": "done"
                            }
                        })
                    else:
                        raise ValueError("Keine GPU-Daten in der Antwort gefunden.")
                else:
                    raise Exception(f"Server-Error: Status {response.status_code}")

            except Exception as e:
                # Fehler dezent anzeigen
                await __event_emitter__({
                    "type": "status",
                    "data": {
                        "description": f"⚠️ GPU-Dashboard Error: {str(e)}",
                        "status": "error"
                    }
                })

        return body

    async def outlet(self, body: Dict[str, Any], __event_emitter__: Any = None) -> Dict[str, Any]:
        return body
