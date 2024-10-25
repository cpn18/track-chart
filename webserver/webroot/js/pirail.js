myChart = null;

function plot_data(chartname, result, windowsize, field) {

  // Find an average reading over the window to normallize the data
  avgresult = [];
  halfwindow = windowsize / 2;
  for (let i = 0; i < result.length; i++) {
    msum = 0;
    mcnt = 0;
    j = i;
    while (j >= 0 && Math.abs(result[i].mileage - result[j].mileage) < halfwindow) {
      msum += result[j][field];
      mcnt += 1;
      j -= 1;
    }
    j = i + 1;
    while ( j < result.length && Math.abs(result[i].mileage - result[j].mileage) < halfwindow) {
      msum += result[j][field];
      mcnt += 1;
      j += 1;
    }
    avgresult.push(msum/mcnt);
  }

  // calculate the noisefloor
  bins = [];
  for (let i = 0; i < result.length; i++) {
    thispoint = Math.abs(result[i][field] - avgresult[i])
    bins.push(thispoint);
  }

  bins.sort(function(a,b){return a-b;});
  index = Math.floor(
    parseFloat(document.getElementById('percentile').value) * bins.length);
  noisefloor = bins[index];
  console.log("noisefloor =", index, "of", bins.length, "value=", noisefloor);

  // convert the JSON to arrays for JChart
  values = [];
  allvalues = [];

  // only plot above the noise floor
  for (let i = 0; i < result.length; i++) {
    thispoint = Math.abs(result[i][field] - avgresult[i])
    if (thispoint > noisefloor) {
      values.push({x: result[i].mileage, y: result[i][field]});
    }
    allvalues.push({x: result[i].mileage, y: result[i][field]});
  }

  // Calculate the average acc_z using a sliding window
  avalues = [];
  for (let i = 0; i < allvalues.length; i++) {
    msum = 0;
    mcnt = 0;
    j = i;
    while ( j >= 0 && Math.abs(allvalues[i]['x'] - allvalues[j]['x']) < halfwindow ) {
      msum += allvalues[j]['y'];
      mcnt += 1;
      j -= 1;
    }
    j = i + 1;
    while ( j < allvalues.length && Math.abs(allvalues[i]['x'] - allvalues[j]['x']) < halfwindow) {
      msum += allvalues[j]['y'];
      mcnt += 1;
      j += 1;
    }
    avalues.push({x: allvalues[i]['x'], y: msum/mcnt});
  }


  // Setup JChart Data
  const data = {
    datasets: [{
      label: field.toUpperCase(),
      backgroundColor: "rgba(220,0,0,1.0)",
      data: values,
    }, {
      label: "AVG_"+field.toUpperCase(),
      backgroundColor: "#9a7b4f",  // Tortilla
      data: avalues,
    }]
  };

  // Options
  const options = {
    //maintainAspectRatio: false,
    //bezierCurve : false,
    //events: [],
    plugins: {
      zoom: {
        pan: {
          enabled: true,
        },
        zoom: {
          mode:'x',
          wheel: {
            enabled: true,
            speed: 0.2,
          },
          pinch: { // Help to zoom in mobile
            enabled: true
          }
        }
      }
    }
  }

  // Plot the chart
  const ctx = document.getElementById(chartname).getContext('2d');
  if (myChart != null) {
	  myChart.destroy()
  }
  myChart = new Chart(ctx, {
    type: 'scatter',
    data: data,
    options: options,
  })
}

function acc_z_stats(data, textStatus, jqXHR) {
  let unit = " m/s<sup>2</sup>";
  console.log(data);
  document.getElementById('min_acc_z').innerHTML = data.acc_z.min.acc_z.toFixed(4) + unit;
  document.getElementById('min_acc_z_mile').innerHTML = data.acc_z.min.mileage.toFixed(2);
  document.getElementById('avg_acc_z').innerHTML = data.acc_z.avg.toFixed(4) + unit;
  document.getElementById('max_acc_z').innerHTML = data.acc_z.max.acc_z.toFixed(4) + unit;
  document.getElementById('max_acc_z_mile').innerHTML = data.acc_z.max.mileage.toFixed(2);
  document.getElementById('median_acc_z').innerHTML = data.acc_z.median.acc_z.toFixed(4) + unit;
  document.getElementById('median_acc_z_mile').innerHTML = data.acc_z.median.mileage.toFixed(2);
  document.getElementById('stddev_acc_z').innerHTML = data.acc_z.stddev.toFixed(4) + unit;
  document.getElementById('nf_label').innerHTML = "NoiseFloor("+document.getElementById('stddev').value + "&sigma;)";
  document.getElementById('nf_acc_z').innerHTML = "&plusmn;" + data.acc_z.noise_floor.toFixed(4) + unit;
}

function plot_acoustic_data(chartname, result, windowsize) {

  // convert the JSON to arrays for JChart
  left_values = [];
  right_values = [];
  
  // populate left values
  for (let i = 0; i < result[0].left.length; i++) {
    left_values.push({x: result[0].left_ts[i], y: result[0].left[i]})
  }
  //console.log("left populated");

  // populate right values
  for (let i = 0; i < result[0].right.length ; i++) {
    right_values.push({x: result[0].right_ts[i], y: result[0].right[i]})
  }

  // Setup JChart Data
  const data = {
    datasets: [{
      label: "left",
      backgroundColor: "rgba(0,0,220)",
      data: left_values,
    }, {
      label: "right",
      backgroundColor: "rgba(220,0,0)",
      data: right_values,
    }]
  };

  // Options
  const options = {
    //maintainAspectRatio: false,
    //bezierCurve : false,
    //events: [],
    plugins: {
      zoom: {
        pan: {
          enabled: true,
        },
        zoom: {
          mode:'x',
          wheel: {
            enabled: true,
            speed: 0.2,
          },
          pinch: { // Help to zoom in mobile
            enabled: true
          }
        }
      }
    }
  }

  // Plot the chart
  const ctx = document.getElementById(chartname).getContext('2d');
  if (myChart != null) {
	  myChart.destroy()
  }
  myChart = new Chart(ctx, {
    type: 'scatter',
    data: data,
    options: options,
  })
}

function time_to_mileage(timescale, ts) {
	m = timescale[0].m
	i = 0
	while (i < timescale.length && timescale[i].t < ts) {
		m = timescale[i].m
		i += 1
	}
	if (i >= 1 && i < timescale.length) {
		m = timescale[i].m + (timescale[i].m - timescale[i-1].m) * (ts - timescale[i-1].t) / (timescale[i].t - timescale[i-1].t)
	}
	//console.log(i, ts)
	return m
}

function plot_both_data(chartname, lpcm_result, imu_result, by_mileage) {

  // convert the JSON to arrays for JChart
  console.log("LPCM", lpcm_result.length)
  console.log("IMU", imu_result.length)

  if (imu_result.length == 0 || lpcm_result.length == 0) {
	  alert("No data")
	  return
  }

  // populate imu values
  imu_values = [];
  timescale = [];

  // first timestamp value
  lpcmstart = lpcm_result[0].time;
  base = Date.parse(lpcmstart);

  // Loop through IMU data
  for (let i = 0; i < imu_result.length; i++) {
    if (imu_result[i].time >= lpcmstart) {
      var date = (Date.parse(imu_result[i].time) - base) / 1000.0;
      if (date >= 60){
        break;
      }
      thispoint = imu_result[i].acc_z;
      xval = date;
      if (by_mileage) {
        xval = imu_result[i].mileage;
      }
      imu_values.push({x: xval, y: thispoint})
      timescale.push({t: date, m: imu_result[i].mileage})
    }
  }
  
  // populate left values
  left_values = [];
  for (let i = 0; i < lpcm_result[0].left.length; i++) {
    xval = lpcm_result[0].left_ts[i]
    if (by_mileage) {
      xval = time_to_mileage(timescale, xval)
    }
    left_values.push({x: xval, y: lpcm_result[0].left[i]})
  }

  // populate right values
  right_values = [];
  for (let i = 0; i < lpcm_result[0].right.length ; i++) {
    xval = lpcm_result[0].right_ts[i]
    if (by_mileage) {
      xval = time_to_mileage(timescale, xval)
    }
    right_values.push({x: xval, y: lpcm_result[0].right[i]})
  }

  // Setup JChart Data
  // prior to 2023, LPCM data was collected backwards
  const data = {
    datasets: [{
      label: "Right",
      backgroundColor: "rgba(0,0,220)",
      data: left_values,
	    yAxisID: 'y',
    }, {
      label: "Left",
      backgroundColor: "rgba(220,0,0)",
      data: right_values,
	    yAxisID: 'y',
    }, {
      label: "ACCz",
      backgroundColor: "rgba(0,220,0)",
      data: imu_values,
	    yAxisID: 'y2',
    }]
  };

  // Options
  const options = {
    //maintainAspectRatio: false,
    //bezierCurve : false,
    //events: [],
    plugins: {
      zoom: {
        pan: {
          enabled: true,
        },
        zoom: {
          mode:'x',
          wheel: {
            enabled: true,
            speed: 0.2,
          },
          pinch: { // Help to zoom in mobile
            enabled: true
          }
        }
      }
    },
	  scales: {
		  y: {
			  type: "linear",
			  position: "left",
		  },
		  y2: {
			  type: "linear",
			  position: "right",
		  },
	  }
  }

  // Plot the chart
  const ctx = document.getElementById(chartname).getContext('2d');
  if (myChart != null) {
	  myChart.destroy()
  }
  myChart = new Chart(ctx, {
    type: 'scatter',
    data: data,
    options: options,
  })
}
