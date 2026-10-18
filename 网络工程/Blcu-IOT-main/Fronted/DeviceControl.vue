<template>
    <div class="device-control">
      <h2 class="title">设备控制</h2>
      <el-row :gutter="20">
        <el-col :span="6" v-for="(device, index) in devices" :key="index">
          <el-card :body-style="{ padding: '0' }">
            <div class="device-card">
              <i :class="['el-icon', device.icon]"></i>
              <h3>{{ device.name }}</h3>
              <el-switch
                v-model="device.state"
                active-color="#13ce66"
                inactive-color="#ff4949"
                @change="toggleDevice(device)"
              ></el-switch>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        devices: [
          { name: '灯光', state: false, icon: 'el-icon-sunny', id: 'light' },
          { name: '水泵', state: false, icon: 'el-icon-video-pause', id: 'pump' },
          { name: '空调', state: false, icon: 'el-icon-turn-off', id: 'ac' },
          { name: '通风', state: false, icon: 'el-icon-refresh', id: 'vent' },
        ],
      };
    },
    methods: {
      toggleDevice(device) {
        console.log(`设备 ${device.name} 的状态：${device.state ? '开启' : '关闭'}`);
        // 在此处发送请求以切换设备状态
      },
    },
  };
  </script>
  
  <style scoped>
  .device-control {
    padding: 20px;
  }
  
  .title {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 30px;
  }
  
  .device-card {
    padding: 20px;
    text-align: center;
    font-size: 18px;
  }
  
  .device-card i {
    font-size: 50px;
    margin-bottom: 10px;
  }
  
  .device-card h3 {
    margin-bottom: 20px;
  }
  </style>
  