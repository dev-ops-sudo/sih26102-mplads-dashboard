import { useEffect, useRef } from "react";

interface NodePoint {
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
  color: string;
  phase: number;
}

const palette = ["#38bdf8", "#34d399", "#fbbf24", "#fb7185", "#a78bfa"];

function makeNodes(width: number, height: number): NodePoint[] {
  return Array.from({ length: width < 640 ? 24 : 42 }, (_, index) => {
    const column = index % 7;
    const row = Math.floor(index / 7);
    const jitterX = ((index * 37) % 23) / 23;
    const jitterY = ((index * 53) % 29) / 29;
    return {
      x: ((column + 0.35 + jitterX * 0.35) / 7) * width,
      y: ((row + 0.25 + jitterY * 0.4) / 6.5) * height,
      vx: ((index % 3) - 1) * 0.08,
      vy: (((index + 1) % 3) - 1) * 0.06,
      radius: index % 8 === 0 ? 4.5 : index % 3 === 0 ? 3 : 2,
      color: palette[index % palette.length],
      phase: index * 0.63
    };
  });
}

export function IntelligenceNetwork() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const context = canvas.getContext("2d");
    if (!context) return;

    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let frame = 0;
    let nodes: NodePoint[] = [];
    let width = 0;
    let height = 0;
    let pointerX = -1000;
    let pointerY = -1000;

    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      const ratio = Math.min(window.devicePixelRatio || 1, 2);
      width = Math.max(rect.width, 1);
      height = Math.max(rect.height, 1);
      canvas.width = Math.round(width * ratio);
      canvas.height = Math.round(height * ratio);
      context.setTransform(ratio, 0, 0, ratio, 0, 0);
      nodes = makeNodes(width, height);
    };

    const draw = (time = 0) => {
      context.clearRect(0, 0, width, height);

      nodes.forEach((node, index) => {
        if (!reducedMotion) {
          node.x += node.vx;
          node.y += node.vy;
          if (node.x < 12 || node.x > width - 12) node.vx *= -1;
          if (node.y < 12 || node.y > height - 12) node.vy *= -1;

          const pointerDistance = Math.hypot(node.x - pointerX, node.y - pointerY);
          if (pointerDistance < 130 && pointerDistance > 0) {
            node.x += ((node.x - pointerX) / pointerDistance) * 0.7;
            node.y += ((node.y - pointerY) / pointerDistance) * 0.7;
          }
        }

        nodes.slice(index + 1).forEach((other) => {
          const distance = Math.hypot(node.x - other.x, node.y - other.y);
          if (distance > 128) return;
          context.beginPath();
          context.moveTo(node.x, node.y);
          context.lineTo(other.x, other.y);
          context.strokeStyle = `rgba(125, 211, 252, ${0.22 * (1 - distance / 128)})`;
          context.lineWidth = 0.8;
          context.stroke();
        });

        const pulse = reducedMotion ? 0 : Math.sin(time * 0.002 + node.phase) * 1.5;
        if (node.radius > 4) {
          context.beginPath();
          context.arc(node.x, node.y, node.radius + 7 + pulse, 0, Math.PI * 2);
          context.strokeStyle = `${node.color}55`;
          context.lineWidth = 1;
          context.stroke();
        }

        context.beginPath();
        context.arc(node.x, node.y, Math.max(1, node.radius + pulse * 0.25), 0, Math.PI * 2);
        context.fillStyle = node.color;
        context.fill();
      });

      if (!reducedMotion && nodes.length > 8) {
        for (let index = 0; index < 5; index += 1) {
          const from = nodes[index * 3];
          const to = nodes[index * 3 + 5];
          const progress = (time * 0.00012 + index * 0.19) % 1;
          context.beginPath();
          context.arc(from.x + (to.x - from.x) * progress, from.y + (to.y - from.y) * progress, 2.2, 0, Math.PI * 2);
          context.fillStyle = palette[index];
          context.fill();
        }
      }

      if (!reducedMotion) frame = requestAnimationFrame(draw);
    };

    const movePointer = (event: PointerEvent) => {
      const rect = canvas.getBoundingClientRect();
      pointerX = event.clientX - rect.left;
      pointerY = event.clientY - rect.top;
    };
    const clearPointer = () => {
      pointerX = -1000;
      pointerY = -1000;
    };

    resize();
    draw();
    const observer = new ResizeObserver(() => {
      resize();
      if (reducedMotion) draw();
    });
    observer.observe(canvas);
    canvas.addEventListener("pointermove", movePointer);
    canvas.addEventListener("pointerleave", clearPointer);

    return () => {
      cancelAnimationFrame(frame);
      observer.disconnect();
      canvas.removeEventListener("pointermove", movePointer);
      canvas.removeEventListener("pointerleave", clearPointer);
    };
  }, []);

  return <canvas ref={canvasRef} className="intelligence-network" aria-hidden="true" />;
}
