<template>
  <Layout>
    <!-- 页面标题 -->
    <div class="row align-items-center">
      <div class="col-sm-6">
        <div class="page-title-box">
          <h4 class="font-size-22">系统主页</h4>
          <ol class="breadcrumb mb-0">
            <li class="breadcrumb-item active font-size-15">欢迎来到智能温湿度监测系统</li>
          </ol>
        </div>
      </div>
    </div>

    <!-- 统计数据 -->
    <div class="row">
      <div class="col-xl-3 col-md-6" v-for="stat in statData" :key="stat.title">
        <Stat
          :title="stat.title"
          :image="stat.image"
          :subText="stat.subText"
          :value="stat.value"
          :color="stat.color"
        />
      </div>
    </div>

    <!-- 设备选择 -->
    <div class="mb-3 row">
      <label class="col-sm-1 col-form-label">设备选择</label>
      <div class="col-sm-2">
        <select class="form-select" v-model="iotSelected" @change="loadTotalEntries">
          <option v-for="device in devices" :key="device.id" :value="device.id">
            {{ device.id }}
          </option>
        </select>
      </div>
    </div>

    <!-- 实时数据展示 -->
    <div class="row mt-4">
      <div class="col-md-6">
        <h5>实时温度</h5>
        <p class="text-muted">{{ currentTemperature }} ℃</p>
      </div>
      <div class="col-md-6">
        <h5>实时湿度</h5>
        <p class="text-muted">{{ currentHumidity }} %</p>
      </div>
    </div>
  </Layout>
</template>

<script>
import Layout from "../layouts/main";
import Stat from "@/components/widgets/widget-stat";
import * as XLSX from "xlsx"; // 引入 xlsx 库

export default {
  components: {
    Layout,
    Stat,
  },
  data() {
    return {
      statData: [
        {
          title: "设备总条目数",
          image: require("@/assets/images/services-icon/02.png"),
          value: "-",
          subText: "☆",
          arrowup: true,
          color: "danger",
        },
        {
          title: "连接设备数目",
          image: require("@/assets/images/services-icon/01.png"),
          value: "-",
          subText: "☆",
          arrowup: true,
          color: "success",
        },
        {
          title: "平均温度",
          image: require("@/assets/images/services-icon/04.png"),
          value: "- ℃",
          subText: "☆",
          arrowup: false,
          color: "warning",
        },
        {
          title: "平均湿度",
          image: require("@/assets/images/services-icon/04.png"),
          value: "- %",
          subText: "☆",
          arrowup: true,
          color: "warning",
        },
        {
          title: "异常温度条数",
          image: require("@/assets/images/services-icon/03.png"),
          value: "-",
          subText: "☆",
          arrowup: true,
          color: "warning",
        },
        {
          title: "异常湿度条数",
          image: require("@/assets/images/services-icon/03.png"),
          value: "-",
          subText: "☆",
          arrowup: true,
          color: "warning",
        },
      ],
      devices: [], // 动态加载的设备列表
      iotSelected: "", // 当前选中的设备ID
      currentHumidity: "-",
      currentTemperature: "-",
    };
  },
  methods: {
    loadDevices() {
      const devices = JSON.parse(localStorage.getItem("devices") || "[]");
      this.devices = devices;
      if (devices.length > 0) {
        this.iotSelected = devices[0].id;
        this.loadTotalEntries(); // 初始化时加载选中设备的数据
      }
    },
    loadTotalEntries() {
      const devices = JSON.parse(localStorage.getItem("devices") || "[]");
      const selectedDevice = devices.find(d => d.id === this.iotSelected);

      if (!selectedDevice) {
        console.error("未找到选中的设备");
        return;
      }

      // 从 public 文件夹读取 Excel 文件
      fetch("/mqtt_data.xlsx")
        .then((response) => response.arrayBuffer())
        .then((data) => {
          const workbook = XLSX.read(data, { type: "array" });
          const firstSheetName = workbook.SheetNames[0];
          const worksheet = workbook.Sheets[firstSheetName];
          const jsonData = XLSX.utils.sheet_to_json(worksheet);

          // 统计总条目数
          const totalEntriesCount = jsonData.length;

          // 统计异常温度和湿度条数
          let abnormalTemperatureCount = 0;
          let abnormalHumidityCount = 0;

          jsonData.forEach((row) => {
            // 检查温度是否超出上下限
            if (row.Temperature > selectedDevice.maxtemp || row.Temperature < selectedDevice.mintemp) {
              abnormalTemperatureCount++;
            }
            // 检查湿度是否超出上下限
            if (row.Humidity > selectedDevice.maxhumi || row.Humidity < selectedDevice.minhumi) {
              abnormalHumidityCount++;
            }
          });

          // 更新统计数据
          this.statData[0].value = totalEntriesCount; // 设置总条目数
          this.statData[4].value = abnormalTemperatureCount; // 设置异常温度条数
          this.statData[5].value = abnormalHumidityCount; // 设置异常湿度条数
        })
        .catch((error) => {
          console.error("读取设备总条目 Excel 文件失败:", error);
        });
    },
    updateStats() {
      const selectedDeviceData = JSON.parse(localStorage.getItem(this.iotSelected) || "{}");

      this.statData[1].value = this.devices.length;
      this.statData[2].value =
        selectedDeviceData.avgTemperature?.toFixed(2) + " ℃" || "- ℃";
      this.statData[3].value =
        selectedDeviceData.avgHumidity?.toFixed(2) + " %" || "- %";

      this.currentTemperature = selectedDeviceData.realTimeTemperature?.toFixed(2) || "-";
      this.currentHumidity = selectedDeviceData.realTimeHumidity?.toFixed(2) || "-";
    },
  },
  mounted() {
    this.loadDevices();
    this.updateStats();

    setInterval(() => {
      this.updateStats();
    }, 3000);
  },
  watch: {
    iotSelected() {
      this.updateStats();
      this.loadTotalEntries(); // 切换设备时重新加载数据
    },
  },
};
</script>