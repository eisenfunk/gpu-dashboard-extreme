// --- TemperatureStoveEffect Class ---
export class TemperatureStoveEffect {
    constructor(fireThresholdLow, fireThresholdHigh, cardId, vId, bId) {
        this.minTemp = fireThresholdLow;
        this.maxTemp = fireThresholdHigh;
        this.cTempCard = document.getElementById(cardId);
        this.vTemp = document.getElementById(vId);
        this.bTemp = document.getElementById(bId);
        this.fireEffect = null;
    }

    setFireEffect(fireEffect) {
        this.fireEffect = fireEffect;
    }

    update(tVal) {
        const val = parseFloat(tVal);
        let tIntensity = Math.min(Math.max((val - this.minTemp) / (this.maxTemp - this.minTemp), 0), 1);
        if (this.fireEffect) {
            this.fireEffect.setIntensity(tIntensity);
        }
        this.vTemp.innerText = val.toFixed(1) + "°C";
        this.bTemp.style.width = Math.min(val, 100) + "%";
        const hue = 200 - ((val - 30) * (200 / 65));
        this.bTemp.style.backgroundColor = `hsl(${hue}, 100%, 50%)`;
        if (val > this.maxTemp) {
            this.cTempCard.classList.add('state-meltdown');
        } else {
            this.cTempCard.classList.remove('state-meltdown');
        }
    }
}
