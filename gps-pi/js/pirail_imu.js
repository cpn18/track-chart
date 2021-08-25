var deg_to_rad = 0.0174533;
var decay=10;

function imu_setup(viewport) {
	var canvas = document.getElementById(viewport);
	var context = canvas.getContext("2d");
	return context.createImageData(canvas.width, canvas.height);
}

function imu_stream(viewport, imagedata) {
    var canvas = document.getElementById(viewport);
    var context = canvas.getContext("2d");

    const imuStream = new EventSource("/imu-stream");
    console.log(imuStream.readyState);
    console.log(imuStream.url);

    imuStream.onopen = function() {
      console.log("imu connection opened");
      document.getElementById('msg').innerHTML = "&nbsp;";
      document.getElementById("imu_status").innerText = "...";
    };

    imuStream.onerror = function() {
      console.log("imu connection error");
      document.getElementById('msg').innerHTML = "&#x274C;Connection Error";
      document.getElementById("imu_status").innerText = "OFF";
    };

    imuStream.addEventListener("att", function(event) {
        // console.log(event);
	var att = JSON.parse(event.data);
	// console.log(att);
	document.getElementById("imu_status").innerText = "ON";
	document.getElementById("yaw").innerText = Math.round(att.yaw);
	document.getElementById("pitch").innerText = Math.round(att.pitch);
	document.getElementById("roll").innerText = Math.round(att.roll);
	document.getElementById("temp").innerText = Math.round(att.temp);
	document.getElementById("time").innerText = att.time.replace('T', ' ');

	// Fade Out
	fade_points(viewport, imagedata, decay);

	// Draw Gauge
	cx = 0.5 * canvas.width;
	cy = 0.5 * canvas.height;
	draw_circle(viewport, imagedata, cx, cy, 100, [0,0,0,255]);
	draw_line(viewport, imagedata, 10, cy, canvas.width-10, cy, [0,0,0,255]);
	draw_line(viewport, imagedata, cx, 10, cx, canvas.height-10, [0,0,0,255]);
	
	// Roll
	a1 = att.roll - 180;
	d1 = 100;
	a2 = att.roll;
	d2 = 100;

	// Pitch
	py = 10*att.pitch;

	x1 = cx + Math.cos(a1*deg_to_rad) * d1;
	y1 = cy + Math.sin(a1*deg_to_rad) * d1 + py;
	x2 = cx + Math.cos(a2*deg_to_rad) * d2;
	y2 = cy + Math.sin(a2*deg_to_rad) * d2 + py;
	draw_line(viewport, imagedata, x1, y1, x2, y2, [0,0,255,255]);

	// Yaw
	yx = (canvas.width + att.yaw) / 2;
	draw_line(viewport, imagedata, yx, cy-10, yx, cy+10, [0,255,0,255]);

	// ACC X
	ax = cx + 2*att.acc_x
	draw_line(viewport, imagedata, ax, cy-10, ax, cy+10, [255,0,0,255]);

	// ACC Y
	ay = cy + 2*att.acc_y
	draw_line(viewport, imagedata, cx-10, ay, cx+10, ay, [255,0,0,255]);

	// ACC_Z
	draw_circle(viewport, imagedata, ax, ay, 2*att.acc_z, [255,0,0,255]);

	context.putImageData(imagedata, 0, 0);
    });
}
