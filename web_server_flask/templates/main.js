
// data
const ctx = document.getElementById('myChart').getContext('2d'); //greater than min and less then max
const myChart = new Chart(ctx, {
    type: 'scatter',
    data: {
        labels: [],
        datasets: [{
            label: 'acc_Z', // label of the chart
            data: [],
            backgroundColor: 'transparent',
            borderColor: 'blue',
            borderWidth: 1,
            //pointRadius: 0,
            pointHoverRadius: 0,
        }]
    },
    options: {
        //maintainAspectRatio: false,
        //bezierCurve : false,
        events: [],
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
});

let saveData = []

// filter
function upDateChart(minRange, maxRange){
    var filterData = saveData.filter(item => item.mileage != undefined && item.acc_z != undefined)//.sort((a, b) => a.mileage - b.mileage)
    if (maxRange != null && minRange != null){
        filterData = filterData.filter(item => item.mileage > minRange && item.mileage < maxRange)
    }

    myChart.data.labels = filterData.map(item => item.mileage);
    myChart.data.datasets.forEach((dataset) => {
        dataset.data = filterData.map(item => item.acc_z);
    });
    myChart.update();
}

fetch('http://www.newenglandsouthernrailroad.com/pirail/data/plrr_20210919_northbound.json')
  .then(response => response.text())
  .then(data =>{
    let x = data.trim().split("\n").map(x => {
        return JSON.parse(x)
    })
    saveData = x
    upDateChart(null, null);


    // reset button
    function resetZoomChart() {
        myChart.resetZoom();
        upDateChart(null, null);
        document.getElementById("rangeFrom").reset();
    }
    document.getElementById("reset").addEventListener("click", resetZoomChart)

    // Submit button
    document.addEventListener('submit', function (event) {
        event.preventDefault();
        var form = document.querySelector('#rangeFrom');
        var data = new FormData(form);
        upDateChart(data.get("minRange"), data.get("maxRange"));
    })
  });