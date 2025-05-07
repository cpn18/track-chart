import React, { useRef, useEffect, useState } from 'react';
import {
  deg_to_rad,
  fade_points,
  draw_point,
  draw_line,
  draw_circle
} from '../draw/pirail_draw';

function Gauge({ att, decay = 1 }) {
  const canvasRef = useRef(null);
  const [msg, setMsg] = useState('\u00A0'); 

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const context = canvas.getContext('2d');
    const { width, height } = canvas;

    // Clear the canvas
    context.clearRect(0, 0, width, height);

    // Get the existing pixels
    let imagedata = context.getImageData(0, 0, canvas.width, canvas.height);

    // Fade out
    fade_points(canvas, imagedata, decay);

    // Draw Gauge
    const cx = 0.5 * width;
    const cy = 0.5 * height;

    draw_circle(canvas, imagedata, cx, cy, 100, [0, 0, 0, 255]);
    draw_line(canvas, imagedata, 10, cy, width - 10, cy, [0, 0, 0, 255]);
    draw_line(canvas, imagedata, cx, 10, cx, height - 10, [0, 0, 0, 255]);

    if (att?.roll !== undefined && att?.pitch !== undefined) {
      // Roll
      const a1 = att.roll - 180;
      const d1 = 100;
      const a2 = att.roll;
      const d2 = 100;

      // Pitch 
      const py = 10 * att.pitch;

      const x1 = cx + Math.cos(a1 * deg_to_rad) * d1;
      const y1 = cy + Math.sin(a1 * deg_to_rad) * d1 + py;
      const x2 = cx + Math.cos(a2 * deg_to_rad) * d2;
      const y2 = cy + Math.sin(a2 * deg_to_rad) * d2 + py;

      draw_line(canvas, imagedata, x1, y1, x2, y2, [0, 0, 255, 255]);
    }

    let ax = cx;
    let ay = cy;

    // ACC X
    if (att?.acc_x !== undefined) {
      ax = cx + 2 * att.acc_x;
      draw_line(canvas, imagedata, ax, cy - 10, ax, cy + 10, [255, 0, 0, 255]);
    }

    // ACC Y
    if (att?.acc_y !== undefined) {
      ay = cy + 2 * att.acc_y;
      draw_line(canvas, imagedata, cx - 10, ay, cx + 10, ay, [255, 0, 0, 255]);
    }

    // ACC Z
    if (att?.acc_z !== undefined) {
      draw_circle(canvas, imagedata, ax, ay, 2 * att.acc_z, [255, 0, 0, 255]);
    }

    context.putImageData(imagedata, 0, 0);

    setMsg('\u00A0'); 
  }, [att, decay]);

  return (
    <div>
      <canvas ref={canvasRef} width={400} height={400} />
      <div>{msg}</div>
    </div>
  );
}

export default Gauge;
