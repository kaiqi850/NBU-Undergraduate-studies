<template>
  <div class="temp-statistics">
    <div class="chart-container">
      <div ref="chart" class="chart"></div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import * as echarts from 'echarts'

export default {
  name: 'TempStatistics',
  data() {
    return {
      chartOptions: {
        title: {
          text: '五个区域最高温度与最低温度统计',
          subtext: '近10分钟内',
        },
        legend: {
          data: ['最高温度', '最低温度'],
        },
        tooltip: {
          trigger: 'axis',
        },
        xAxis: {
          type: 'category',
          data: ['区域1', '区域2', '区域3', '区域4', '区域5'],
        },
        yAxis: {
          type: 'value',
        },
        series: [
          {
            name: '最高温度',
            type: 'bar',
            barWidth: 40,
            data: [0, 0, 0, 0, 0],
          },
          {
            name: '最低温度',
            type: 'bar',
            barWidth: 40,
            data: [0, 0, 0, 0, 0],
          },
        ],
      },
    }
  },

  mounted() {
    this.fetchData()
  },

  methods: {
    async fetchData() {
      try {
        const response = await axios.get('/temperature_statistics')
        if (response.data.code === 0) {
          const { data } = response.data
          this.updateChartData(data)
        } else {
          console.log('Failed to fetch data')
        }
      } catch (error) {
        console.log('Failed to fetch data', error)
      }
    },

    updateChartData(data) {
      const { maxTemps, minTemps } = data
      this.chartOptions.series[0].data = maxTemps
      this.chartOptions.series[1].data = minTemps
      this.$nextTick(() => {
        const chart = echarts.init(this.$refs.chart)
        chart.setOption(this.chartOptions)
      })
    },
  },
}
</script>

<style scoped>
.temp-statistics {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.chart-container {
  width: 80%;
  height: 80%;
}

.chart {
  width: 100%;
  height: 100%;
}
</style>
