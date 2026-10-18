<template>
  <Layout>
    <PageHeader :title="title" :items="items" />
    <div class="container-fluid">
      <div v-for="device in devices" :key="device.id" class="row">
        <!-- 温度报表 -->
        <div class="col-lg-6">
          <div class="card">
            <div class="card-body">
              <h4 class="card-title mb-4">[{{ device.id }}] 温度报表</h4>
              <div class="row justify-content-center">
                <div class="col-sm-4 text-center">
                  <h5 class="mb-0 font-size-20">{{ device.maxTemperature.toFixed(2) }} ℃</h5>
                  <p class="text-muted">最高温度</p>
                </div>
                <div class="col-sm-4 text-center">
                  <h5 class="mb-0 font-size-20">{{ device.minTemperature.toFixed(2) }} ℃</h5>
                  <p class="text-muted">最低温度</p>
                </div>
                <div class="col-sm-4 text-center">
                  <h5 class="mb-0 font-size-20">{{ device.avgTemperature.toFixed(2) }} ℃</h5>
                  <p class="text-muted">平均温度</p>
                </div>
              </div>
              <TemperatureChart
                :temperatureData="device.temperatureData"
                :secondaryTemperatureData="device.secondaryTemperatureData"
                :timeStamps="device.timeStamps"
                :ids="device.id"
              />
            </div>
          </div>
        </div>
        <!-- 湿度报表 -->
        <div class="col-lg-6">
          <div class="card">
            <div class="card-body">
              <h4 class="card-title mb-4">[{{ device.id }}] 湿度报表</h4>
              <div class="row justify-content-center">
                <div class="col-sm-4 text-center">
                  <h5 class="mb-0 font-size-20">{{ device.maxHumidity.toFixed(2) }} %</h5>
                  <p class="text-muted">最高湿度</p>
                </div>
                <div class="col-sm-4 text-center">
                  <h5 class="mb-0 font-size-20">{{ device.minHumidity.toFixed(2) }} %</h5>
                  <p class="text-muted">最低湿度</p>
                </div>
                <div class="col-sm-4 text-center">
                  <h5 class="mb-0 font-size-20">{{ device.avgHumidity.toFixed(2) }} %</h5>
                  <p class="text-muted">平均湿度</p>
                </div>
              </div>
              <HumidityChart
                :humidityData="device.humidityData"
                :secondaryHumidityData="device.secondaryHumidityData"
                :timeStamps="device.timeStamps"
                :ids="device.id"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script>
import Layout from "../../layouts/main";
import PageHeader from "@/components/page-header";
import TemperatureChart from "./TemperatureChart.vue";
import HumidityChart from "./HumidityChart.vue";
import * as xlsx from "xlsx";

export default {
  components: {
    Layout,
    PageHeader,
    TemperatureChart,
    HumidityChart,
  },
  data() {
    return {
      title: "数据分析",
      items: [{ text: "仪表盘", link: "/" }, { text: "数据分析", active: true }],
      devices: [],
    };
  },
  methods: { 
    async loadData() {
  try {
    // 读取实时数据文件
    const realTimeFile = await fetch("/mqtt_data.xlsx");
    const realTimeBlob = await realTimeFile.blob();
    const realTimeWorkbook = xlsx.read(await realTimeBlob.arrayBuffer(), { type: "array" });
    const realTimeData = xlsx.utils.sheet_to_json(realTimeWorkbook.Sheets[realTimeWorkbook.SheetNames[0]]);

    // 读取全量数据文件
    const historyFile = await fetch("/predicted_data.xlsx");
    const historyBlob = await historyFile.blob();
    const historyWorkbook = xlsx.read(await historyBlob.arrayBuffer(), { type: "array" });
    const historyData = xlsx.utils.sheet_to_json(historyWorkbook.Sheets[historyWorkbook.SheetNames[0]]);

    // 按设备分组处理数据
    const groupedDevices = {};
    realTimeData.forEach((row) => {
      if (!groupedDevices[row.deviceId]) {
        groupedDevices[row.deviceId] = {
          id: row.deviceId,
          temperatureData: [],
          humidityData: [],
          secondaryTemperatureData: [],
          secondaryHumidityData: [],
          timeStamps: []
        };
      }
      groupedDevices[row.deviceId].temperatureData.push(row.Temperature || 0);
      groupedDevices[row.deviceId].humidityData.push(row.Humidity || 0);
      groupedDevices[row.deviceId].timeStamps.push(row.Timestamp || "未知");
    });

    // 获取实时数据中的最后300条数据
    Object.values(groupedDevices).forEach((device) => {
      device.temperatureData = device.temperatureData.slice(-300);
      device.humidityData = device.humidityData.slice(-300);
      device.timeStamps = device.timeStamps.slice(-300);
    });

    // 获取实时数据中的最后一个时间戳
    
    Object.values(groupedDevices).forEach((device) => {

      

      
      const lastHistoryData = historyData.slice(-60);
        const historyTimeStamps = lastHistoryData.map(row => row.Timestamp);
        
        device.secondaryTemperatureData = lastHistoryData
          .map(row => row.Temperature);
        device.secondaryHumidityData = lastHistoryData
          .map(row => row.Humidity);

      // 合并实时数据和全量数据，展示360个数据点
      const realTimeDataSubset = device.temperatureData;
      const realTimeTimeStamps = device.timeStamps;
      const realTimehumidityData = device.humidityData;
      const fullHistoryData = device.secondaryTemperatureData.slice(-60);

      const fullHistoryDataSubset = fullHistoryData.slice(0, 60);

      const fullHistoryData1 = device.secondaryHumidityData.slice(-60);
      const fullHistoryDataSubset1 = fullHistoryData1.slice(0, 60);

      // 合并实时数据和全量数据
      device.temperatureData = realTimeDataSubset.concat(device.secondaryTemperatureData);
      device.timeStamps = realTimeTimeStamps.concat(historyTimeStamps);
      device.humidityData = realTimehumidityData.concat(device.secondaryHumidityData);
      device.secondaryTemperatureData = fullHistoryDataSubset;
      device.secondaryHumidityData = fullHistoryDataSubset1;
    });

    // 计算温湿度统计值
    Object.values(groupedDevices).forEach((device) => {
      device.maxTemperature = Math.max(...device.temperatureData);
      device.minTemperature = Math.min(...device.temperatureData);
      device.avgTemperature =
        device.temperatureData.reduce((sum, val) => sum + val, 0) / device.temperatureData.length;

      device.maxHumidity = Math.max(...device.humidityData);
      device.minHumidity = Math.min(...device.humidityData);
      device.avgHumidity =
        device.humidityData.reduce((sum, val) => sum + val, 0) / device.humidityData.length;
      const deviceDataForStorage = {
        avgTemperature: device.avgTemperature,
        avgHumidity: device.avgHumidity,
        realTimeTemperature: realTimeData[realTimeData.length - 1].Temperature,
        realTimeHumidity: realTimeData[realTimeData.length - 1].Humidity
      };

      // 将数据转换为JSON字符串后存入localStorage，以设备的某个唯一标识（这里假设设备有个id属性）作为键名
      localStorage.setItem(device.id, JSON.stringify(deviceDataForStorage));
      console.log(localStorage.getItem(device.id));
    });

    // 更新设备数据
    this.devices = Object.values(groupedDevices);
  } catch (error) {
    console.error("读取Excel失败：", error);
  }
},

  updateData() {
    // 每隔7秒更新一次图表数据
    this.loadData();
    setInterval(this.loadData, 7000);
  },
},

mounted() {
  this.loadData();
  this.updateData();
},

};
</script>
