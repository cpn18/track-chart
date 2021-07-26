function setup()
{
  $.ajax({
    datatype: "json",
    url: "/setup?imu_x="+$('#imu_x').val()+"&imu_y="+$('#imu_y').val()+"&imu_z="+$('#imu_z').val(),
    success: function(data) {
      var obj = JSON.parse(data);
      $('#msg').text(obj.message);
    }
  });
}
