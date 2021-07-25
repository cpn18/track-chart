function imu_stream() {
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
    });
}
