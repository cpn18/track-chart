var deg_to_rad = 0.0174533;

function fade_points(name, imagedata, decay)
{
	var canvas = $("#"+name)[0];

	// Fade the existing data
	//
	// Each "bit" is four bytes (RED, GREEN, BlUE, ALPHA)
	// Loop through the image, and brighten the RGB components
	for (var i=0; i<canvas.width*canvas.height*4; i += 4) {
	    for (var j=0; j < 3; j++) {
		if (imagedata.data[i+j] < 255) {
		    imagedata.data[i+j] = Math.min(imagedata.data[i+j] + decay, 255);
		}
	    }
	}
}

function draw_point(name, imagedata, x, y, color) {
	var canvas = $("#"+name)[0];

	// need to be integers
	x = Math.round(x);
	y = Math.round(y);

	// filter based on canvas size
	if (x < 0 || x >= canvas.width || y < 0 || y >= canvas.height) {
		return;
	}

	// Each "bit" is controlled by four bytes
	pixel = (y * canvas.width + x) * 4;
	imagedata.data[pixel] = color[0];     // RED
	imagedata.data[pixel+1] = color[1];   // GREEN
	imagedata.data[pixel+2] = color[2];   // BLUE
	imagedata.data[pixel+3] = color[3];   // ALPHA
}

function draw_line(name, imagedata, x1, y1, x2, y2, color) {
        dy = y2 - y1;      // rise
	dx = x2 - x1;      // run

        if ( Math.abs(dx) > Math.abs(dy) ) {  // slope less than 1
             // sort x endpoints
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
             for (tx = start_x, ty = start_y; tx < end_x; tx++, ty += dy/dx) {
	       draw_point(name, imagedata, tx, ty, color);
             }
         } else {  // slope greater than 1
             // sort the y end points
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
       	     for (ty = start_y, tx = start_x; ty < end_y; ty++, tx += dx/dy) {
	       draw_point(name, imagedata, tx, ty, color);
	     }
        }
}

function draw_circle(viewport, imagedata, cx, cy, r, color) {
	last_x = 0;
	last_y = 0;

	for (a=0; a<360; a++) {
		x = cx + r * Math.sin(a * deg_to_rad);
		y = cy + r * Math.cos(a * deg_to_rad);
		if (a > 0) {
		    draw_line(viewport, imagedata, x, y, last_x, last_y, color);
		}
		last_x = x;
		last_y = y;
	}
}
