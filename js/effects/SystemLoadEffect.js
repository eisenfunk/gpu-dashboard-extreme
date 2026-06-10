// --- System Load Effect ---
export class SystemLoadEffect {
    constructor(cardId, valueId, barId) {
        this.card = document.getElementById(cardId);
        this.valueElement = document.getElementById(valueId);
        this.barElement = document.getElementById(barId);
        
        // Set initial state
        if (this.valueElement) {
            this.valueElement.innerText = '--';
        }
        if (this.barElement) {
            this.barElement.style.width = '0%';
        }
    }
    
    update(data) {
        // Extract system capacity saturation from the data
        const systemCapacitySaturation = data?.cpu?.system_capacity_saturation;
        
        if (this.valueElement) {
            // Display the system capacity saturation value
            if (systemCapacitySaturation !== undefined) {
                // Convert to percentage for display
                const percentage = Math.round(systemCapacitySaturation * 100);
                this.valueElement.innerText = percentage + '%';
            } else {
                this.valueElement.innerText = '--';
            }
        }
        
        if (this.barElement) {
            // Set bar width based on system capacity saturation
            const percentage = systemCapacitySaturation !== undefined ?
                Math.min(100, Math.max(0, systemCapacitySaturation * 100)) : 0;
            this.barElement.style.width = percentage + '%';
            
            // Apply color based on value
            if (percentage > 80) {
                this.barElement.className = 'bar-fill c-systemload';
            } else if (percentage > 60) {
                this.barElement.className = 'bar-fill c-systemload';
            } else {
                this.barElement.className = 'bar-fill c-systemload';
            }
        }
    }
}