<template>
  <div>
    <h2 class="text-center text-xl font-semibold mb-4">历史趋势图——温度</h2>
    <canvas ref="forecastChart"></canvas>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue';
import {
  Chart,
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  Title,
  CategoryScale,
  Tooltip,
  Legend
} from 'chart.js';
import axios from 'axios'; // 引入axios

Chart.register(
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Title,
  Tooltip,
  Legend
);

export default {
  name: 'ForecastChart',
  props: {
    chartData: {
      type: Array,
      required: true
    }
  },
  setup(props) {
    const forecastChart = ref(null);
    let chartInstance = null;

    // 定义API请求函数
    const fetchData = async () => {
      try {
        const response = await axios.get('https://api.example.com/temperature'); // 替换为实际API地址
        const data = response.data; // 假设API返回的数据格式为[[时间, 温度], ...]
        props.chartData = data; // 将数据传递给chartData prop
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    const renderChart = () => {
      const labels = props.chartData.map(item => item[0]); // 第一列作为X轴（时间）
      const dataPoints = props.chartData.map(item => item[1]); // 第二列作为Y轴（例如湿度）

      if (chartInstance) {
        chartInstance.destroy();
      }

      chartInstance = new Chart(forecastChart.value, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [
            {
              label: '温度数据',
              data: dataPoints,
              borderColor: 'rgba(255, 99, 132, 1)',
              backgroundColor: 'rgba(255, 99, 132, 0.2)',
              fill: true,
              tension: 0.4
            }
          ]
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: 'top'
            },
            title: {
              display: false,
              text: '历史趋势图——温度'
            }
          }
        }
      });
    };

    onMounted(() => {
      fetchData(); // 在组件挂载时调用API
      renderChart();
    });

    watch(
      () => props.chartData,
      () => {
        renderChart();
      },
      { deep: true }
    );

    return {
      forecastChart
    };
  }
};
</script>

<style scoped>
canvas {
  max-width: 100%;
  height: 400px;
}
</style>