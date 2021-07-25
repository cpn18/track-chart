function lpcm_stream()
{
  const lpcmStream = new EventSource("/lpcm-stream");
  console.log(lpcmStream.readyState);
  console.log(lpcmStream.url);

  lpcmStream.onopen = function() {
    console.log("lpcm connection opened");
    document.getElementById('msg').innerHTML = "&nbsp;";
    document.getElementById('lpcm_status').innerText = "...";
  };

  lpcmStream.onerror = function() {
    console.log("lpcm connection error");
    document.getElementById('msg').innerHTML = "&#x274C;Connection Error";
    document.getElementById('lpcm_status').innerText = "OFF";
  };

  lpcmStream.addEventListener("lpcm", function(event) {
    var lpcm = JSON.parse(event.data)
    document.getElementById('lpcm_status').innerText = "ON";
  });
}
