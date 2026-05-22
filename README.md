🚀 GPU Extreme Cockpit V4

 
 

 
 

 
 

GPU Extreme Cockpit ist ein hochperformantes, visuell intensives Monitoring-Widget für Grafikkarten. Es wurde speziell für Streamer (OBS/Streamlabs) oder Enthusiasten entwickelt, die ihre GPU-Auslastung nicht nur sehen, sondern spüren wollen. Durch extrem dynamische CSS-Animationen reagiert das Interface physisch auf die Last deiner Hardware.
✨ Features

    🔥 Extreme Visual Feedback:
        VRAM Bloat & Pop: Die VRAM-Box dehnt sich bei hoher Last aus und vollzieht einen "Comic-Style" Pop-and-Shrink-Zyklus.
        Meltdown Mode: Bei kritischen Temperaturen wechselt das Interface in einen rötlichen Schüttel-Modus.
        Lightning Bursts: Power-Spitzen lösen visuelle Blitzeffekte aus.
        Heat Effects: Temperatur-Anstiege verändern die Farbe und Intensität des Interfaces (Fire-Effect).
    ⚡ Real-Time Updates: Nutzt Server-Sent Events (SSE) für minimale Latenz bei höchster Performance.
    🛠️ Fully Customizable: Steuerung des Layouts und der Intensität direkt über URL-Parameter.
    🎮 Simulation Mode: Integrierter Test-Modus, um die Animationen ohne echte Last zu prüfen.

🛠️ Installation
Voraussetzungen

    Python 3.8+
    AMD GPU mit installierten ROCm-Treibern (nutzt rocm-smi zur Datenerfassung).
    Flask (Python Library).

Setup

     

    Repository klonen:
    bash
     
         
     
     
    1
    2
    git clone https://github.com/dein-username/gpu-extreme-cockpit.git
    cd gpu-extreme-cockpit
     
     
     

    Abhängigkeiten installieren:
    bash
     
         
     
     
    1
    pip install flask
     
     
     

    Skript starten:
    bash
     
         
     
     
    1
    python app.py
     
     

    Das Dashboard ist nun unter http://localhost:8090 erreichbar.

⚙️ Konfiguration (URL Parameters)

Du kannst das Verhalten des Widgets direkt beim Aufruf im Browser oder in OBS über URL-Parameter steuern:
Parameter
	
Typ
	
Standard
	
Beschreibung
col
	
Integer
	
2
	
Anzahl der Spalten im Grid (1, 2, oder 4).
interval
	
Float
	
2
	
Update-Intervall in Sekunden.
test
	
Boolean
	
false
	
Aktiviert den Simulations-Modus (ideal zum Testen der Animationen).
width
	
Integer
	
520
	
Breite des gesamten Widgets in Pixeln.
widget_size
	
String
	
520px
	
CSS-kompatible Breitenangabe.
 
  
 

Beispiel für ein 4-Spalten-Layout im Testmodus:
http://localhost:8090/?col=4&test=true&interval=1
🖥️ Integration in OBS

     Öffne OBS.
     Füge eine neue Quelle hinzu: Browser.
     Gib die URL ein: http://localhost:8090/?col=4&interval=2 (oder deine gewünschte Konfiguration).
     Setze die Breite und Höhe passend zu deiner Konfiguration.
     Fertig! Dein Cockpit ist live.

⚠️ Disclaimer

Dieses Tool liest Hardware-Daten über Systembefehle aus. Die Verwendung erfolgt auf eigene Gefahr. Die Animationen sind rein dekorativ und haben keinen Einfluss auf die Hardware-Performance oder die Kühlung.
📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

Developed with ❤️ for GPU Enthusiasts.
