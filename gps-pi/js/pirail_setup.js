function setup()
{
  $.ajax({
    datatype: "json",
    url: "/setup?x="+$('#xaxis').val()+"&y="+$('#yaxis').val()+"&z="+$('#zaxis').val(),
    success: function(data) {
      var obj = JSON.parse(data);
      $('#msg').text(obj.message);
    }
  });
}
