myChart = null;

function plot_data(chartname, result, windowsize) {

  // Find an average reading over the window to normallize the data
  avgresult = [];
  halfwindow = windowsize / 2;
  for (let i = 0; i < result.length; i++) {
    msum = 0;
    mcnt = 0;
    j = i;
    while (j >= 0 && Math.abs(result[i].mileage - result[j].mileage) < halfwindow) {
      msum += result[j].acc_z;
      mcnt += 1;
      j -= 1;
    }
    j = i + 1;
    while ( j < result.length && Math.abs(result[i].mileage - result[j].mileage) < halfwindow) {
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
