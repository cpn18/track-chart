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
	$("#lidar_status").text("ON");
	lidar_update(name, imagedata, lidar);
      } else {
	$("#lidar_status").text("No 360 Scan");
      }
    } else if (lidar.class == 'LIDAR3D') {
	    if (lidar.depth != undefined) {
	        $("#lidar_status").text("ON");
	        lidar_update_3d(name, imagedata, lidar);
		   } else {
	$("#lidar_status").text("No 3D Scan");
		   }
    } else {
	$("#lidar_status").text("Unsupported LIDAR class");
    }
  });
}

// Color Maps
var white = [255, 255, 255, 255];
var black = [0, 0, 0, 255];
var spectrum = [[255, 0, 0, 255], [254, 1, 0, 255], [253, 2, 0, 255], [252, 3, 
0, 255], [251, 4, 0, 255], [250, 5, 0, 255], [249, 6, 0, 255], [248, 7, 0, 
255], [247, 8, 0, 255], [246, 9, 0, 255], [245, 10, 0, 255], [244, 11, 0, 255], 
[243, 12, 0, 255], [242, 13, 0, 255], [241, 14, 0, 255], [240, 15, 0, 255], 
[239, 16, 0, 255], [238, 17, 0, 255], [237, 18, 0, 255], [236, 19, 0, 255], 
[235, 20, 0, 255], [234, 21, 0, 255], [233, 22, 0, 255], [232, 23, 0, 255], 
[231, 24, 0, 255], [230, 25, 0, 255], [229, 26, 0, 255], [228, 27, 0, 255], 
[227, 28, 0, 255], [226, 29, 0, 255], [225, 30, 0, 255], [224, 31, 0, 255], 
[223, 32, 0, 255], [222, 33, 0, 255], [221, 34, 0, 255], [220, 35, 0, 255], 
[219, 36, 0, 255], [218, 37, 0, 255], [217, 38, 0, 255], [216, 39, 0, 255], 
[215, 40, 0, 255], [214, 41, 0, 255], [213, 42, 0, 255], [212, 43, 0, 255], 
[211, 44, 0, 255], [210, 45, 0, 255], [209, 46, 0, 255], [208, 47, 0, 255], 
[207, 48, 0, 255], [206, 49, 0, 255], [205, 50, 0, 255], [204, 51, 0, 255], 
[203, 52, 0, 255], [202, 53, 0, 255], [201, 54, 0, 255], [200, 55, 0, 255], 
[199, 56, 0, 255], [198, 57, 0, 255], [197, 58, 0, 255], [196, 59, 0, 255], 
[195, 60, 0, 255], [194, 61, 0, 255], [193, 62, 0, 255], [192, 63, 0, 255], 
[191, 64, 0, 255], [190, 65, 0, 255], [189, 66, 0, 255], [188, 67, 0, 255], 
[187, 68, 0, 255], [186, 69, 0, 255], [185, 70, 0, 255], [184, 71, 0, 255], 
[183, 72, 0, 255], [182, 73, 0, 255], [181, 74, 0, 255], [180, 75, 0, 255], 
[179, 76, 0, 255], [178, 77, 0, 255], [177, 78, 0, 255], [176, 79, 0, 255], 
[175, 80, 0, 255], [174, 81, 0, 255], [173, 82, 0, 255], [172, 83, 0, 255], 
[171, 84, 0, 255], [170, 85, 0, 255], [169, 86, 0, 255], [168, 87, 0, 255], 
[167, 88, 0, 255], [166, 89, 0, 255], [165, 90, 0, 255], [164, 91, 0, 255], 
[163, 92, 0, 255], [162, 93, 0, 255], [161, 94, 0, 255], [160, 95, 0, 255], 
[159, 96, 0, 255], [158, 97, 0, 255], [157, 98, 0, 255], [156, 99, 0, 255], 
[155, 100, 0, 255], [154, 101, 0, 255], [153, 102, 0, 255], [152, 103, 0, 255], 
[151, 104, 0, 255], [150, 105, 0, 255], [149, 106, 0, 255], [148, 107, 0, 255], 
[147, 108, 0, 255], [146, 109, 0, 255], [145, 110, 0, 255], [144, 111, 0, 255], 
[143, 112, 0, 255], [142, 113, 0, 255], [141, 114, 0, 255], [140, 115, 0, 255], 
[139, 116, 0, 255], [138, 117, 0, 255], [137, 118, 0, 255], [136, 119, 0, 255], 
[135, 120, 0, 255], [134, 121, 0, 255], [133, 122, 0, 255], [132, 123, 0, 255], 
[131, 124, 0, 255], [130, 125, 0, 255], [129, 126, 0, 255], [128, 127, 0, 255], 
[127, 128, 0, 255], [126, 129, 0, 255], [125, 130, 0, 255], [124, 131, 0, 255], 
[123, 132, 0, 255], [122, 133, 0, 255], [121, 134, 0, 255], [120, 135, 0, 255], 
[119, 136, 0, 255], [118, 137, 0, 255], [117, 138, 0, 255], [116, 139, 0, 255], 
[115, 140, 0, 255], [114, 141, 0, 255], [113, 142, 0, 255], [112, 143, 0, 255], 
[111, 144, 0, 255], [110, 145, 0, 255], [109, 146, 0, 255], [108, 147, 0, 255], 
[107, 148, 0, 255], [106, 149, 0, 255], [105, 150, 0, 255], [104, 151, 0, 255], 
[103, 152, 0, 255], [102, 153, 0, 255], [101, 154, 0, 255], [100, 155, 0, 255], 
[99, 156, 0, 255], [98, 157, 0, 255], [97, 158, 0, 255], [96, 159, 0, 255], 
[95, 160, 0, 255], [94, 161, 0, 255], [93, 162, 0, 255], [92, 163, 0, 255], 
[91, 164, 0, 255], [90, 165, 0, 255], [89, 166, 0, 255], [88, 167, 0, 255], 
[87, 168, 0, 255], [86, 169, 0, 255], [85, 170, 0, 255], [84, 171, 0, 255], 
[83, 172, 0, 255], [82, 173, 0, 255], [81, 174, 0, 255], [80, 175, 0, 255], 
[79, 176, 0, 255], [78, 177, 0, 255], [77, 178, 0, 255], [76, 179, 0, 255], 
[75, 180, 0, 255], [74, 181, 0, 255], [73, 182, 0, 255], [72, 183, 0, 255], 
[71, 184, 0, 255], [70, 185, 0, 255], [69, 186, 0, 255], [68, 187, 0, 255], 
[67, 188, 0, 255], [66, 189, 0, 255], [65, 190, 0, 255], [64, 191, 0, 255], 
[63, 192, 0, 255], [62, 193, 0, 255], [61, 194, 0, 255], [60, 195, 0, 255], 
[59, 196, 0, 255], [58, 197, 0, 255], [57, 198, 0, 255], [56, 199, 0, 255], 
[55, 200, 0, 255], [54, 201, 0, 255], [53, 202, 0, 255], [52, 203, 0, 255], 
[51, 204, 0, 255], [50, 205, 0, 255], [49, 206, 0, 255], [48, 207, 0, 255], 
[47, 208, 0, 255], [46, 209, 0, 255], [45, 210, 0, 255], [44, 211, 0, 255], 
[43, 212, 0, 255], [42, 213, 0, 255], [41, 214, 0, 255], [40, 215, 0, 255], 
[39, 216, 0, 255], [38, 217, 0, 255], [37, 218, 0, 255], [36, 219, 0, 255], 
[35, 220, 0, 255], [34, 221, 0, 255], [33, 222, 0, 255], [32, 223, 0, 255], 
[31, 224, 0, 255], [30, 225, 0, 255], [29, 226, 0, 255], [28, 227, 0, 255], 
[27, 228, 0, 255], [26, 229, 0, 255], [25, 230, 0, 255], [24, 231, 0, 255], 
[23, 232, 0, 255], [22, 233, 0, 255], [21, 234, 0, 255], [20, 235, 0, 255], 
[19, 236, 0, 255], [18, 237, 0, 255], [17, 238, 0, 255], [16, 239, 0, 255], 
[15, 240, 0, 255], [14, 241, 0, 255], [13, 242, 0, 255], [12, 243, 0, 255], 
[11, 244, 0, 255], [10, 245, 0, 255], [9, 246, 0, 255], [8, 247, 0, 255], [7, 
248, 0, 255], [6, 249, 0, 255], [5, 250, 0, 255], [4, 251, 0, 255], [3, 252, 0, 
255], [2, 253, 0, 255], [1, 254, 0, 255], [0, 255, 0, 255], [0, 254, 1, 255], 
[0, 253, 2, 255], [0, 252, 3, 255], [0, 251, 4, 255], [0, 250, 5, 255], [0, 
249, 6, 255], [0, 248, 7, 255], [0, 247, 8, 255], [0, 246, 9, 255], [0, 245, 
10, 255], [0, 244, 11, 255], [0, 243, 12, 255], [0, 242, 13, 255], [0, 241, 14, 
255], [0, 240, 15, 255], [0, 239, 16, 255], [0, 238, 17, 255], [0, 237, 18, 
255], [0, 236, 19, 255], [0, 235, 20, 255], [0, 234, 21, 255], [0, 233, 22, 
255], [0, 232, 23, 255], [0, 231, 24, 255], [0, 230, 25, 255], [0, 229, 26, 
255], [0, 228, 27, 255], [0, 227, 28, 255], [0, 226, 29, 255], [0, 225, 30, 
255], [0, 224, 31, 255], [0, 223, 32, 255], [0, 222, 33, 255], [0, 221, 34, 
255], [0, 220, 35, 255], [0, 219, 36, 255], [0, 218, 37, 255], [0, 217, 38, 
255], [0, 216, 39, 255], [0, 215, 40, 255], [0, 214, 41, 255], [0, 213, 42, 
255], [0, 212, 43, 255], [0, 211, 44, 255], [0, 210, 45, 255], [0, 209, 46, 
255], [0, 208, 47, 255], [0, 207, 48, 255], [0, 206, 49, 255], [0, 205, 50, 
255], [0, 204, 51, 255], [0, 203, 52, 255], [0, 202, 53, 255], [0, 201, 54, 
255], [0, 200, 55, 255], [0, 199, 56, 255], [0, 198, 57, 255], [0, 197, 58, 
255], [0, 196, 59, 255], [0, 195, 60, 255], [0, 194, 61, 255], [0, 193, 62, 
255], [0, 192, 63, 255], [0, 191, 64, 255], [0, 190, 65, 255], [0, 189, 66, 
255], [0, 188, 67, 255], [0, 187, 68, 255], [0, 186, 69, 255], [0, 185, 70, 
255], [0, 184, 71, 255], [0, 183, 72, 255], [0, 182, 73, 255], [0, 181, 74, 
255], [0, 180, 75, 255], [0, 179, 76, 255], [0, 178, 77, 255], [0, 177, 78, 
255], [0, 176, 79, 255], [0, 175, 80, 255], [0, 174, 81, 255], [0, 173, 82, 
255], [0, 172, 83, 255], [0, 171, 84, 255], [0, 170, 85, 255], [0, 169, 86, 
255], [0, 168, 87, 255], [0, 167, 88, 255], [0, 166, 89, 255], [0, 165, 90, 
255], [0, 164, 91, 255], [0, 163, 92, 255], [0, 162, 93, 255], [0, 161, 94, 
255], [0, 160, 95, 255], [0, 159, 96, 255], [0, 158, 97, 255], [0, 157, 98, 
255], [0, 156, 99, 255], [0, 155, 100, 255], [0, 154, 101, 255], [0, 153, 102, 
255], [0, 152, 103, 255], [0, 151, 104, 255], [0, 150, 105, 255], [0, 149, 106, 
255], [0, 148, 107, 255], [0, 147, 108, 255], [0, 146, 109, 255], [0, 145, 110, 
255], [0, 144, 111, 255], [0, 143, 112, 255], [0, 142, 113, 255], [0, 141, 114, 
255], [0, 140, 115, 255], [0, 139, 116, 255], [0, 138, 117, 255], [0, 137, 118, 
255], [0, 136, 119, 255], [0, 135, 120, 255], [0, 134, 121, 255], [0, 133, 122, 
255], [0, 132, 123, 255], [0, 131, 124, 255], [0, 130, 125, 255], [0, 129, 126, 
255], [0, 128, 127, 255], [0, 127, 128, 255], [0, 126, 129, 255], [0, 125, 130, 
255], [0, 124, 131, 255], [0, 123, 132, 255], [0, 122, 133, 255], [0, 121, 134, 
255], [0, 120, 135, 255], [0, 119, 136, 255], [0, 118, 137, 255], [0, 117, 138, 
255], [0, 116, 139, 255], [0, 115, 140, 255], [0, 114, 141, 255], [0, 113, 142, 
255], [0, 112, 143, 255], [0, 111, 144, 255], [0, 110, 145, 255], [0, 109, 146, 
255], [0, 108, 147, 255], [0, 107, 148, 255], [0, 106, 149, 255], [0, 105, 150, 
255], [0, 104, 151, 255], [0, 103, 152, 255], [0, 102, 153, 255], [0, 101, 154, 
255], [0, 100, 155, 255], [0, 99, 156, 255], [0, 98, 157, 255], [0, 97, 158, 
255], [0, 96, 159, 255], [0, 95, 160, 255], [0, 94, 161, 255], [0, 93, 162, 
255], [0, 92, 163, 255], [0, 91, 164, 255], [0, 90, 165, 255], [0, 89, 166, 
255], [0, 88, 167, 255], [0, 87, 168, 255], [0, 86, 169, 255], [0, 85, 170, 
255], [0, 84, 171, 255], [0, 83, 172, 255], [0, 82, 173, 255], [0, 81, 174, 
255], [0, 80, 175, 255], [0, 79, 176, 255], [0, 78, 177, 255], [0, 77, 178, 
255], [0, 76, 179, 255], [0, 75, 180, 255], [0, 74, 181, 255], [0, 73, 182, 
255], [0, 72, 183, 255], [0, 71, 184, 255], [0, 70, 185, 255], [0, 69, 186, 
255], [0, 68, 187, 255], [0, 67, 188, 255], [0, 66, 189, 255], [0, 65, 190, 
255], [0, 64, 191, 255], [0, 63, 192, 255], [0, 62, 193, 255], [0, 61, 194, 
255], [0, 60, 195, 255], [0, 59, 196, 255], [0, 58, 197, 255], [0, 57, 198, 
255], [0, 56, 199, 255], [0, 55, 200, 255], [0, 54, 201, 255], [0, 53, 202, 
255], [0, 52, 203, 255], [0, 51, 204, 255], [0, 50, 205, 255], [0, 49, 206, 
255], [0, 48, 207, 255], [0, 47, 208, 255], [0, 46, 209, 255], [0, 45, 210, 
255], [0, 44, 211, 255], [0, 43, 212, 255], [0, 42, 213, 255], [0, 41, 214, 
255], [0, 40, 215, 255], [0, 39, 216, 255], [0, 38, 217, 255], [0, 37, 218, 
255], [0, 36, 219, 255], [0, 35, 220, 255], [0, 34, 221, 255], [0, 33, 222, 
255], [0, 32, 223, 255], [0, 31, 224, 255], [0, 30, 225, 255], [0, 29, 226, 
255], [0, 28, 227, 255], [0, 27, 228, 255], [0, 26, 229, 255], [0, 25, 230, 
255], [0, 24, 231, 255], [0, 23, 232, 255], [0, 22, 233, 255], [0, 21, 234, 
255], [0, 20, 235, 255], [0, 19, 236, 255], [0, 18, 237, 255], [0, 17, 238, 
255], [0, 16, 239, 255], [0, 15, 240, 255], [0, 14, 241, 255], [0, 13, 242, 
255], [0, 12, 243, 255], [0, 11, 244, 255], [0, 10, 245, 255], [0, 9, 246, 
255], [0, 8, 247, 255], [0, 7, 248, 255], [0, 6, 249, 255], [0, 5, 250, 255], 
[0, 4, 251, 255], [0, 3, 252, 255], [0, 2, 253, 255], [0, 1, 254, 255], [0, 0, 
255, 255]];
var spectrum_length = spectrum.length - 1;

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

function base64_to_bytes(inData, rows, cols)
{
	rawString = atob(inData);
	outData = new Uint8Array(rawString.length);
	for (var i=0; i<rawString.length; i++) {
		outData[i] = rawString.charCodeAt(i);
	}

	newDepth = [];
	index = 0;
	for (var row=0; row < rows; row++) {
		depthRow = [];
		for (var col=0; col < columns; col++) {
			depthRow.push(outData[index] + outData[index+1] * 256);
			index += 2;
		}
		newDepth.push(depthRow);
	}
	return newDepth
}

function lidar_update_3d(name, imagedata, obj) {
	var canvas = $("#"+name)[0];
	var context = canvas.getContext("2d");

	if (typeof(obj.depth) == 'string') {
		// Decode the Base64 Input
		obj.depth = base64_to_bytes(obj.depth, obj.rows, obj.columns)
	}

	//  Find Min/Max Values
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

	// Populate Image
	for (var row=0; row < obj.depth.length; row++) {
		for (var col=0; col < obj.depth[row].length; col++) {
			value = obj.depth[row][col];
			if (is_valid(value)) {
				value = parseInt(spectrum_length * (value - min_value) / (max_value-min_value));
		 		color = spectrum[value];
			} else if (value == 65400 || value == 65500) {
		 		color = white;
			} else {
				color = black;
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
