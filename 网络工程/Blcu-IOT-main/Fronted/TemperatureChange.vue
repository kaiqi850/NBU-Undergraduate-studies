<template>
  <div class="temperature-change">
    <div class="chart-container">
      <div ref="chart" class="chart"></div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import * as echarts from 'echarts'

export default {
  name: 'TemperatureChange',
  data() {
    return {
      chartOptions: {
        title: {
          text: '历史温度变化',
          subtext: '最近一天内各传感器温度变化',
        },
        tooltip: {
          trigger: 'axis',
          formatter: (params) => {
            const time = params[0].name
            const values = params
              .slice(1)
              .map((item) => `${item.seriesName}: ${item.value}°C`)
              .join('<br/>')
            return `${time}<br/>${values}`
          },
        },
        legend: {
          data: [],
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: [],
        },
        yAxis: {
          type: 'value',
        },
        series: [],
      },
    }
  },

  mounted() {
    this.fetchData()
  },

  methods: {
    async fetchData() {
      try {
        const response = await axios.get('/temperature_change')
        if (response.data.code === 0) {
          const { data } = response.data
          const chartData = this.formatData(data)
          this.renderChart(chartData)
        } else {
          console.log('Failed to fetch data')
        }
      } catch (error) {
        console.log('Failed to fetch data', error)
      }
    },

    formatData(data) {
      const sensors = Object.keys(data)
      const hours = [...new Array(24)].map((_, index) => {
        const hour = index.toString().padStart(2, '0')
        return `${hour}:00`
      })
      const chartData = sensors.map((sensor) => {
        const temperatures = data[sensor].temperatures
        const formattedTemperatures = []
        for (let i = 0; i < temperatures.length; i += 60) {
          const hourData = temperatures.slice(i, i + 60)
          const averageTemp = (
            hourData.reduce((total, t) => total + t) / hourData.length
          ).toFixed(1)
          formattedTemperatures.push(averageTemp)
        }
        return {
          name: sensor.replace('Sensor', '传感器'), // 将 "Sensor" 替换为 "传感器"
          data: formattedTemperatures,
        }
      })
      return { hours, chartData }
    },

    renderChart(chartData) {
      const { hours, chartData: seriesData } = chartData
      const legendData = []
      const series = seriesData.map((item) => {
        legendData.push(item.name)
        return {
          name: item.name,
          type: 'line',
          data: item.data,
        }
      })
      this.chartOptions.legend.data = legendData
      this.chartOptions.xAxis.data = hours
      this.chartOptions.series = series
      this.$nextTick(() => {
        const chart = echarts.init(this.$refs.chart)
        chart.setOption(this.chartOptions)
      })
    },
  },
}
</script>

<style scoped>
.temperature-change {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.chart-container {
  width: 80%;
  height: 80%;
  margin: 0 auto;
}

.chart {
  width: 100%;
  height: 100%;
}

@media screen and (max-width: 768px) {
  .chart-container {
    width: 100%;
    height: 400px;
  }
}
</style>