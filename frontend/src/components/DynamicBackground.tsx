"use client";

import React, { useEffect, useRef } from 'react';
import { useTheme } from '@/context/ThemeContext';

export default function DynamicBackground() {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const { theme, isAnimated } = useTheme();

    useEffect(() => {
        if (!isAnimated || theme !== 'hazard') return;

        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d', { alpha: false });
        if (!ctx) return;

        let animationFrameId: number;

        const resizeCanvas = () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        };

        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        const particles: { x: number; y: number; speed: number; size: number; opacity: number; life: number; maxLife: number; vx: number }[] = [];
        const particleCount = Math.min(window.innerWidth / 8, 200); // Responsive count

        for (let i = 0; i < particleCount; i++) {
            particles.push(createParticle(canvas, true));
        }

        function createParticle(canvas: HTMLCanvasElement, randomY: boolean = false) {
            return {
                x: Math.random() * canvas.width,
                y: randomY ? Math.random() * canvas.height : canvas.height + Math.random() * 100,
                speed: 0.2 + Math.random() * 1.5,
                size: Math.random() * 2.5 + 0.5,
                opacity: Math.random() * 0.6 + 0.1,
                life: 0,
                maxLife: 200 + Math.random() * 300,
                vx: (Math.random() - 0.5) * 0.5
            };
        }

        const render = () => {
            // Draw background
            const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
            gradient.addColorStop(0, '#020502'); // Very dark green/black
            gradient.addColorStop(1, '#051205'); // Slightly lighter dark green
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Draw grid (subtle)
            ctx.strokeStyle = 'rgba(57, 255, 20, 0.03)';
            ctx.lineWidth = 1;
            const gridSize = 40;
            ctx.beginPath();
            for (let x = 0; x < canvas.width; x += gridSize) {
                ctx.moveTo(x, 0);
                ctx.lineTo(x, canvas.height);
            }
            for (let y = 0; y < canvas.height; y += gridSize) {
                ctx.moveTo(0, y);
                ctx.lineTo(canvas.width, y);
            }
            ctx.stroke();

            particles.forEach((p, index) => {
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                
                // Glow effect occasionally
                if (Math.random() > 0.95) {
                    ctx.shadowBlur = 15;
                    ctx.shadowColor = '#39FF14';
                } else {
                    ctx.shadowBlur = 5;
                    ctx.shadowColor = 'rgba(57, 255, 20, 0.5)';
                }
                
                const currentOpacity = p.opacity * (1 - p.life / p.maxLife);
                ctx.fillStyle = `rgba(57, 255, 20, ${currentOpacity})`;
                ctx.fill();

                // Reset shadow
                ctx.shadowBlur = 0;

                p.y -= p.speed;
                p.x += Math.sin(p.life / 30) * 0.5 + p.vx;
                p.life++;

                if (p.life >= p.maxLife || p.y < -10) {
                    particles[index] = createParticle(canvas);
                }
            });

            // Draw vignette
            const vignette = ctx.createRadialGradient(
                canvas.width / 2, canvas.height / 2, 0,
                canvas.width / 2, canvas.height / 2, Math.max(canvas.width, canvas.height) / 1.5
            );
            vignette.addColorStop(0, 'rgba(0,0,0,0)');
            vignette.addColorStop(1, 'rgba(0,0,0,0.8)');
            ctx.fillStyle = vignette;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            animationFrameId = requestAnimationFrame(render);
        };

        render();

        return () => {
            window.removeEventListener('resize', resizeCanvas);
            cancelAnimationFrame(animationFrameId);
        };
    }, [theme, isAnimated]);

    if (!isAnimated || theme !== 'hazard') return null;

    return (
        <canvas
            ref={canvasRef}
            className="fixed inset-0 pointer-events-none z-[-1] transition-opacity duration-1000"
            style={{ width: '100vw', height: '100vh', opacity: 1 }}
            aria-hidden="true"
        />
    );
}
