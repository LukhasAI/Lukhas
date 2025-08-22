// ParticleMorpher.js
// Provides a particle-based morphing animation for the sacred digital login ritual

import React, { useRef, useEffect } from "react";

export default function ParticleMorpher({ trigger }) {
    const canvasRef = useRef(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext("2d");
        let particles = [];
        const w = canvas.width = 400;
        const h = canvas.height = 200;
        const particleCount = 80;

        function randomColor() {
            const colors = ["#6e44ff", "#b892ff", "#faff7f", "#ffbfae", "#ff6e6c"];
            return colors[Math.floor(Math.random() * colors.length)];
        }

        function createParticles() {
            particles = [];
            for (let i = 0; i < particleCount; i++) {
                particles.push({
                    x: Math.random() * w,
                    y: Math.random() * h,
                    r: Math.random() * 6 + 2,
                    dx: (Math.random() - 0.5) * 2,
                    dy: (Math.random() - 0.5) * 2,
                    color: randomColor(),
                });
            }
        }

        function morphParticles() {
            for (let p of particles) {
                p.x += p.dx * 2;
                p.y += p.dy * 2;
                p.r += Math.sin(Date.now() / 200 + p.x) * 0.1;
                if (p.x < 0 || p.x > w) p.dx *= -1;
                if (p.y < 0 || p.y > h) p.dy *= -1;
            }
        }

        function drawParticles() {
            ctx.clearRect(0, 0, w, h);
            for (let p of particles) {
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.r, 0, 2 * Math.PI);
                ctx.fillStyle = p.color;
                ctx.globalAlpha = 0.7;
                ctx.fill();
            }
        }

        let animationId;
        function animate() {
            morphParticles();
            drawParticles();
            animationId = requestAnimationFrame(animate);
        }

        if (trigger) {
            createParticles();
            animate();
            setTimeout(() => {
                cancelAnimationFrame(animationId);
                ctx.clearRect(0, 0, w, h);
            }, 1800);
        } else {
            ctx.clearRect(0, 0, w, h);
        }

        return () => cancelAnimationFrame(animationId);
    }, [trigger]);

    return (
        <canvas ref={canvasRef} width={400} height={200} style={{ display: "block", margin: "2em auto", background: "#181818", borderRadius: "16px" }} />
    );
}
