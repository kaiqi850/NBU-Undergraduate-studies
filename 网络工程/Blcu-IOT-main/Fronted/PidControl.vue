<template>
    <div class="pid-control">
      <div class="data-display">
        <div class="temperature">
          <div class="current-temperature">
            <i class="fas fa-thermometer-half"></i>
            <span class="temperature-value">{{ currentTemperature }}</span>
            <sup>℃</sup>
          </div>
          <div class="temperature-difference">
            <span class="label">温度差：</span>
            <span :class="temperatureDifferenceClass">{{ temperatureDifference }}</span>
            <sup>℃</sup>
          </div>
        </div>
        <div class="target-temperature">
          <label for="target-temp-input">目标温度：</label>
          <input id="target-temp-input" type="number" v-model="targetTemperature" />
          <sup>℃</sup>
        </div>
        <div class="control-status">
          <span class="label">调节状态：</span>
          <el-switch v-model="isAutoControl" active-color="#13ce66" inactive-color="#ff4949"></el-switch>
        </div>
      </div>
  
      <div class="control-buttons">
        <el-button type="primary" icon="el-icon-play" :disabled="isAutoControl" @click="startAutoControl">
          启动自动调节
        </el-button>
        <el-button type="danger" icon="el-icon-stop" :disabled="!isAutoControl" @click="stopAutoControl">
          停止自动调节
        </el-button>
      </div>
  
      <div class="chart-display">
        <div ref="chart" class="chart"></div>
      </div>
    </div>
  </template>
  
<script>
import axios from 'axios';
import * as echarts from 'echarts'

export default {
  name: 'PIDControl',
  data() {
    return {
      currentTemp: 0,
      targetTemp: 0,
      isAuto: false,
      tempChart: null,
      tempOption: {
        title: {
          text: '温度变化趋势',
        },
        tooltip: {
          trigger: 'axis',
        },
        xAxis: {
          type: 'category',
          data: [],
        },
        yAxis: {
          type: 'value',
          min: 0,
          max: 50,
        },
        series: [
          {
            name: '当前温度',
            type: 'line',
            data: [],
          },
          {
            name: '目标温度',
            type: 'line',
            data: [],
          },
        ],
      },
    }
  },
  methods: {
    startAuto() {
      axios.post('/api/pid-control/start', {
        targetTemperature: this.targetTemp,
      }).then(res => {
        this.isAuto = true
        this.updateTempChart()
        this.updateTempInterval = setInterval(() => {
          this.updateTempChart()
        }, 5000)
      }).catch(err => {
        console.error(err)
        this.$message.error('自动调节启动失败')
      })
    },
    stopAuto() {
      axios.post('/api/pid-control/stop').then(res => {
        this.isAuto = false
        clearInterval(this.updateTempInterval)
      }).catch(err => {
        console.error(err)
        this.$message.error('自动调节停止失败')
      })
    },
    updateTempChart() {
      axios.get('/api/pid-control/temp').then(res => {
        const timestamp = Date.now()
        const currentTemp = res.data.currentTemp
        const targetTemp = res.data.targetTemp
        this.currentTemp = currentTemp
        this.tempOption.xAxis.data.push(timestamp)
        this.tempOption.series[0].data.push(currentTemp)
        this.tempOption.series[1].data.push(targetTemp)
        this.$nextTick(() => {
          this.tempChart.setOption(this.tempOption)
        })
      }).catch(err => {
        console.error(err)
        this.$message.error('温度获取失败')
      })
    },
  },
  mounted() {
    this.tempChart = echarts.init(this.$refs.chart)
    this.updateTempChart()
  },
  beforeDestroy() {
    clearInterval(this.updateTempInterval)
  },
}
</script>


<style scoped>
.pid-control {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.data-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

.temperature {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.current-temperature {
  font-size: 4em;
  display: flex;
  align-items: center;
}

.temperature-difference {
  font-size: 1.2em;
  color: #666;
  margin-left: 10px;
}

.temperature-difference .label {
  color: #999;
}

.target-temperature {
  font-size: 1.5em;
  margin-bottom: 10px;
}

.control-status {
  font-size: 1.2em;
  margin-bottom: 10px;
}

.control-buttons {
  margin-bottom: 20px;
}

.chart-display {
  width: 80%;
  height: 400px;
}
</style>
