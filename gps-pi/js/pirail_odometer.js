var m_to_ft = 3.28084;
var ms_to_mph = 2.23694;
var deg_to_rad = 0.0174533;
var decay=10;

function reset()
{
  $.ajax({
    datatype: "json",
    url: "/gps/odometer-reset?memo="+$('#memo').val(),
    success: function(obj) {
      $('#msg').text(obj.message);
      $('#memo').val('');
    }
  });
}

function gps_stream(viewport, imagedata) {
    const gpsStream = new EventSource("/gps/stream");

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

	if (typeof tpv.speed != 'undefined') {
	    $("#speed").text(Math.round(tpv.speed*ms_to_mph));
	}
	if (typeof tpv.eps != 'undefined') {
	    $("#eps").html("&plusmn;"+Math.round(tpv.eps*ms_to_mph)+"mph");
	}
	if (typeof tpv.odometer != 'undefined') {
	    $("#odometer").text(tpv.odometer.toFixed(2));
	}
	if (typeof tpv.mode != 'undefined') {
	    $("#mode").text(tpv.mode + "D ");
	}
    });

}
