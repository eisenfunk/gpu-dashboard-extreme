// --- Dashboard Manager ---
export class DashboardManager {
    constructor(temperatureStoveEffect, powerFlashEffect, gpuUsageEffect, vramBloatEffect, sweatDropletEffect) {
        this.temperatureStoveEffect = temperatureStoveEffect;
        this.powerFlashEffect = powerFlashEffect;
        this.gpuUsageEffect = gpuUsageEffect;
        this.vramBloatEffect = vramBloatEffect;
        this.sweatDropletEffect = sweatDropletEffect;
        this.reconnectInterval = 5; // seconds between reconnection attempts
        this.eventSource = null;
        this._setupEventSource();
    }

    updateDashboard(data) {
        if (data.error) {
            document.getElementById('status-text').innerText = "Error: " + data.error;
            return;
        }
        document.getElementById('status-text').innerText = "LIVE";
        const c0 = data.card0;
        this.temperatureStoveEffect.update(c0["Temperature (Sensor edge) (C)"]);
        this.powerFlashEffect.update(c0["Current Socket Graphics Package Power (W)"]);
        this.gpuUsageEffect.update(c0["GPU use (%)"]);
        this.vramBloatEffect.update(c0["GPU Memory Allocated (VRAM%)"]);
        this.sweatDropletEffect.update(this.gpuUsageEffect.getDropsPerSecond());
    }

    _getStatusText() {
        const urlParams = new URLSearchParams(window.location.search);
        const isTest = urlParams.get('test') === 'true';
        return isTest ? ' [TEST]' : '';
    }

    _setConnectionStatus(status) {
        const statusText = document.getElementById('status-text');
        if (statusText) {
            statusText.innerText = status + this._getStatusText();
        }
    }

    _setupEventSource() {
        const urlParams = new URLSearchParams(window.location.search);
        const streamUrl = `/stream?interval=${urlParams.get('interval') || 2}&test=${urlParams.get('test') || 'false'}`;
        
        this._setConnectionStatus('Connecting...');
        
        this.eventSource = new EventSource(streamUrl);
        
        this.eventSource.onopen = () => {
            this._setConnectionStatus('Connected');
        };

        this.eventSource.onmessage = (e) => {
            this.updateDashboard(JSON.parse(e.data));
        };

        this.eventSource.onerror = () => {
            this._setConnectionStatus('Disconnected - Reconnecting in ' + this.reconnectInterval + 's...');
            this.eventSource.close();
            
            // Retry connection after interval (infinite retry)
            setTimeout(() => {
                this._setupEventSource();
            }, this.reconnectInterval * 1000);
        };
    }
}
