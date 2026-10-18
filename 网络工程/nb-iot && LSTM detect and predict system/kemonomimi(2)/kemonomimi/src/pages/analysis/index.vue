<template>
  <div class="analysis-container">
    <div class="analysis-main">
      <div v-for="device in devices" :key="device.id" class="device-section">
        <div class="chart-row">
          <!-- 温度报表 -->
          <div class="chart-col">
            <div class="chart-card">
              <div class="card-header">
                [{{ device.id }}] 温度报表
              </div>
              <div class="statistics-row">
                <div class="stat-item">
                  <div class="stat-title">最高温度</div>
                  <div class="stat-value">
                    {{ device.maxTemperature ? device.maxTemperature.toFixed(2) : '0.00' }} ℃
                  </div>
                </div>
                <div class="stat-item">
                  <div class="stat-title">最低温度</div>
                  <div class="stat-value">
                    {{ device.minTemperature ? device.minTemperature.toFixed(2) : '0.00' }} ℃
                  </div>
                </div>
                <div class="stat-item">
                  <div class="stat-title">平均温度</div>
                  <div class="stat-value">
                    {{ device.avgTemperature ? device.avgTemperature.toFixed(2) : '0.00' }} ℃
                  </div>
                </div>
              </div>
              <div class="chart-container">
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
          <div class="chart-col">
            <div class="chart-card">
              <div class="card-header">
                [{{ device.id }}] 湿度报表
              </div>
              <div class="statistics-row">
                <div class="stat-item">
                  <div class="stat-title">最高湿度</div>
                  <div class="stat-value">
                    {{ device.maxHumidity ? device.maxHumidity.toFixed(2) : '0.00' }} %
                  </div>
                </div>
                <div class="stat-item">
                  <div class="stat-title">最低湿度</div>
                  <div class="stat-value">
                    {{ device.minHumidity ? device.minHumidity.toFixed(2) : '0.00' }} %
                  </div>
                </div>
                <div class="stat-item">
                  <div class="stat-title">平均湿度</div>
                  <div class="stat-value">
                    {{ device.avgHumidity ? device.avgHumidity.toFixed(2) : '0.00' }} %
                  </div>
                </div>
              </div>
              <div class="chart-container">
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
    </div>
  </div>
</template>

<script>
import TemperatureChart from "./TemperatureChart.vue";
import HumidityChart from "./HumidityChart.vue";
import * as xlsx from "xlsx";
import * as echarts from 'echarts';

export default {
  components: {
    TemperatureChart,
    HumidityChart,
  },
  data() {
    return {
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
        const realTimeData = xlsx.utils.sheet_to_json(realTimeWorkbook.Sheets[realTimeWorkbook.SheetNames[0]], {
          raw: false,  // 确保数据作为字符串读取
          header: ["Temperature", "Humidity", "deviceId", "Timestamp"]  // 指定列名
        });

        // 读取预测数据文件
        const historyFile = await fetch("/predicted_data.xlsx");
        const historyBlob = await historyFile.blob();
        const historyWorkbook = xlsx.read(await historyBlob.arrayBuffer(), { type: "array" });
        const historyData = xlsx.utils.sheet_to_json(historyWorkbook.Sheets[historyWorkbook.SheetNames[0]], {
          raw: false,
          header: ["Temperature", "Humidity", "deviceId", "Timestamp"]
        });

        // 按设备分组处理数据
        const groupedDevices = {};
        realTimeData.forEach((row) => {
          // 跳过标题行
          if (row.Temperature === "Temperature") return;
          
          const deviceId = row.deviceId || "2";  // 如果没有设备ID，默认使用"2"
          
          if (!groupedDevices[deviceId]) {
            groupedDevices[deviceId] = {
              id: deviceId,
              temperatureData: [],
              humidityData: [],
              secondaryTemperatureData: [],
              secondaryHumidityData: [],
              timeStamps: [],
              maxTemperature: -Infinity,
              minTemperature: Infinity,
              avgTemperature: 0,
              maxHumidity: -Infinity,
              minHumidity: Infinity,
              avgHumidity: 0
            };
          }
          
          // 添加数据前进行数值转换
          const temp = parseFloat(row.Temperature);
          const humidity = parseFloat(row.Humidity);
          
          if (!isNaN(temp)) {
            groupedDevices[deviceId].temperatureData.push(temp);
          }
          
          if (!isNaN(humidity)) {
            groupedDevices[deviceId].humidityData.push(humidity);
          }
          
          groupedDevices[deviceId].timeStamps.push(row.Timestamp || "未知");
        });

        Object.values(groupedDevices).forEach((device) => {
          // 只取最后300条实时数据
          const lastIndex = device.temperatureData.length;
          const startIndex = Math.max(0, lastIndex - 300);
          
          device.temperatureData = device.temperatureData.slice(startIndex);
          device.humidityData = device.humidityData.slice(startIndex);
          device.timeStamps = device.timeStamps.slice(startIndex);

          // 计算统计值（只使用实时数据）
          if (device.temperatureData.length > 0) {
            device.maxTemperature = Math.max(...device.temperatureData);
            device.minTemperature = Math.min(...device.temperatureData);
            device.avgTemperature = device.temperatureData.reduce((a, b) => a + b, 0) / device.temperatureData.length;
          }

          if (device.humidityData.length > 0) {
            device.maxHumidity = Math.max(...device.humidityData);
            device.minHumidity = Math.min(...device.humidityData);
            device.avgHumidity = device.humidityData.reduce((a, b) => a + b, 0) / device.humidityData.length;
          }

          // 添加预测数据
          const lastHistoryData = historyData.slice(-60);
          device.secondaryTemperatureData = lastHistoryData
            .filter(row => row.Temperature !== "Temperature")
            .map(row => parseFloat(row.Temperature))
            .filter(val => !isNaN(val));
            
          device.secondaryHumidityData = lastHistoryData
            .filter(row => row.Humidity !== "Humidity")
            .map(row => parseFloat(row.Humidity))
            .filter(val => !isNaN(val));
            
          const historyTimeStamps = lastHistoryData
            .filter(row => row.Timestamp !== "Timestamp")
            .map(row => row.Timestamp);

          // 合并实时数据和预测数据
          device.temperatureData = device.temperatureData.concat(device.secondaryTemperatureData);
          device.humidityData = device.humidityData.concat(device.secondaryHumidityData);
          device.timeStamps = device.timeStamps.concat(historyTimeStamps);

          // 调试输出
          console.log(`Device ${device.id} statistics:`, {
            maxTemp: device.maxTemperature,
            minTemp: device.minTemperature,
            avgTemp: device.avgTemperature,
            maxHum: device.maxHumidity,
            minHum: device.minHumidity,
            avgHum: device.avgHumidity
          });
        });

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

<style scoped>
.analysis-container {
  padding: 20px;
  width: 100%;
}

.analysis-main {
  width: 100%;
}

.device-section {
  margin-bottom: 24px;
  width: 100%;
}

.chart-row {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
}

.chart-col {
  flex: 1;
  min-width: 0;
}

.chart-card {
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
  padding: 20px;
}

.card-header {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.statistics-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
  flex: 1;
}

.stat-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #409EFF;
}

.chart-container {
  width: 100%;
  height: 400px;
  margin: 20px 0;
}
</style>
