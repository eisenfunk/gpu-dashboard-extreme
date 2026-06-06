// --- TemperatureStoveEffect Class ---
export class TemperatureStoveEffect {
    constructor() {
        this.minTemp = 40;
        this.maxTemp = 80;
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
        const vTemp = document.getElementById('v-temp');
        const bTemp = document.getElementById('b-temp');
        const cTempCard = document.getElementById('card-temp');
        vTemp.innerText = val.toFixed(1) + "°C";
        bTemp.style.width = Math.min(val, 100) + "%";
        const hue = 200 - ((val - 30) * (200 / 65));
        bTemp.style.backgroundColor = `hsl(${hue}, 100%, 50%)`;
        if (val > this.maxTemp) {
            cTempCard.classList.add('state-meltdown');
        } else {
            cTempCard.classList.remove('state-meltdown');
        }
    }
}
