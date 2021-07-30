var m_to_ft = 3.28084;
var ms_to_mph = 2.23694;
var deg_to_rad = 0.0174533;
var decay=10;

function mark()
{
  $.ajax({
    datatype: "json",
    url: "/mark?memo="+$('#memo').val(),
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
    url: "/hold?memo="+$('#memo').val(),
    success: function(obj) {
      $('#msg').text(obj.message);
      $('#memo').val('');
    }
  });
}

function gps_setup(viewport) {
	var canvas = document.getElementById(viewport);
	var context = canvas.getContext("2d");
	return context.createImageData(canvas.width, canvas.height);
}

function gps_stream(viewport, imagedata) {
    const gpsStream = new EventSource("/gps-stream");

    console.log(gpsStream.readyState);
    console.log(gpsStream.url);

    var canvas = document.getElementById(viewport);
    var context = canvas.getContext("2d"); 

    gpsStream.onopen = function() {
      console.log("connection opened");
      document.getElementById('msg').innerHTML = "&nbsp;";
      document.getElementById("mode").innerText = "...";
      document.getElementById("gps_count").innerText = "";
    };

    gpsStream.onerror = function() {
      console.log("connection error");
      document.getElementById('msg').innerHTML = "&#x274C;Connecton Error";
      document.getElementById("mode").innerText = "OFF";
      document.getElementById("gps_count").innerText = "";
    };

    gpsStream.addEventListener("tpv", function(event) {
        // console.log(event);
	var tpv = JSON.parse(event.data);
        // console.log(tpv);

	document.getElementById("gpstime").innerHTML = tpv.time.replace('T', '<br>');
	document.getElementById("ept").innerText = "+/-"+tpv.ept+"s";

	document.getElementById("lat").innerText = tpv.lat.toLocaleString(undefined,{minimumFractionDigits:6, maximumFractionDigits: 6});
	document.getElementById("epy").innerText = "+/-"+Math.round(tpv.epy*m_to_ft)+"ft";

	document.getElementById("lon").innerText = tpv.lon.toLocaleString(undefined,{minimumFractionDigits:6, maximumFractionDigits: 6});
	document.getElementById("epx").innerText = "+/-"+Math.round(tpv.epx*m_to_ft)+"ft";

	document.getElementById("alt").innerText = tpv.alt.toLocaleString(undefined,{minimumFractionDigits:1, maximumFractionDigits: 1});
	document.getElementById("epv").innerText = "+/-"+Math.round(tpv.epv*m_to_ft)+"ft";

	document.getElementById("speed").innerText = Math.round(tpv.speed*ms_to_mph);
	document.getElementById("eps").innerText = "+/-"+Math.round(tpv.eps*ms_to_mph)+"mph";

	document.getElementById("mode").innerText = tpv.mode + "D ";

	if (tpv.hold == -1) {
	  document.getElementById("hold").innerText = "OFF";
	} else {
	  document.getElementById("hold").innerText = tpv.hold;
	}
    });

    gpsStream.addEventListener("sky", function(event) {
        // console.log(event);
	var sky = JSON.parse(event.data);
	// console.log(sky);
	var used = 0;

	fade_points(viewport, imagedata, decay);

	draw_circle(viewport, imagedata, 0.5 * canvas.width, 0.5 * canvas.height, 45, [0,0,0,255]);
	draw_circle(viewport, imagedata, 0.5 * canvas.width, 0.5 * canvas.height, 90, [0,0,0,255]);

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
	    x = el * Math.sin(az) + 0.5 * canvas.width;
	    y = el * Math.cos(az) + 0.5 * canvas.height;

	    draw_point(viewport, imagedata, x+1, y, color);
	    draw_point(viewport, imagedata, x-1, y, color);
	    draw_point(viewport, imagedata, x, y, color);
	    draw_point(viewport, imagedata, x, y+1, color);
	    draw_point(viewport, imagedata, x, y-1, color);

	    draw_line(viewport, imagedata, 0.5*canvas.width, 0.5*canvas.height, x, y, color);
	}
	document.getElementById("gps_count").innerText = used + "/" + sky.satellites.length;
	context.putImageData(imagedata, 0, 0);
    });
}
