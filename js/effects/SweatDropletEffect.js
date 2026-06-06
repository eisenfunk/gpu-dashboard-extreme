// --- SweatDropletEffect Class ---
export class SweatDropletEffect {
    constructor(sweatAnimIntervalMs, cardId) {
        this.card = document.getElementById(cardId);;
        this.sweatAnimIntervalMs = sweatAnimIntervalMs;
        this.dropsPerSecond = 0;
        this._startLoop();
    }

    update(gVal) {
        this.dropsPerSecond = gVal;
    }

    _spawn() {
        if (!this.card) return;
        const drop = document.createElement('div');
        drop.className = 'droplet';
        drop.style.left = Math.random() * 90 + '%';
        drop.style.animationDelay = (Math.random() * 0.2) + 's';
        this.card.appendChild(drop);
        setTimeout(() => drop.remove(), 1000);
    }

    _startLoop() {
        setInterval(() => {
            if (this.dropsPerSecond > 0) {
                const dropsToSpawnThisTick = (this.dropsPerSecond / 1000) * this.sweatAnimIntervalMs;
                for (let i = 0; i < Math.floor(dropsToSpawnThisTick); i++) { this._spawn(); }
                if (Math.random() < (dropsToSpawnThisTick % 1)) { this._spawn(); }
            }
        }, this.sweatAnimIntervalMs);
    }
}
