<template>
    <div class="temperature-adjustment">
      <h2 class="title">传感器温度调节</h2>
      <div class="sensor-list">
        <div class="sensor" v-for="(sensor, index) in sensors" :key="index">
          <h3 class="sensor-name">传感器 {{ index + 1 }}</h3>
          <div class="sensor-info">
            <div class="current-temperature">
              <span>当前温度：</span>
              <span class="temperature-value">{{ sensor.currentTemperature }}℃</span>
            </div>
            <div class="adjustment">
              <span>调节温度：</span>
              <input type="range" min="0" max="100" v-model="sensor.adjustmentTemperature">
            </div>
          </div>
        </div>
      </div>
      <el-button class="submit-button" type="primary" @click="submitAdjustment">提交调节</el-button>
    </div>
  </template>
  
  <script>
  import axios from 'axios'
  
  export default {
    name: 'AdjustTemp',
  
    data() {
      return {
        sensors: [
          {
            id: 1,
            currentTemperature: 25,
            adjustmentTemperature: 25,
          },
          {
            id: 2,
            currentTemperature: 24,
            adjustmentTemperature: 24,
          },
          {
            id: 3,
            currentTemperature: 23,
            adjustmentTemperature: 23,
          },
          {
            id: 4,
            currentTemperature: 22,
            adjustmentTemperature: 22,
          },
          {
            id: 5,
            currentTemperature: 21,
            adjustmentTemperature: 21,
          },
        ],
      }
    },
  
    methods: {
      submitAdjustment() {
        // 提交调节温度的数据到后端保存
        const adjustmentData = this.sensors.map((sensor) => {
          return {
            id: sensor.id,
            origin_temp: sensor.currentTemperature,
            new_temp: sensor.adjustmentTemperature,
            update_time: new Date(),
          }
        })
        axios
          .post('temperature_adjust', adjustmentData)
          .then((response) => {
            console.log('调节温度成功！')
          })
          .catch((error) => {
            console.log('调节温度失败：', error)
          })
      },
    },
  }
  </script>
  
  <style>
  .temperature-adjustment {
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  
  .title {
    font-size: 20px;
    margin-top: 20px;
  }
  
  .sensor-list {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .sensor {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 20px;
    padding: 20px;
    border: 1px solid #ccc;
    border-radius: 5px;
    box-shadow: 0 0 10px #ccc;
  }
  
  .sensor-name {
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 10px;
  }
  
  .sensor-info {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 20px;
  }
  
  .current-temperature {
    font-size: 16px;
    margin-bottom: 10px;
  }
  
  .temperature-value {
    font-weight: bold;
  }
  
  .adjustment {
    margin-top: 10px;
  }
  
  .submit-button {
    margin-top: 20px;
  }
  </style>
  