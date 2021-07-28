var scale=0.1;
var decay=10;

function imu_stream(name, imagedata)
{
  const lidarStream = new EventSource("/lidar-stream");
  console.log(lidarStream.readyState);
  console.log(lidarStream.url);

  lidarStream.onopen = function() {
    console.log("lidar connection opened");
    document.getElementById('msg').innerHTML = "&nbsp;";
  };

  lidarStream.onerror = function() {
    console.log("lidar connection error");
    document.getElementById('msg').innerHTML = "&#x274C;Connection Error";
  };

  lidarStream.addEventListener("lidar", function(event) {
    var lidar = JSON.parse(event.data)
    imu_update(name, imagedata, lidar);
  });
}

function fade_points(name, imagedata, decay)
{
	var canvas = document.getElementById(name);

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

function draw_point(name, imagedata, x, y, r, g, b, a) {
	var canvas = document.getElementById(name);

	// Each "bit" is controlled by four bytes
	pixel = (y * canvas.width + x) * 4;
	imagedata.data[pixel] = r;     // RED
	imagedata.data[pixel+1] = g;   // GREEN
	imagedata.data[pixel+2] = b;   // BLUE
	imagedata.data[pixel+3] = a;   // ALPHA
}

function draw_line(name, imagedata, x1, y1, x2, y2, r, g, b, a) {
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
	       draw_point(name, imagedata, tx, Math.round(ty), r, g, b, a);
             }
         } else {  // slope greater than 1
             // sort the y end points
	     if (y > y2) {
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
	       draw_point(name, imagedata, Math.round(tx), ty, r, g, b, a);
	     }
        }
}

function imu_setup(name) {
	var canvas = document.getElementById(name);
	var context = canvas.getContext("2d");
	return context.createImageData(canvas.width, canvas.height);
}

function imu_update(name, imagedata, obj) {
	var canvas = document.getElementById(name);
	var context = canvas.getContext("2d");
	var last_x = 0;
	var last_y = 0;

	// Fade the existing data
	fade_points(name, imagedata, decay);

	// Last point
	last_x = 0;
	last_y = 0;

	// Draw a green pixel at the center of the LIDAR hub

	// The center of the LIDAR hub is offset toward the bottom
	// of the bit map
	x = Math.round(canvas.width / 2);
	y = Math.round(0.75 * canvas.height);
	draw_point(name, imagedata, x, y, 0, 255, 0, 255);

	// Process all the data in the scan array
	for (var i=0; i<obj.scan.length; i++) {
		a = obj.scan[i][0];          // Angle in degrees
		d = obj.scan[i][1] * scale;  // Distance in mm

		// convert a,d to x,y
		x = Math.round(d * Math.sin(a*0.0174533) + canvas.width / 2);
		y = Math.round(-d * Math.cos(a*0.0174533) + 0.75 * canvas.height);

		// filter based on canvas size
		if (x < 0 || x >= canvas.width || y < 0 || y >= canvas.height) {
			continue;
		}

		// Draw a black pixel
	        draw_point(name, imagedata, x, y, 0, 0, 0, 255);

		// Try to group with the last pixel drawn
		// similar to how a RADAR system groups points
		// to create "bogie"
                dy = last_y - y;      // rise
		dx = last_x - x;      // run
		distance = Math.sqrt(dx*dx+dy*dy);

		if (distance < d*0.05) {
                  draw_line(name, imagedata, last_x, last_y, x, y, 0, 0, 255, 255);
                }
		
		// keep track of the last point
		last_x = x;
		last_y = y;
	}
	// update the image
	context.putImageData(imagedata, 0, 0);
}
