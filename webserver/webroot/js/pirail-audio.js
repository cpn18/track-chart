myChart = null;

function plot_data(chartname, result, windowsize) {

  // Find an average reading over the window to normallize the data
  // TODO: This only works with data sorted low-to-high
  avgresult = []
  for (let i = 0; i < result.length; i++) {
    mlow = result[i].mileage - windowsize/2;
    mhigh = result[i].mileage + windowsize/2;
    msum = 0;
    mcnt = 0;
    j = i;
    while ( j >= 0 && result[j].mileage >= mlow ) {
      msum += result[j].acc_z;
      mcnt += 1;
      j -= 1;
    }
    j = i + 1;
    while ( j < result.length && result[j].mileage <= mhigh) {
      msum += result[j].acc_z;
      mcnt += 1;
      j += 1;
    }
    avgresult.push(msum/mcnt);
  }

  // calculate the noisefloor
  bins = [];
  for (let i = 0; i < result.length; i++) {
    thispoint = Math.abs(result[i].acc_z - avgresult[i])
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
    thispoint = Math.abs(result[i].acc_z - avgresult[i])
    if (thispoint > noisefloor) {
      values.push({x: result[i].mileage, y: result[i].acc_z});
    }
    allvalues.push({x: result[i].mileage, y: result[i].acc_z});
  }

  // Calculate the average acc_z using a sliding window
  avalues = [];
  for (let i = 0; i < allvalues.length; i++) {
    mlow = allvalues[i]['x'] - windowsize/2;
    mhigh = allvalues[i]['x'] + windowsize/2;
    msum = 0;
    mcnt = 0;
    j = i;
    while ( j >= 0 && allvalues[j]['x'] >= mlow ) {
      msum += allvalues[j]['y'];
      mcnt += 1;
      j -= 1;
    }
    j = i + 1;
    while ( j < allvalues.length && allvalues[j]['x'] <= mhigh) {
      msum += allvalues[j]['y'];
      mcnt += 1;
      j += 1;
    }
    avalues.push({x: allvalues[i]['x'], y: msum/mcnt});
  }


  // Setup JChart Data
  const data = {
    datasets: [{
      label: "ACC_Z",
      data: values,
    }, {
      label: "AVG_Z",
      backgroundColor: "rgba(220,0,0)",
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
  document.getElementById('nf_label').innerHTML = "NoiseFloor("+document.getElementById('percentile').value*100+"%)";
  document.getElementById('nf_acc_z').innerHTML = "&plusmn;" + data.acc_z.noise_floor.toFixed(4) + unit;
}

function plot_acoustic_data(chartname, result, windowsize) {

  // convert the JSON to arrays for JChart
  left_values = [];
  right_values = [];

  // populate left values
  for (let i = 0; i < result[0].left.length; i++) {
    left_values.push({x: result[0].ts[i], y: result[0].left[i]})
  }

  // populate right values
  for (let i = 0; i < result[0].right.length; i++) {
    right_values.push({x: result[0].ts[i], y: result[0].right[i]})
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
