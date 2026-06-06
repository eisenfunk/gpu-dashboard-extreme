// --- GpuUsageEffect Class ---
export class GpuUsageEffect {
    constructor(cardId, valueDisplayId, barFillId) {
        this.cardId = cardId;
        this.valueDisplayId = valueDisplayId;
        this.barFillId = barFillId;
        this.dropsPerSecond = 0;
        this.vGpu = document.getElementById(this.valueDisplayId);
        this.bGpu = document.getElementById(this.barFillId);
    }

    update(gVal) {
        const val = parseFloat(gVal);
        this.vGpu.innerText = val.toFixed(0) + "%";
        this.bGpu.style.width = Math.min(val, 100) + "%";
        this.dropsPerSecond = val >= 50 ? 2 + (((val - 50) / 100) * 28) : 0;
    }

    getDropsPerSecond() {
        return this.dropsPerSecond;
    }
}
