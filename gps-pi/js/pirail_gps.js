var m_to_ft = 3.28084;
var ms_to_mph = 2.23694;
var deg_to_rad = 0.0174533;
var decay=10;

function mark()
{
  $.ajax({
    datatype: "json",
    url: "/gps/mark?memo="+$('#memo').val(),
    success: function(obj) {
      $('#msg').text(obj.message);
      $('#memo').val('');
    }
  });
}

function hold()
{
  $.ajax({
    datatype: "json",
    url: "/gps/hold?memo="+$('#memo').val(),
    success: function(obj) {
      $('#msg').text(obj.message);
      $('#memo').val('');
    }
  });
}

function gps_setup(viewport) {
	var canvas = $("#"+viewport)[0];
	var context = canvas.getContext("2d");
	return context.createImageData(canvas.width, canvas.height);
}

function gps_stream(viewport, imagedata) {
    const gpsStream = new EventSource("/gps/");

    console.log(gpsStream.readyState);
    console.log(gpsStream.url);

    var canvas = $("#"+viewport)[0];
    var context = canvas.getContext("2d");

    gpsStream.onopen = function() {
      console.log("connection opened");
      $("#msg").html("&nbsp;");
      $("#mode").text("...");
      $("#gps_count").text("");
    };

    gpsStream.onerror = function() {
      console.log("connection error");
      $("#msg").html("&#x274C;Connecton Error");
      $("#mode").text("OFF");
      $("#gps_count").text("");
    };

    gpsStream.addEventListener("tpv", function(event) {
        // console.log(event);
	var tpv = JSON.parse(event.data);
        // console.log(tpv);

	if (tpv.time != undefined) {
	    $("#gpstime").html(tpv.time.replace('T', '<br>'));
	} else {
	    $("#gpstime").text("It's Five O'clock Somewhere"));
	}
	if (tpv.ept != undefined) {
	    $("#ept").html("&plusmn;"+tpv.ept+"s");
	} else {
	    $("#ept").text("");
	}
	if (tpv.lat != undefined) {
	    $("#lat").html(tpv.lat.toLocaleString('en-US',{minimumFractionDigits:6, maximumFractionDigits: 6})+"&#xb0;");
	} else {
	  $("#lat").text("");
	}
	if (tpv.epv != undefined) {
	    $("#epy").html("&plusmn;"+Math.round(tpv.epy*m_to_ft)+"ft");
	} else {
	    $("#epy").text("");
        }
	if (tpv.lon != undefined) {
	    $("#lon").html(tpv.lon.toLocaleString('en-US',{minimumFractionDigits:6, maximumFractionDigits: 6})+"&#xb0;");
	} else {
	  $("#lon").text("");
	}
	if (tpv.epx != undefined) {
	    $("#epx").html("&plusmn;"+Math.round(tpv.epx*m_to_ft)+"ft");
	} else {
	    $("#epx").text("");
	}
	if (tpv.alt != undefined) {
	    $("#alt").html(tpv.alt.toLocaleString('en-US',{minimumFractionDigits:1, maximumFractionDigits: 1})+"&rsquo;");
	} else {
	  $("#alt").text("");
	if (tpv.epv != undefined) {
	    $("#epv").html("&plusmn;"+Math.round(tpv.epv*m_to_ft)+"ft");
	} else {
		$("#epv").text("");
	}
	if (tpv.speed != undefined) {
	    $("#speed").text(Math.round(tpv.speed*ms_to_mph));
	} else {
		$("#speed").text("");
	}
	if (tpv.eps != undefined) {
	    $("#eps").html("&plusmn;"+Math.round(tpv.eps*ms_to_mph)+"mph");
	} else {
		$("#eps").text("");
	}
	if (tpv.odometer != undefined) {
	    $("#odometer").text(tpv.odometer.toFixed(3)+"mi");
	} else {
		$("#odometer").text("");
	}
	if (tpv.mode != undefined) {
	    $("#mode").text(tpv.mode + "D ");
	} else {
	    $("#mode").text("?D ");
	}
	if (tpv.hold != undefined) {
	    if (tpv.hold == -1) {
	        $("#hold").text("OFF");
	    } else {
	        $("#hold").text(tpv.hold);
	    }
	} else {
	        $("#hold").text("OFF");
	}
    });

    gpsStream.addEventListener("sky", function(event) {
        // console.log(event);
	var sky = JSON.parse(event.data);
	// console.log(sky);
	var used = 0;

	cx = 0.5 * canvas.width;
	cy = 0.5 * canvas.height;

	fade_points(viewport, imagedata, decay);

	draw_circle(viewport, imagedata, cx, cy, 45, [0,0,0,255]);
	draw_circle(viewport, imagedata, cx, cy, 90, [0,0,0,255]);
	draw_line(viewport, imagedata, cx+45, cy, canvas.width, cy, [0,0,0,255]);
	draw_line(viewport, imagedata, cx-45, cy, 0, cy, [0,0,0,255]);
	draw_line(viewport, imagedata, cx, cy+45, cx, canvas.height, [0,0,0,255]);
	draw_line(viewport, imagedata, cx, cy-45, cx, 0, [0,0,0,255]);

	if (sky.satellites != undefined) {
	  for (var i=0; i<sky.satellites.length; i++) {
	      az = sky.satellites[i].az;
	      el = 90 - sky.satellites[i].el;
	      //console.log(az, el);
	      az = az * deg_to_rad;
	      if (sky.satellites[i].used) {
	          used ++;
		  color = [0, 255, 0, 255];
	      } else {
	          color = [255, 0, 0, 255];
	      }

	      x = el * Math.sin(az) + cx;
	      y = el * Math.cos(az) + cy;

	      draw_point(viewport, imagedata, x+1, y, color);
	      draw_point(viewport, imagedata, x-1, y, color);
	      draw_point(viewport, imagedata, x, y, color);
	      draw_point(viewport, imagedata, x, y+1, color);
	      draw_point(viewport, imagedata, x, y-1, color);

	      draw_line(viewport, imagedata, 0.5*canvas.width, 0.5*canvas.height, x, y, color);
	    }
	  $("#gps_count").text(used + "/" + sky.satellites.length);
	  context.putImageData(imagedata, 0, 0);
	} else {
	  $("#gps_count").text("?/?");
	}
    });
}
