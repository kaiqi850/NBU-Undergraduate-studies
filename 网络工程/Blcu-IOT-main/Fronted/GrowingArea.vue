<!-- src/components/GrowthChart.vue -->
<template>
  <div>
    <div ref="chart" style="width: 100%; height: 400px;"></div>
  </div>
</template>

<script>
import axios from 'axios';
import * as echarts from 'echarts';

export default {
  name: 'GrowingArea',
  data() {
    return {
      chartInstance: null
    };
  },
  mounted() {
    this.getGrowthData();
  },
  methods: {
    async getGrowthData() {
      try {
        const response = await axios.get('/growing_area_data');
        if (response.data.code === 0) {
          this.createChart(response.data.data);
        } else {
          console.error('Failed to fetch growth data:', response.data.message);
        }
      } catch (error) {
        console.error('Failed to fetch growth data:', error);
      }
    },
    createChart(growthData) {
      const xAxisData = growthData.map(item => `分区${item.id}-${item.oid}`);
      const seriesData = growthData.map(item => item.number);

      this.chartInstance = echarts.init(this.$refs.chart);

      const chartOptions = {
        title: {
          text: '各分区生长状况'
        },
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: xAxisData
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '产量',
            type: 'bar',
            data: seriesData
          }
        ]
      };

      this.chartInstance.setOption(chartOptions);
    }
  },
  beforeDestroy() {
    if (this.chartInstance) {
      this.chartInstance.dispose();
    }
  }
};
</script>
