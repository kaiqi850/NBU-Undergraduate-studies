<template>
  <div class="container">
    <div class="chart">
      <div ref="echarts" class="echarts"></div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import * as echarts from 'echarts'

export default {
  name: 'AverageTemp',
  data() {
    return {
      chartData: []
    }
  },
  mounted() {
    this.getSensorData()
  },
  methods: {
    async getSensorData() {
      try {
        const response = await axios.get('sensors_data')
        if (response.data.code === 0) {
          this.chartData = response.data.data
          this.initChart()
        } else {
          console.log('Error fetching data from server')
        }
      } catch (error) {
        console.log('Error fetching data from server')
      }
    },
    initChart() {
  const myChart = echarts.init(this.$refs.echarts)

  // 设置图表的配置项和数据
  const option = {
    title: {
      text: '近10分钟平均温湿度',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const name = params[0].name;
        const temp = params[0].value;
        const humi = params[1].value;
        return `${name} <br />温度：${temp}°C<br />湿度：${humi}%`
      },
      axisPointer: {
        animation: false
      }
    },
    xAxis: {
      type: 'category',
      data: this.chartData.map(sensor => sensor.sensor_id)
    },
    yAxis: [
      {
        type: 'value',
        name: '温度/°C',
        min: function(value) {
          return Math.floor(value.min - 5)
        },
        max: function(value) {
          return Math.ceil(value.max + 5)
        },
        axisLine: {
          lineStyle: {
            color: '#675Bba'
          }
        }
      },
      {
        type: 'value',
        name: '湿度/%',
        min: function(value) {
          return Math.floor(value.min - 5)
        },
        max: function(value) {
          return Math.ceil(value.max + 5)
        },
        axisLine: {
          lineStyle: {
            color: '#188df0'
          }
        }
      }
    ],
    series: [
      {
        data: this.chartData.map(sensor => sensor.avg_temperature),
        type: 'line',
        name: '温度',
        yAxisIndex: 0,
        itemStyle: {
          color: '#675Bba'
        }
      },
      {
        data: this.chartData.map(sensor => sensor.avg_humidity),
        type: 'line',
        name: '湿度',
        yAxisIndex: 1,
        itemStyle: {
          color: '#188df0'
        }
      }
    ]
  }

  // 使用刚指定的配置项和数据显示图表
  myChart.setOption(option)
}

  }
}
</script>

<style>
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

.chart {
  width: 80%;
  height: 80%;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
  border-radius: 10px;
}

.echarts {
  width: 100%;
  height: 100%;
}
</style>
