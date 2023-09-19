var deg_to_rad = 0.0174533;
var decay=10;

function zero()
{
  $.ajax({
    datatype: "json",
    url: "/imu/zero",
    success: function(obj) {
      $('#msg').text(obj.message);
    }
  });
}

function imu_setup(viewport) {
	var canvas = $("#"+viewport)[0];
	var context = canvas.getContext("2d");
	return context.createImageData(canvas.width, canvas.height);
}

function imu_stream(viewport, imagedata) {
    var canvas = $("#"+viewport)[0];
    var context = canvas.getContext("2d");

    const imuStream = new EventSource("/imu/");
    console.log(imuStream.readyState);
    console.log(imuStream.url);

    imuStream.onopen = function() {
      console.log("imu connection opened");
      $("#msg").html("&nbsp;");
      $("#imu_status").text("...");
    };

    imuStream.onerror = function() {
      console.log("imu connection error");
      $("#msg").html("&#x274C;Connection Error");
      $("#imu_status").text("OFF");
    };

    imuStream.addEventListener("att", function(event) {
        // console.log(event);
	var att = JSON.parse(event.data);
	// console.log(att);
	$("#imu_status").text("ON");
	if (att.pitch != undefined) {
	  $("#pitch").text(Math.round(att.pitch));
	} else {
	  $("#pitch").text("");
	}
	if (att.roll != undefined) {
	  $("#roll").text(Math.round(att.roll));
	} else {
	  $("#roll").text("");
	}
	if (att.temp != undefined) {
	  $("#temp").text(Math.round(att.temp));
	} else {
	  $("#temp").text("");
	}
	if (att.time != undefined) {
	  $("#time").text(att.time.replace('T', ' '));
	} else {
	  $("#time").text("");
	}

	// Fade Out
	fade_points(viewport, imagedata, decay);

	// Draw Gauge
	cx = 0.5 * canvas.width;
	cy = 0.5 * canvas.height;
	draw_circle(viewport, imagedata, cx, cy, 100, [0,0,0,255]);
	draw_line(viewport, imagedata, 10, cy, canvas.width-10, cy, [0,0,0,255]);
	draw_line(viewport, imagedata, cx, 10, cx, canvas.height-10, [0,0,0,255]);

	if (att.roll != undefined && att.pitch != undefined) {
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
	}

	if (att.acc_x != undefined) {
	  // ACC X
	  ax = cx + 2*att.acc_x
	  draw_line(viewport, imagedata, ax, cy-10, ax, cy+10, [255,0,0,255]);
	} else {
		ax = cx;
	}

	if (att.acc_y != undefined) {
	  // ACC Y
	  ay = cy + 2*att.acc_y
	  draw_line(viewport, imagedata, cx-10, ay, cx+10, ay, [255,0,0,255]);
	} else {
	  ay = cy;
	}

	if (att.acc_z != undefined) {
	  // ACC_Z
	  draw_circle(viewport, imagedata, ax, ay, 2*att.acc_z, [255,0,0,255]);
	}

	context.putImageData(imagedata, 0, 0);
      $("#msg").html("&nbsp;");
    });
}
