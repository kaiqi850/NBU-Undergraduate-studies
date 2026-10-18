<template>
  <div class="temperature-chart">
    <chartist :data="chartData" :options="chartOptions" :type="'Line'" />
  </div>
</template>

<script>

import Chartist from "chartist";

export default {
  name:'Tempchart',
  data() {
    return {
      chartData: {
        labels: [],
        series: [[]],
      },
      chartOptions: {
        showPoint: true,
        lineSmooth: false,
        axisY: {
          type: Chartist.FixedScaleAxis,
          low: 0,
          high: 100, // 你的温度阈值上限
          ticks: [0, 20, 40, 60, 80, 100],
        },
      },
    };
  },
  methods: {
    updateChartData(newTemperature) {
      const currentTime = new Date().toLocaleTimeString();
      this.chartData.labels.push(currentTime);
      this.chartData.series[0].push(newTemperature);

      // 只保留最新的 N 个数据点，以防止图表过大
      const maxDataPoints = 10;
      if (this.chartData.labels.length > maxDataPoints) {
        this.chartData.labels.shift();
        this.chartData.series[0].shift();
      }
    },
  },
  watch: {
    // 监听温度数据的变化，并更新图表数据
    temperature(newTemperature) {
      alert(newTemperature);
      this.updateChartData(newTemperature);
      this.$nextTick(() => {
        this.$data._chart.update();
      });
    },
  },
  mounted() {
    // 初始化图表
    const options = {
      showPoint: true,
      lineSmooth: false,
      axisY: {
        type: Chartist.FixedScaleAxis,
        low: 0,
        high: 100, // 你的温度阈值上限
        ticks: [0, 20, 40, 60, 80, 100],
      },
    };

    this.$data._chart = new Chartist.Line(
      this.$el.querySelector(".ct-chart"),
      this.chartData,
      options
    );
  },
};
</script>

<style scoped>
.temperature-chart {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}
</style>
