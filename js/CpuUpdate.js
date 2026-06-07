// --- CPU Update Class ---
export class CpuUpdate {
    constructor() {
        this.container = document.getElementById('cpu-cores-container');
    }

    update(cpuData) {
        // Aktualisiere die CPU-Gesamtauslastung
        const cpuPercent = cpuData.cpu_percent;
        const cpuElement = document.getElementById('v-cpu');
        if (cpuElement) {
            cpuElement.innerText = Math.round(cpuPercent) + '%';
        }
        
        // Erstelle oder aktualisiere die CPU-Core-Balken
        this.updateCpuCoreBars(cpuData);
    }
    
    updateCpuCoreBars(cpuData) {
        if (!this.container) return;
        
        // Nur aktualisieren, wenn sich die Anzahl der Kerne geändert hat
        const numCores = cpuData.num_cores || 1;
        const numThreadsPerCore = cpuData.num_threads_per_core || 1;
        
        // Erstelle die HTML-Struktur für die CPU-Core-Balken
        let html = '';
        for (let i = 0; i < numCores; i++) {
            html += `
                <div class="cpu-core">
                    <div class="cpu-core-bar-container">
                        <div class="cpu-core-bar" id="cpu-core-${i}" style="height: 0%;"></div>
                    </div>
                </div>
            `;
        }
        
        this.container.innerHTML = html;
        
        // Aktualisiere die Balkenwerte
        if (cpuData.cpu_per_core && cpuData.cpu_per_core.length > 0) {
            for (let i = 0; i < numCores; i++) {
                const coreUsage = cpuData.cpu_per_core[i] || 0;
                const bar = document.getElementById(`cpu-core-${i}`);
                if (bar) {
                    // Sicherstellen, dass der Wert zwischen 0 und 100 liegt
                    const clampedValue = Math.max(0, Math.min(100, coreUsage));
                    // Setze Höhe auf 0% für 0% Nutzung, um 1px Linie zu vermeiden
                    bar.style.height = clampedValue === 0 ? '0%' : clampedValue + '%';
                }
            }
        }
    }
}