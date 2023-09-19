var m_to_ft = 3.28084;
var ms_to_mph = 2.23694;
var deg_to_rad = 0.0174533;
var decay=10;

function reset()
{
  $.ajax({
    datatype: "json",
    url: "/gps/odometer-reset?mileage="+$('#mileage').val(),
    success: function(obj) {
      $('#msg').text(obj.message);
      $('#mileage').val('');
    }
  });
}

function reverse()
{
  $.ajax({
    datatype: "json",
    url: "/gps/odometer-reverse",
    success: function(obj) {
      $('#msg').text(obj.message);
      $('#memo').val('');
    }
  });
}

function gps_stream(viewport, imagedata) {
    const gpsStream = new EventSource("/gps/");

    console.log(gpsStream.readyState);
    console.log(gpsStream.url);

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

	if (tpv.speed != undefined) {
	    $("#speed").text(Math.round(tpv.speed*ms_to_mph));
	}
	if (tpv.eps != undefined) {
	    $("#eps").html("&plusmn;"+Math.round(tpv.eps*ms_to_mph)+"mph");
	} else {
	    $("#eps").text("mph");
	}
	if (tpv.odometer != undefined) {
		var mileage = tpv.odometer.toFixed(3);
		if (tpv.odir == 1) {
			dir = "&#x2B06;";
		} else {
			dir = "&#x2B07;";
		}
	    $("#odometer").html('<font size="+2">' + mileage.slice(0,-1) + '</font>' + mileage.slice(-1));
	    $("#odir").html(dir + " mi");
	} else {
            $("#odometer").text("");
            $("#odir").text("");
	}
	if (tpv.mode != undefined) {
	    $("#mode").text(tpv.mode + "D ");
	} else {
	    $("#mode").text("?D ");
	}
        $('#msg').html('&nbsp;');
    });

	gpsStream.addEventListener("sky", function(event) {
        // console.log(event);
        var sky = JSON.parse(event.data);
        // console.log(sky);
	if (sky.satellites != undefined) {
        var used = 0;
		for (var i=0; i<sky.satellites.length; i++) {
			if (sky.satellites[i].used) {
				used ++;
			}
		}
		$("#gps_count").text(used + "/" + sky.satellites.length);
	} else {
		$("#gps_count").text("?/?");
	}
	});
}
