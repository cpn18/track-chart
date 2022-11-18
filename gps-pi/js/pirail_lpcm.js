function lpcm_stream()
{
  const lpcmStream = new EventSource("/lpcm-stream");
  console.log(lpcmStream.readyState);
  console.log(lpcmStream.url);

  lpcmStream.onopen = function() {
    console.log("lpcm connection opened");
    $("#msg").html("&nbsp;");
    $("#lpcm_status").text("...");
  };

  lpcmStream.onerror = function() {
    console.log("lpcm connection error");
    $("#msg").html("&#x274C;Connection Error");
    $("#lpcm_status").text("OFF");
  };

  lpcmStream.addEventListener("lpcm", function(event) {
    var lpcm = JSON.parse(event.data)
    $("#lpcm_status").text("ON");
  });
}
