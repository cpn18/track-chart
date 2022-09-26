myChart = null;

function plot_data(chartname, result) {
  let windowsize = 0.01; // miles

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
  console.log("noisefloor =", index, "of", bins.length);

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

  // Plot the chart
  const ctx = document.getElementById(chartname).getContext('2d');
  if (myChart != null) {
	  myChart.destroy()
  }
  myChart = new Chart(ctx, {
    type: 'scatter',
    data: data,
  })
}
