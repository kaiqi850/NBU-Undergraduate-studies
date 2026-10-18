<template>
  <v-sheet :elevation="2" :height="205" :width="350" class="rounded-lg"
    style="position: absolute; top: 50px; left: 100px;">
    <div class="container">
      <div class="title text-subtitle-2">室外气象环境监控</div>
      <div class="timestamp text-subtitle-2">更新时间: 16:50</div>
    </div>

    <v-divider class="border-opacity-25"></v-divider>

    <v-table class="text-caption" density="compact">
      <tbody>
        <tr align="right" style="white-space: nowrap;">
          <th>温度:</th>
          <td>14℃</td>
        </tr>

        <tr align="right">
          <th>湿度:</th>
          <td>53%</td>
        </tr>

        <tr align="right">
          <th>太阳光照:</th>
          <td>3842LUX</td>
        </tr>

        <tr align="right">
          <th>太阳辐射</th>
          <td>8.7W/m2</td>
        </tr>
      </tbody>
    </v-table>
  </v-sheet>

  <v-sheet :elevation="2" :height="180" :width="350" class="rounded-lg"
    style="position: absolute; top: 350px; left: 100px;">
    <div class="container">
      <div class="title text-subtitle-2">三日天气预报</div>
    </div>

    <v-divider class="border-opacity-25"></v-divider>

    <v-row>
      <v-col col="auto" class="mx-auto text-center">
        <div class="text-h6">周三</div>

        <v-icon color="black" icon="mdi-weather-pouring" size="60" class="py-lg-4"></v-icon>

        <div class="py-lg-1">11℃~17℃</div>
      </v-col>

      <v-divider vertical style="margin-top: 12px;"></v-divider>

      <v-col col="auto" class="mx-auto text-center">
        <div class="text-h6">周四</div>

        <v-icon color="error" icon="mdi-weather-lightning" size="60" class="py-lg-4"></v-icon>

        <div class="py-lg-1">9℃~14℃</div>
      </v-col>

      <v-divider vertical style="margin-top: 12px;"></v-divider>

      <v-col col="auto" class="mx-auto text-center">
        <div class="text-h6">周五</div>

        <v-icon color="black" icon="mdi-weather-sunny" size="60" class="py-lg-4"></v-icon>

        <div class="py-lg-1">13℃~20℃</div>
      </v-col>
    </v-row>

  </v-sheet>

  <v-sheet :elevation="2" :height="40" :width="350" class="rounded-lg"
    style="position: absolute; top: 600px; left: 100px;">
    <div class="container">
      <div class="title text-subtitle-2">实时视频监控</div>
    </div>
  </v-sheet>

  <v-sheet :elevation="2" :height="220" :width="350" class="rounded-lg"
    style="position: absolute; top: 630px; left: 100px;">
    <div class="container">
      <!-- <div class="title text-h4">这里放视频</div> -->
      <video src="@/assets/video.mp4" controls width="350" height="200" autoplay></video>


    </div>
  </v-sheet>

  <v-sheet :elevation="2" :height="108" :width="700" class="rounded-lg"
    style="position: absolute; top: 50px; left: 600px;">
    <div class="container">
      <div class="title text-subtitle-2">温室环境监控</div>
    </div>

    <v-divider class="border-opacity-25"></v-divider>

    <v-row class="py-lg-2">
      <v-col col="auto" class="mx-auto text-center">
        <div>空气温度</div>
        <div>24℃</div>
      </v-col>

      <v-divider vertical style="margin-top: 4px;"></v-divider>

      <v-col col="auto" class="mx-auto text-center">
        <div>空气湿度</div>
        <div>64%</div>
      </v-col>

      <v-divider vertical style="margin-top: 4px;"></v-divider>

      <v-col col="auto" class="mx-auto text-center">
        <div>CO2浓度</div>
        <div>843 ppm</div>
      </v-col>

      <v-divider vertical style="margin-top: 4px;"></v-divider>

      <v-col col="auto" class="mx-auto text-center">
        <div>光照强度</div>
        <div>1039 lux</div>
      </v-col>
    </v-row>

  </v-sheet>

  <div id="threejs" style="position: absolute; top: 200px;left: 500px"></div>
  
  <v-sheet :elevation="2" :height="auto" :width="250" class="rounded-lg"
    style="position: absolute; top: 50px; left: 1600px;">
  <div class="container">
    <div class="title text-subtitle-2">温室设备控制</div>
  </div>

  <v-divider class="border-opacity-25"></v-divider>

  <!-- 修改 v-row 为垂直方向 -->
  <v-row class="py-lg-4" direction="column" align="center">
    
    <!-- 风机设备控制 -->
    <v-col col="auto" class="mx-auto text-center">
      <img src="@/assets/fan.png" alt="Icon" style="width: 30px; height: 30px;">
      <div class="py-lg-1">风机</div>
      <v-switch color="primary" label="开关" class="d-flex justify-center"></v-switch>
    </v-col>

    <v-divider style="margin-top: 4px;"></v-divider>

    <!-- 照明设备控制 -->
    <v-col col="auto" class="mx-auto text-center">
      <img src="@/assets/light.png" alt="Icon" style="width: 30px; height: 30px;">
      <div class="py-lg-1">照明</div>
      <v-switch color="primary" label="开关" class="d-flex justify-center"></v-switch>
    </v-col>

    <v-divider style="margin-top: 4px;"></v-divider>

    <!-- 另一照明设备控制 -->
    <v-col col="auto" class="mx-auto text-center">
      <img src="@/assets/light.png" alt="Icon" style="width: 30px; height: 30px;">
      <div class="py-lg-1">照明</div>
      <v-switch color="primary" label="开关" class="d-flex justify-center"></v-switch>
    </v-col>

    <v-divider style="margin-top: 4px;"></v-divider>

    <!-- 另一风机设备控制 -->
    <v-col col="auto" class="mx-auto text-center">
      <img src="@/assets/fan.png" alt="Icon" style="width: 30px; height: 30px;">
      <div class="py-lg-1">风机</div>
      <v-switch color="primary" label="开关" class="d-flex justify-center"></v-switch>
    </v-col>

  </v-row>
</v-sheet>

</template>

<script setup>
// import InfoCard from '@/components/index/InfoCard.vue';
// import MapContainer from '@/components/index/MapContainer.vue';
// import DataPanel from '@/components/index/DataPanel.vue';
import { ref } from 'vue';
import axiosRequest from "@/utils/request";
import { onMounted } from 'vue';
import * as echarts from 'echarts';
import { nextTick } from 'vue';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

// 从后端获取到数据以后在前端进行展示
const _isRequestSuccess = ref(false);
const _isLoading = ref(false);
const _selectDeviceId = ref(-1);
const _latestData = ref({});
const _geoAddress = ref({});

const model = ref("no")

// 传递给子组件
// let DataPanelProps = {
//   _isRequestSuccess,
//   _isLoading,
//   _selectDeviceId,
//   _latestData,
//   _geoAddress
// }

// function handleChange() {
//   if (model.value == 'no') {
//     model.value = 'yes'
//   } else {
//     model.value = 'no'
//   }
// }

// 点击到地图上的坐标以后发起后端请求
// function pointClickEvent(id) {
//   _isRequestSuccess.value = false;
//   _isLoading.value = true;
//   _selectDeviceId.value = id;

//   let promise_latestDataById = new Promise((resolve) => {
//     axiosRequest.get("/api/device/latestDataById", {
//       params: {
//         id
//       }
//     })
//       .then(res => {
//         _latestData.value = res;
//         resolve();
//       });
//   });

//   let promise_deviceGeoAddressById = new Promise((resolve) => {
//     axiosRequest.get("/api/device/deviceGeoAddressById", {
//       params: {
//         id
//       }
//     })
//       .then(res => {
//         _geoAddress.value = res;
//         resolve();
//       });
//   });

//   Promise.all([promise_latestDataById, promise_deviceGeoAddressById])
//     .then(() => {
//       _isLoading.value = false;
//       _isRequestSuccess.value = true;
//     });
// }

onMounted(() => {

  // 透视摄像头
  const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.z = 5;

  // 基础渲染器
  // const renderer = new THREE.WebGLRenderer({ alpha: true });
  const renderer = new THREE.WebGLRenderer({ alpha: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(1000, 700);
  renderer.setClearColor(0xffffff);
  document.getElementById('threejs').appendChild(renderer.domElement);

  // 可移动的摄像头
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(0, 0.5, 0);
  controls.update();
  // controls.enablePan = false;
  controls.enableDamping = true;

  // 辐射场景贴图
  const pmremGenerator = new THREE.PMREMGenerator(renderer);

  // const geometry = new THREE.BoxGeometry(1, 1, 1);
  // const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
  // const cube = new THREE.Mesh(geometry, material);
  // scene.add(cube);

  // 创建场景
  const scene = new THREE.Scene();
  scene.environment = pmremGenerator.fromScene(new RoomEnvironment(renderer), 0.04).texture;

  // 模型加载器
  const loader = new GLTFLoader();
  loader.load('src/pages/garden_greenhouse/scene.gltf', function (gltf) {

    scene.add(gltf.scene);

  }, undefined, function (error) {

    console.error(error);

  });

  function animate() {
    requestAnimationFrame(animate);
    controls.update();
    // cube.rotation.x += 0.01;
    // cube.rotation.y += 0.01;
    renderer.render(scene, camera);
  }
  animate();
})
</script>
<style>
.container {
  display: flex;
  width: 100%;
}

.title {
  flex-grow: 1;
  /* font-size: 2em; */
  /* 大标题字体大小 */
  padding: 10px;
  font-family: Arial, sans-serif;
  /* 使用Arial字体 */
  box-sizing: border-box;
  /* 防止padding影响最终尺寸 */
}

.timestamp {
  /* font-size: 1em; */
  /* 时间戳字体大小 */
  padding: 10px;
  font-family: Arial, sans-serif;
  box-sizing: border-box;
  white-space: nowrap;
  /* 防止时间戳折行 */
}
</style>