import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'; // you can find the chart.js documentation here https://www.chartjs.org/
import { Line } from 'react-chartjs-2';

function SpeedChart({ att }) {
    ChartJS.register(
        CategoryScale,
        LinearScale,
        PointElement,
        LineElement,
        Title,
        Tooltip
    );

    const speed_options = {
    responsive: true,
    plugins: {
        title: {
            display: true,
            text: 'Speed',
        },
    },
    animation: false,
    };

    const acc_x_options = {
    responsive: true,
    plugins: {

        title: {
            display: true,
            text: 'X Axis Acceleration',
        },
    },
    animation: false,
    };

    const acc_z_options = {
    responsive: true,
    plugins: {

        title: {
            display: true,
            text: 'Z Axis Acceleration',
        },
    },
    animation: false,
    };

    const labels = att.time;

    const speed = {
    labels: Array.from(labels),
    datasets: [
        {
        label: 'Speed',
        data: Array.from(att.speed),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        },
    ],
    };

    const acc_x = {
    labels: Array.from(labels),
    datasets: [
        {
        label: 'X Axis Accel',
        data: Array.from(att.acc_x),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(99, 255, 132, 0.5)',
        },
    ],
    };

    const acc_z = {
    labels: Array.from(labels),
    datasets: [
        {
        label: 'Z Axis Accel',
        data: Array.from(att.acc_z),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(99, 132, 255, 0.5)',
        },
    ],
    };


    return(
        <div>
            <Line options={speed_options} data={speed} height={"100%"} />
            <Line options={acc_x_options} data={acc_x} height={"100%"} />
            <Line options={acc_z_options} data={acc_z} height={"100%"} />
        </div>
    )
}

export default SpeedChart;
