// --- FireEffect Class (Temperature Visual) ---
export class FireEffect {
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
