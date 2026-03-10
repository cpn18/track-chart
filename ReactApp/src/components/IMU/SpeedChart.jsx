import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
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
    };

    const gyroYangle_options = {
    responsive: true,
    plugins: {

        title: {
            display: true,
            text: 'Gyroscopic Y angle',
        },
    },
    };

    const acc_z_options = {
    responsive: true,
    plugins: {

        title: {
            display: true,
            text: 'Z Axis Acceleration',
        },
    },
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

    const gyroYangle = {
    labels: Array.from(labels),
    datasets: [
        {
        label: 'Gyroscopic Y angle',
        data: Array.from(att.gyroYangle),
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
            <Line options={gyroYangle_options} data={gyroYangle} height={"100%"} />
            <Line options={acc_z_options} data={acc_z} height={"100%"} />
        </div>
    )
}

export default SpeedChart;