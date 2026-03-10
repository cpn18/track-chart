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

function AxesChart({ att }) {
    ChartJS.register(
        CategoryScale,
        LinearScale,
        PointElement,
        LineElement,
        Title,
        Tooltip
    );

    const pitch_options = {
    responsive: true,
    plugins: {
        title: {
            display: true,
            text: 'Pitch',
        },
    },
    };

    const roll_options = {
    responsive: true,
    plugins: {
        
        title: {
            display: true,
            text: 'Roll',
        },
    },
    };

    const yaw_options = {
    responsive: true,
    plugins: {
        
        title: {
            display: true,
            text: 'Yaw',
        },
    },
    };

    const labels = att.time;

    const pitch = {
    labels: Array.from(labels),
    datasets: [
        {
        label: 'Pitch',
        data: Array.from(att.pitch),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        },
    ],
    };

    const roll = {
    labels: Array.from(labels),
    datasets: [
        {
        label: 'Roll',
        data: Array.from(att.roll),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(99, 255, 132, 0.5)',
        },
    ],
    };

    const yaw = {
    labels: Array.from(labels),
    datasets: [
        {
        label: 'Yaw',
        data: Array.from(att.yaw),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(99, 132, 255, 0.5)',
        },
    ],
    };


    return(
        <div>
            <Line options={pitch_options} data={pitch} height={"100%"} />
            <Line options={roll_options} data={roll} height={"100%"} />
            <Line options={yaw_options} data={yaw} height={"100%"} />
        </div>
    )
}

export default AxesChart;