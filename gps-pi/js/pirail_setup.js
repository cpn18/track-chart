function setup_reset()
{
  $.ajax({
    datatype: "json",
    url: "/setup",
    success: function(obj) {
      $('#msg').text("");
      $('#gps_enable').prop('checked', obj.gps.enable);
      $('#imu_enable').prop('checked', obj.imu.enable);
      $('#imu_x').val(obj.imu.x);
      $('#imu_y').val(obj.imu.y);
      $('#imu_z').val(obj.imu.z);
      $('#lidar_enable').prop('checked', obj.lidar.enable);
      $('#lpcm_enable').prop('checked', obj.lpcm.enable);
    }
  });
}

function setup_save()
{
  formdata = {
	  gps: {
		  enable: $('#gps_enable').is(":checked")
	  },
	  imu: {
		  x: $('#imu_x').val(),
		  y: $('#imu_y').val(),
		  z: $('#imu_z').val(),
		  enable: $('#imu_enable').is(":checked")
	  },
	  lidar: {
		  enable: $('#lidar_enable').is(":checked")
	  },
	  lpcm: {
		  enable: $('#lpcm_enable').is(":checked")
	  }
  };

  $.ajax({
    type: "post",
    datatype: "json",
    data: JSON.stringify(formdata),
    url: "/setup",
    success: function(obj) {
      $('#msg').text(obj.message);
    }
  });
}