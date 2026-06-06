// --- VramBloatEffect Class ---
export class VramBloatEffect {
    constructor(animIntervalMs, bloatSequenceLength, threshold, cardId, vId, bId) {
        this.animIntervalMs = animIntervalMs;
        this.bloatSequenceLength = bloatSequenceLength;
        this.threshold = threshold;
        this.state = {
            intensity: 0,
            baseBx: 1,
            baseBy: 1,
            startTime: 0
        };
        this.shakeInterval = null;
        this.vVram = document.getElementById(vId);
        this.bVram = document.getElementById(bId);
        this.cVramCard = document.getElementById(cardId);
    }

    update(vVal) {
        const val = parseFloat(vVal);

        this.vVram.innerText = val.toFixed(0) + "%";
        this.bVram.style.width = Math.min(val, 100) + "%";
        const cVramContent = this.cVramCard.querySelector('.card-content');

        if (val > this.threshold) {
            this._handleActiveState(val, this.cVramCard, cVramContent);
        } else {
            this._handleResetState(this.cVramCard, cVramContent);
        }
    }

    _handleActiveState(val, cVramCard, cVramContent) {
        const intensity = (val - this.threshold) / (100 - this.threshold);
        this.state.intensity = intensity;

        // 1. Die "Base" Skalierung (das langsame Bloaten)
        const bloomFactor = Math.sqrt(intensity);
        this.state.baseBx = 1 + (0.05 * bloomFactor);
        this.state.baseBy = 1 + (0.2 * bloomFactor);

        // 2. Radius & Background (basierend auf Base-Bloat)
        const brPercent = 15 + (intensity * 10);
        cVramCard.style.setProperty('--br', brPercent + '%');
        cVramCard.style.setProperty('--bg-lightness', (intensity * 15) + "%");
        cVramCard.classList.add('state-pressure');

        if (!this.shakeInterval) {
            this.state.startTime = Date.now();
            this.shakeInterval = setInterval(() => {
                this._animationTick(cVramCard, cVramContent,);
            }, this.animIntervalMs);
        }
    }

    _handleResetState(cVramCard, cVramContent) {
        this.state.intensity = 0;
        this.state.baseBx = 1;
        this.state.baseBy = 1;
        
        cVramCard.classList.remove('state-pressure');
        cVramCard.style.transform = '';
        cVramCard.style.setProperty('--br', '12px');
        cVramCard.style.setProperty('--bg-lightness', '0%');
        if (this.shakeInterval) {
            clearInterval(this.shakeInterval);
            this.shakeInterval = null;
        }
        cVramContent.style.setProperty('--app-bx', '1');
        cVramContent.style.setProperty('--app-by', '1');
        cVramContent.style.setProperty('--rot', '0deg');
        cVramContent.style.setProperty('--tx', '0px');
        cVramContent.style.setProperty('--ty', '0px');
    }

    _animationTick(cVramCard, cVramContent) {
        const now = Date.now();
        const thres1 = 0.85;
        const thres2 = 0.95;

        let elapsed = now - this.state.startTime;

        if (elapsed >= this.bloatSequenceLength) {
            this.state.startTime = now;
            elapsed = 0;
        }

        const ratio = elapsed / this.bloatSequenceLength;
        let curBx, curBy, scale, brightness, innerScale;
        
        // --- PHASE LOGIC (Comic Style) ---
        if (ratio < thres1) {
            scale = (ratio / thres1 * 0.1 ) + 1 ;
            curBx = this.state.baseBx * (scale * 1);
            curBy = this.state.baseBy * scale * scale * scale;
            brightness = 50 * ratio * this.state.intensity * this.state.intensity;
            innerScale = 1;
        } else if (ratio < thres2) {
            scale = (1.8 - ratio) * 1.2;
            curBx =  scale;
            curBy =  scale * 1.5;
            brightness = 100 * ratio  * this.state.intensity * this.state.intensity;
            innerScale = 1;
        } else  {
            scale = (ratio * this.state.intensity);
            curBx = this.state.baseBx * ratio * ratio * ratio;
            curBy = this.state.baseBx * ratio * ratio * ratio;
            brightness = (1 - ratio) * 10 * this.state.intensity * this.state.intensity;
            innerScale = ratio * ratio * ratio * ratio * ratio;
        }
        const brPercent = (5 + (this.state.intensity * 10)) + (scale * 20);
        cVramCard.style.setProperty('--br', brPercent + '%');
        cVramCard.style.setProperty('--bg-lightness', brightness + "%");

        // --- JITTER (Nur in der Normal-Phase für knackiges Gefühl) ---
        const shakePower = this.state.intensity * this.state.intensity;
        const isJittering = (ratio < thres1);
        const jitterScale = isJittering ? (1 - (shakePower * 0.02 * Math.sin(elapsed / 40))) : 1;
        
        const finalBx = curBx * jitterScale;
        const finalBy = curBy * jitterScale;

        // Apply transform to Card (using transform instead of width/height)
        cVramCard.style.transform = `scale(${finalBx}, ${finalBy})`;

        // Rattle Werte für Content
        const rot = (Math.random() * 4 - 2) * shakePower * (isJittering ? 1 : 0.3);
        const tx = (Math.random() * 6 - 2) * shakePower * (isJittering ? 0.1 : 0);
        const ty = (Math.random() * 6 - 2) * shakePower * (isJittering ? 0.1 : 0);

        // Apply counter-scale + Rotation/Translation to Content
        let contentBx = innerScale / finalBx;
        let contentBy = innerScale / finalBy;

        cVramContent.style.setProperty('--app-bx', contentBx);
        cVramContent.style.setProperty('--app-by', contentBy);
        cVramContent.style.setProperty('--rot', rot + 'deg');
        cVramContent.style.setProperty('--tx', tx + 'px');
        cVramContent.style.setProperty('--ty', ty + 'px');
    }
}
