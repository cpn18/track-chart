var m_to_ft = 3.28084;
var ms_to_mph = 2.23694;

function reset()
{
  $.ajax({
    datatype: "json",
    url: "/reset",
    success: function(obj) {
      $('#msg').text(obj.message);
    }
  });
}

function power()
{
  $.ajax({
    datatype: "json",
    url: "/poweroff",
    success: function(obj) {
      $('#msg').text(obj.message);
    }
  });
}

function dashboard() {
    const gpsStream = new EventSource("/gps/");
    console.log(gpsStream.readyState);
    console.log(gpsStream.url);

    const imuStream = new EventSource("/imu/");
    console.log(imuStream.readyState);
    console.log(imuStream.url);

    const lidarStream = new EventSource("/lidar/");
    console.log(lidarStream.readyState);
    console.log(lidarStream.url);

    const lpcmStream = new EventSource("/lpcm/");
    console.log(lpcmStream.readyState);
    console.log(lpcmStream.url);

    const sysStream = new EventSource("/sys/");
    console.log(sysStream.readyState);
    console.log(sysStream.url);

    hasTpv = hasSky = false;

    gpsStream.onopen = function() {
	console.log("gps connection opened");
        $("#mode").text("...");
        $("#gps_count").text("");
	};

    gpsStream.onerror = function() {
      console.log("gps connection error");
        $("#msg").html("&nbsp;");
        $("#mode").text("OFF");
        $("#gps_count").text("");
    };

    gpsStream.addEventListener("tpv", function(event) {
        // console.log(event);
	var tpv = JSON.parse(event.data);
        // console.log(tpv);
	$("#gpstime").html(tpv.time.replace('T', '<br>'));
	$("#ept").text("+/-"+tpv.ept+"s");
	$("#mode").text(tpv.mode + "D ");
	if (hasSky) {
	    gpsStream.close();
	} else {
	    hasTpv = true;
	}
    });

    gpsStream.addEventListener("sky", function(event) {
        // console.log(event);
	var sky = JSON.parse(event.data);
	// console.log(sky);
	var used = 0;
	for (var i=0; i<sky.satellites.length; i++) {
	    if (sky.satellites[i].used) {
	        used ++;
	    }
	}
	$("#gps_count").text(used + "/" + sky.satellites.length);
	if (hasTpv) {
	    gpsStream.close();
	} else {
	    hasSky = true;
	}
    });

    imuStream.onopen = function() {
	console.log("imu connection opened");
        $("#imu_status").text("...");
	};

    imuStream.onerror = function() {
      console.log("imu connection error");
      $("#msg").html("&nbsp;");
      $("#imu_status").text("OFF");
    };

    imuStream.addEventListener("att", function(event) {
        // console.log(event);
	var att = JSON.parse(event.data);
	// console.log(att);
	$("#imu_status").text("ON");
	$("#temp").text(Math.round(att.temp));
	$("#time").text(att.time.replace('T', ' '));
	imuStream.close();
    });

    lidarStream.onopen = function() {
	console.log("lidar connection opened");
        $("#lidar_status").text("...");
	};

    lidarStream.onerror = function() {
      console.log("lidar connection error");
      $("#msg").html("&nbsp;");
      $("#lidar_status").text("OFF");
    };

    lidarStream.addEventListener("lidar", function(event) {
        // console.log(event);
	var lidar = JSON.parse(event.data);
	// console.log(lidar);
	$("#lidar_status").text("ON");
	lidarStream.close();
    });

    lpcmStream.onopen = function() {
	console.log("lpcm connection opened");
        $("#lpcm_status").text("...");
	};

    lpcmStream.onerror = function() {
      console.log("lpcm connection error");
      $("#msg").html("&nbsp;");
      $("#lpcm_status").text("OFF");
    };

    lpcmStream.addEventListener("lpcm", function(event) {
        // console.log(event);
	var lpcm = JSON.parse(event.data);
	// console.log(lpcm);
	$("#lpcm_status").text("ON");
	lpcmStream.close();
    });

    sysStream.onopen = function() {
	console.log("sys connection opened");
        $("#used").text("...");
	};

    sysStream.onerror = function() {
      console.log("sys connection error");
      $("#msg").html("&nbsp;");
      $("#used").text("...");
    };

    sysStream.addEventListener("sys", function(event) {
        // console.log(event);
	var sys = JSON.parse(event.data);
	// console.log(lpcm);
	$("#used").text(sys.used_percent);
	$("#sw_version").text(sys.sw_version);
	sysStream.close();
    });

  $("#msg").html("&nbsp;");
}
