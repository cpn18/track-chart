function displayChart (jsonfile) {
    const labels = jsonfile.jsonarray.map(function(e) {
        if (e.class == "ATT") {
            return e.time;
        }
        else {
            return
        }
    });

    const dataset_y = jsonfile.jsonarray.map(function(e) {
        if (e.class == "ATT") {
            return e.gyro_y;
        }
        else {
            return
        }
    });;

    const dataset_x = jsonfile.jsonarray.map(function(e) {
        if (e.class == "ATT") {
            return e.gyro_x;
        }
        else {
            return
        }
    });;

    const dataset_z = jsonfile.jsonarray.map(function(e) {
        if (e.class == "ATT") {
            return e.gyro_z;
        }
        else {
            return
        }
    });;

    const data = {
        labels: labels,
        datasets: [{
            label: 'X',
            backgroundColor: 'rgb(255, 0, 0)',
            borderColor: 'rgb(255, 0, 0)',
            borderWidth: 0.3,
            pointRadius: 0,
            data: dataset_x
        },
        {
            label: 'Y',
            backgroundColor: 'rgb(0, 255, 0)',
            borderColor: 'rgb(0, 255, 0)',
            borderWidth: 0.3,
            pointRadius: 0,
            data: dataset_y
        },
        {
            label: 'Z',
            backgroundColor: 'rgb(0, 0, 255)',
            borderColor: 'rgb(0, 0, 255)',
            borderWidth: 0.3,
            pointRadius: 0,
            data: dataset_z
        }
    ]
    };

    const config = {
        type: 'line',
        data: data,
        options: {
            repsonsive: true,
            maintainAspectRatio: false,
            aspectRatio: 1,
        }
    };

    const myChart = new Chart(document.getElementById('myChart'), config);
}


