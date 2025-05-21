// Convert degrees to radians
export const deg_to_rad = 0.0174533;

export function fade_points(canvas, imagedata, decay) {
  for (let i = 0; i < canvas.width * canvas.height * 4; i += 4) {
    for (let j = 0; j < 3; j++) {
      if (imagedata.data[i + j] < 255) {
        imagedata.data[i + j] = Math.min(imagedata.data[i + j] + decay, 255);
      }
    }
  }
}

export function draw_point(canvas, imagedata, x, y, color) {
  // need to be integers
  const ix = Math.round(x);
  const iy = Math.round(y);

  // filter based on canvas size
  if (ix < 0 || ix >= canvas.width || iy < 0 || iy >= canvas.height) {
    return;
  }

  // Each "bit" is controlled by four bytes
  let pixelIndex = (iy * canvas.width + ix) * 4;
  imagedata.data[pixelIndex + 0] = color[0]; // RED
  imagedata.data[pixelIndex + 1] = color[1]; // GREEN
  imagedata.data[pixelIndex + 2] = color[2]; // BLUE
  imagedata.data[pixelIndex + 3] = color[3]; // ALPHA

  imagedata.data[pixelIndex + 4] = color[0]; // RED
  imagedata.data[pixelIndex + 5] = color[1]; // GREEN
  imagedata.data[pixelIndex + 6] = color[2]; // BLUE
  imagedata.data[pixelIndex + 7] = color[3]; // ALPHA

  pixelIndex += canvas.width*4

  imagedata.data[pixelIndex + 0] = color[0]; // RED
  imagedata.data[pixelIndex + 1] = color[1]; // GREEN
  imagedata.data[pixelIndex + 2] = color[2]; // BLUE
  imagedata.data[pixelIndex + 3] = color[3]; // ALPHA

  imagedata.data[pixelIndex + 4] = color[0]; // RED
  imagedata.data[pixelIndex + 5] = color[1]; // GREEN
  imagedata.data[pixelIndex + 6] = color[2]; // BLUE
  imagedata.data[pixelIndex + 7] = color[3]; // ALPHA
}

export function draw_line(canvas, imagedata, x1, y1, x2, y2, color) {
  let dy = y2 - y1; // rise
  let dx = x2 - x1; // run

// slope less than 1, sort x endpoints
  if (Math.abs(dx) > Math.abs(dy)) {
    let start_x, end_x, start_y, end_y;
    if (x1 > x2) {
      start_x = x2;
      end_x = x1;
      start_y = y2;
      end_y = y1;
    } else {
      start_x = x1;
      end_x = x2;
      start_y = y1;
      end_y = y2;
    }
	// draw a horizontal line from start_x to end_x
    dx = end_x - start_x;
    dy = end_y - start_y;
    let ty = start_y;
    const slope = dy / dx;

    for (let tx = start_x; tx <= end_x; tx++) {
      draw_point(canvas, imagedata, tx, ty, color);
      ty += slope;
    }
  } 
  // Else slope >= 1 in magnitude, use y as the driving variable
  else {
    let start_x, end_x, start_y, end_y;
    if (y1 > y2) {
      start_x = x2;
      end_x = x1;
      start_y = y2;
      end_y = y1;
    } else {
      start_x = x1;
      end_x = x2;
      start_y = y1;
      end_y = y2;
    }
	// draw a vertical line from start_y to end_y
    dx = end_x - start_x;
    dy = end_y - start_y;
    let tx = start_x;
    const slope = dx / dy;

    for (let ty = start_y; ty <= end_y; ty++) {
      draw_point(canvas, imagedata, tx, ty, color);
      tx += slope;
    }
  }
}

export function draw_circle(canvas, imagedata, cx, cy, r, color) {
  let last_x = 0;
  let last_y = 0;

  for (let a = 0; a < 360; a++) {
    const x = cx + r * Math.sin(a * deg_to_rad);
    const y = cy + r * Math.cos(a * deg_to_rad);
    if (a > 0) {
      draw_line(canvas, imagedata, x, y, last_x, last_y, color);
    }
    last_x = x;
    last_y = y;
  }
}
