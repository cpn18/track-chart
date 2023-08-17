var scale=0.1;
var decay=10;

function lidar_stream(name, imagedata)
{
  const lidarStream = new EventSource("/lidar/");
  console.log(lidarStream.readyState);
  console.log(lidarStream.url);

  lidarStream.onopen = function() {
    console.log("lidar connection opened");
    $("#msg").html("&nbsp;");
    $("#lidar_status").text("...");
  };

  lidarStream.onerror = function() {
    console.log("lidar connection error");
    $("#msg").html("&#x274C;Connection Error");
    $("#lidar_status").text("OFF");
  };

  lidarStream.addEventListener("lidar", function(event) {
    var lidar = JSON.parse(event.data)
    //console.log(lidar);
    if (lidar.class == 'LIDAR') {
      if (lidar.scan != undefined ) {
	lidar_update(name, imagedata, lidar);
	$("#lidar_status").text("ON");
      }
    } else if (lidar.class == 'LIDAR3D') {
	lidar_update_3d(name, imagedata, lidar);
	$("#lidar_status").text("ON");
    } else {
	$("#lidar_status").text("Unsupported LIDAR class");
    }
  });
}

function lidar_setup(name) {
	var canvas = $("#"+name)[0];
	var context = canvas.getContext("2d");
	return context.createImageData(canvas.width, canvas.height);
}

function is_valid(value) {
	if (value == 0x000 || value == 0xFF14 || value == 0xFF78 || value == 0xFFDC || value == 0xFFFA) {
		return false;
	}
	return true;
}

function quad_point(name, imagedata, x, y, color)
{
	draw_point(name, imagedata, 2*x, 2*y, color);
	draw_point(name, imagedata, 2*x+1, 2*y, color);
	draw_point(name, imagedata, 2*x, 2*y+1, color);
	draw_point(name, imagedata, 2*x+1, 2*y+1, color);
}

function lidar_update_3d(name, imagedata, obj) {
	var canvas = $("#"+name)[0];
	var context = canvas.getContext("2d");
	max_value = 0;
	min_value = 99999;
	for (var row=0; row < obj.depth.length; row++) {
		for (var col=0; col < obj.depth[row].length; col++) {
			value = obj.depth[row][col];
			if (is_valid(value)) {
				if (value > max_value) {
					max_value = value;
				}
				if (value < min_value) {
					min_value = value;
				}
			}
		}
	}
	for (var row=0; row < obj.depth.length; row++) {
		for (var col=0; col < obj.depth[row].length; col++) {
			value = obj.depth[row][col];
			if (is_valid(value)) {
				value = (256 * (value - min_value) / (max_value-min_value));
			 	color = [255-value, value, 0, 255];
			} else if (value == 65400 || value == 65500) {
			 	color = [255, 255, 255, 255];
			} else {
				color = [0, 0, 0, 255];
			}
			quad_point(name, imagedata, col, row, color);
		}
	}
	// update the image
	context.putImageData(imagedata, 0, 0);
}

function lidar_update(name, imagedata, obj) {
	var canvas = $("#"+name)[0];
	var context = canvas.getContext("2d");
	var last_x = 0;
	var last_y = 0;
	var x_origin = 0.50;
	var y_origin = 0.75;
	var deg_to_rad = 0.0174533;

	// Fade the existing data
	fade_points(name, imagedata, decay);

	// Last point
	last_x = 0;
	last_y = 0;

	// Draw a green pixel at the center of the LIDAR hub

	// The center of the LIDAR hub is offset toward the bottom
	// of the bit map
	cx = x_origin * canvas.width;
	cy = y_origin * canvas.height;
	draw_point(name, imagedata, cx, cy, [0, 255, 0, 255]);
	draw_circle(name, imagedata, cx, cy, 1000*scale, [0, 255, 0, 255]);
	draw_circle(name, imagedata, cx, cy, 2000*scale, [0, 255, 0, 255]);

	// Process all the data in the scan array
	for (var i=0; i<obj.scan.length; i++) {
		a = obj.scan[i][0] * deg_to_rad; // Angle in radians
		d = obj.scan[i][1] * scale;      // Distance in mm

		// convert a,d to x,y
		x = d * Math.sin(a) + x_origin * canvas.width;
		y = -d * Math.cos(a) + y_origin * canvas.height;

		// Try to group with the last pixel drawn
		// similar to how a RADAR system groups points
		// to create "bogie"
                dy = last_y - y;      // rise
		dx = last_x - x;      // run
		distance = Math.sqrt(dx*dx+dy*dy);

		// if distance between is less than 5% of the distance
		if (distance < d*0.05) {
                  draw_line(name, imagedata, last_x, last_y, x, y, [0, 0, 255, 255]);
                }

		// Draw a black pixel
	        draw_point(name, imagedata, x, y, [0, 0, 0, 255]);
		
		// keep track of the last point
		last_x = x;
		last_y = y;
	}
	// update the image
	context.putImageData(imagedata, 0, 0);
}
