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
    const gpsStream = new EventSource("/gps-stream");
    console.log(gpsStream.readyState);
    console.log(gpsStream.url);

    const imuStream = new EventSource("/imu-stream");
    console.log(imuStream.readyState);
    console.log(imuStream.url);

    const lidarStream = new EventSource("/lidar-stream");
    console.log(lidarStream.readyState);
    console.log(lidarStream.url);

    const lpcmStream = new EventSource("/lpcm-stream");
    console.log(lpcmStream.readyState);
    console.log(lpcmStream.url);

    const sysStream = new EventSource("/sys-stream");
    console.log(sysStream.readyState);
    console.log(sysStream.url);

    gpsStream.onopen = function() {
	console.log("gps connection opened");
        document.getElementById("mode").innerText = "...";
        document.getElementById("gps_count").innerText = "";
	};

    gpsStream.onerror = function() {
      console.log("gps connection error");
        document.getElementById("msg").innerHTML = "&nbsp;";
        document.getElementById("mode").innerText = "OFF";
        document.getElementById("gps_count").innerText = "";
    };

    gpsStream.addEventListener("tpv", function(event) {
        // console.log(event);
	var tpv = JSON.parse(event.data);
        // console.log(tpv);
	document.getElementById("gpstime").innerHTML = tpv.time.replace('T', '<br>');
	document.getElementById("ept").innerText = "+/-"+tpv.ept+"s";
	document.getElementById("mode").innerText = tpv.mode + "D ";
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
	document.getElementById("gps_count").innerText = used + "/" + sky.satellites.length;
    });

    imuStream.onopen = function() {
	console.log("imu connection opened");
        document.getElementById("imu_status").innerText = "...";
	};

    imuStream.onerror = function() {
      console.log("imu connection error");
      document.getElementById("msg").innerHTML = "&nbsp;";
      document.getElementById("imu_status").innerText = "OFF";
    };

    imuStream.addEventListener("att", function(event) {
        // console.log(event);
	var att = JSON.parse(event.data);
	// console.log(att);
	document.getElementById("imu_status").innerText = "ON";
	document.getElementById("temp").innerText = Math.round(att.temp);
	document.getElementById("time").innerText = att.time.replace('T', ' ');
    });

    lidarStream.onopen = function() {
	console.log("lidar connection opened");
        document.getElementById("lidar_status").innerText = "...";
	};

    lidarStream.onerror = function() {
      console.log("lidar connection error");
      document.getElementById("msg").innerHTML = "&nbsp;";
      document.getElementById("lidar_status").innerText = "OFF";
    };

    lidarStream.addEventListener("lidar", function(event) {
        // console.log(event);
	var lidar = JSON.parse(event.data);
	// console.log(lidar);
	document.getElementById("lidar_status").innerText = "ON";
    });

    lpcmStream.onopen = function() {
	console.log("lpcm connection opened");
        document.getElementById("lpcm_status").innerText = "...";
	};

    lpcmStream.onerror = function() {
      console.log("lpcm connection error");
      document.getElementById("msg").innerHTML = "&nbsp;";
      document.getElementById("lpcm_status").innerText = "OFF";
    };

    lpcmStream.addEventListener("lpcm", function(event) {
        // console.log(event);
	var lpcm = JSON.parse(event.data);
	// console.log(lpcm);
	document.getElementById("lpcm_status").innerText = "ON";
    });

    sysStream.onopen = function() {
	console.log("sys connection opened");
        document.getElementById("used").innerText = "...";
	};

    sysStream.onerror = function() {
      console.log("sys connection error");
      document.getElementById("msg").innerHTML = "&nbsp;";
      document.getElementById("used").innerText = "...";
    };

    sysStream.addEventListener("sys", function(event) {
        // console.log(event);
	var sys = JSON.parse(event.data);
	// console.log(lpcm);
	document.getElementById("used").innerText = sys.used_percent;
    });

  document.getElementById("msg").innerHTML = "&nbsp;";
}
