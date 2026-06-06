// --- PowerFlashEffect Class ---
export class PowerFlashEffect {
    constructor(thresholdMin, thresholdMax, cardId, vId, bId) {
        this.cardId = cardId;

        this.card = document.getElementById(cardId);
        this.bPower = document.getElementById(bId);
        this.vPower = document.getElementById(vId);
        this.thresholdMin = thresholdMin;
        this.thresholdMax = thresholdMax;
        this.timeout = null;
    }

    update(pVal) {
        const val = parseFloat(pVal);
        let pIntensity = Math.max(0, Math.min((val - this.thresholdMin) / (this.thresholdMax - this.thresholdMin), 1));
        const saturation = 100 * (1 - pIntensity);
        const lightness = 50 + (50 * pIntensity);
        this.vPower.innerText = val.toFixed(1) + "W";
        this.bPower.style.width = Math.min((val / 90 * 100), 100) + "%";
        this.bPower.style.backgroundColor = `hsl(200, ${saturation}%, ${lightness}%)`;
        this.bPower.style.setProperty('--glow-blur', (pIntensity * 15) + 'px');
        this.bPower.style.setProperty('--glow-opacity', pIntensity);
        this.bPower.style.setProperty('--glow-color', `rgba(0, 212, 255, ${pIntensity})`);
        if (val < this.thresholdMin) {
            this.card.classList.remove('state-lightning');
            this.card.style.transform = 'rotate(0deg)';
            if (this.timeout) { clearTimeout(this.timeout); this.timeout = null; }
            return;
        }
        if (this.timeout) return;
        const runFlashCycle = () => {
            const randomAngle = (Math.random() * 20 - 10);
            this.card.classList.remove('state-lightning');
            void this.card.offsetWidth;
            this.card.classList.add('state-lightning');
            this.card.style.transform = `rotate(${randomAngle}deg)`;
            setTimeout(() => { this.card.style.transform = 'rotate(0deg)'; this.card.classList.remove('state-lightning'); }, 150);
            const minGap = 110 * (1 - pIntensity) + 40;
            const maxGap = (2000 - 1000 * pIntensity) * (1 - pIntensity) + 50;
            this.timeout = setTimeout(runFlashCycle, Math.random() * (maxGap - minGap) + minGap);
        };
        runFlashCycle();
    }
}
