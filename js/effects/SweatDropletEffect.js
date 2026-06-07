// --- SweatDropletEffect Class ---
export class SweatDropletEffect {
    constructor(sweatAnimIntervalMs, cardId) {
        this.card = document.getElementById(cardId);
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
        
        // Get card dimensions
        const cardRect = this.card.getBoundingClientRect();
        const cardWidth = cardRect.width;
        
        // Position droplet within card boundaries (random horizontal position)
        const leftPosition = Math.random() * (cardWidth - 4); // 4px is droplet width
        drop.style.left = leftPosition + 'px';
        
        // Set initial top position at the top of the card
        drop.style.top = '0px';
        
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
