<template>
  <div>
    <div ref="chart" style="width: 100%; height: 400px;"></div>
  </div>
</template>

<script>
import * as echarts from "echarts";

export default {
  data() {
    return {
      chartInstance: null,
      chartData: [], // 存储从后端获取的温度数据
    };
  },
  mounted() {
    this.initChart();
    this.fetchData();
  },
  methods: {
    // 初始化图表
    initChart() {
      this.chartInstance = echarts.init(this.$refs.chart);
    },
    // 更新图表数据
    updateChart() {
      const options = {
        title: { text: "历史趋势图 - 温度" },
        tooltip: { trigger: "axis" },
        xAxis: {
          type: "category",
          data: this.chartData.map((item) => item.time), // 时间轴
        },
        yAxis: { type: "value" },
        series: [
          {
            name: "温度",
            type: "line",
            data: this.chartData.map((item) => item.temperature), // 温度数据
          },
        ],
      };
      this.chartInstance.setOption(options);
    },
    // 从后端获取数据
    async fetchData() {
      try {
        const response = await fetch("/realities/data");
        const data = await response.json();
        this.chartData = data; // 赋值后端返回的数据
        this.updateChart(); // 更新图表
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    },
  },
};
</script>


  <style scoped>
  canvas {
    max-width: 100%;
    height: 400px;
  }
  </style>
  