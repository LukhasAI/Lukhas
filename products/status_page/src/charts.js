/**
 * Simple chart rendering for status page
 * Uses HTML5 Canvas for lightweight charts
 */

class SimpleChart {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;

        this.ctx = this.canvas.getContext('2d');
        this.data = this.generateMockData();
        this.render();
    }

    generateMockData() {
        const points = 24; // 24 hours
        const data = [];

        for (let i = 0; i < points; i++) {
            data.push({
                x: i,
                y: 30 + Math.random() * 40 // Random latency 30-70ms
            });
        }

        return data;
    }

    render() {
        const width = this.canvas.width;
        const height = this.canvas.height;
        const padding = 40;

        // Clear canvas
        this.ctx.clearRect(0, 0, width, height);

        // Draw grid
        this.ctx.strokeStyle = '#E5E7EB';
        this.ctx.lineWidth = 1;

        for (let i = 0; i <= 5; i++) {
            const y = padding + (height - 2 * padding) * (i / 5);
            this.ctx.beginPath();
            this.ctx.moveTo(padding, y);
            this.ctx.lineTo(width - padding, y);
            this.ctx.stroke();
        }

        // Draw data line
        this.ctx.strokeStyle = '#7C3AED';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();

        const maxY = Math.max(...this.data.map(d => d.y));
        const scaleX = (width - 2 * padding) / (this.data.length - 1);
        const scaleY = (height - 2 * padding) / maxY;

        this.data.forEach((point, i) => {
            const x = padding + point.x * scaleX;
            const y = height - padding - point.y * scaleY;

            if (i === 0) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }
        });

        this.ctx.stroke();

        // Draw axis labels
        this.ctx.fillStyle = '#4B5563';
        this.ctx.font = '12px sans-serif';
        this.ctx.fillText('0h', padding, height - 20);
        this.ctx.fillText('24h', width - padding - 20, height - 20);
        this.ctx.fillText('0ms', 10, height - padding);
        this.ctx.fillText(`${maxY.toFixed(0)}ms`, 10, padding + 10);
    }
}

// Initialize charts on page load
document.addEventListener('DOMContentLoaded', () => {
    new SimpleChart('latency-chart');
    new SimpleChart('request-chart');
});
