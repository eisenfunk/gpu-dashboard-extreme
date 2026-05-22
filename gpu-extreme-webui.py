import requests
import json
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class Filter:
    class Type(str):
        FILTER = "filter"

    class Valves(BaseModel):
        server_url: str = Field(
            default="http://localhost:8090/stats-quick",
            description="URL to your GPU extreme dashboard"
        )
        update_on_inlet: bool = Field(
            default=True,
            description="Reload on each chat?"
        )

    def __init__(self):
        self.valves = self.Valves()

    async def inlet(self, body: Dict[str, Any], __event_emitter__: Any = None) -> Dict[str, Any]:
        if __event_emitter__ is not None and self.valves.update_on_inlet:
            try:
                response = requests.get(self.valves.server_url, timeout=3)
                
                if response.status_code == 200:
                    data = response.json()
                    gpu = data.get("card0", {})
                    
                    if gpu:
                        temp = f"{float(gpu.get('Temperature (Sensor edge) (C)', 0)):.0f}°C"
                        pwr = f"{float(gpu.get('Current Socket Graphics Package Power (W)', 0)):.0f}W"
                        load = f"{float(gpu.get('GPU use (%)', 0)):.0f}%"
                        vram = f"{float(gpu.get('GPU Memory Allocated (VRAM%)', 0)):.0f}%"
                        
                        # --- ICONS: 🌡️ Temp | ⚡ Power | 🚀 Load | 🧠 VRAM (AI-Chip) ---
                        status_msg = f"🌡️ {temp} | ⚡ {pwr} | 🚀 {load} | 🧠 {vram}"
                        
                        await __event_emitter__({
                            "type": "status",
                            "data": {
                                "description": status_msg,
                                "status": "done"
                            }
                        })
                    else:
                        raise ValueError("Keine GPU-Daten gefunden.")
                else:
                    raise Exception(f"Server-Fehler: {response.status_code}")

            except Exception as e:
                await __event_emitter__({
                    "type": "status",
                    "data": {
                        "description": f"⚠️ GPU-Fehler: {str(e)}",
                        "status": "error"
                    }
                })

        return body

    async def outlet(self, body: Dict[str, Any], __event_emitter__: Any = None) -> Dict[str, Any]:
        return body
