<template>
  <v-container>
    <div id="container"></div>
  </v-container>
</template>

<script setup>
import AMapLoader from "@amap/amap-jsapi-loader";
// import { useMapContainerStore } from "@/stores/index/indexj";
// const MapContainerData = useMapContainerStore();
import axiosRequest from "@/utils/request";
import { _makeMassPoints } from "@/utils/api/index/massPoint";
import { onMounted, onUnmounted, ref, computed, defineEmits } from "vue";

const emitEvent = defineEmits([
  // 点击地图上的坐标
  'pointClickEvent'
]);
// 原始坐标集合
const _originalPoints = ref([]);
// 高德地图对象
const _AMap = ref(null);
// 高德地图实例化对象
const _map = ref(null);
// 初始缩放大小
const _initZoom = ref(5);
// 地图组件的key
const _mapKey = ref('c08c1da9af99050f1c68373c0dfc4e53');
// 高德地图上的海量点图层，用于后续的修改
const _layer = ref(null);

// 事件

// 点击到地图上的坐标以后发起后端请求
function _pointsClick(id) {
  emitEvent('pointClickEvent', id);
}

// 计算属性

// 点聚合坐标
const _massPointsComputed = computed(() => {
  let points = []

  _originalPoints.value.forEach((value) => {
    let point = []
    point.push(value.longitude)
    point.push(value.latitude)

    points.push(point)
  })

  return points
});

// 事件
onMounted(async () => {
  _originalPoints.value = await axiosRequest.get("/api/device/allLocation");

  AMapLoader.load({
    key: _mapKey.value, // 申请好的Web端开发者Key，首次调用 load 时必填
    version: "2.0", // 指定要加载的 JSAPI 的版本，缺省时默认为 1.4.15
    plugins: ["AMap.MarkerCluster", "AMap.Geocoder"], //需要使用的的插件列表，如比例尺'AMap.Scale'，支持添加多个如：['...','...']
  })
    .then((AMap) => {
      let map = new AMap.Map("container", {
        // 设置地图容器id
        // viewMode: "3D", // 是否为3D地图模式  
        zoom: _initZoom.value, // 初始化地图级别
        center: [116.397428, 39.90923], // 初始化地图中心点位置
      });

      map.on('complete', () => {
        _layer.value = _makeMassPoints(
          _AMap.value,
          _map.value,
          _massPointsComputed.value,
          _layer.value,
          _pointsClick)
      });

      _AMap.value = AMap;
      _map.value = map;
    })
    .catch((e) => {
      console.log(e);
    });
});

onUnmounted(() => {
  _map.value?.destroy();
});
</script>

<style scoped>
#container {
  padding: 0px;
  margin: 0px;
  width: 100%;
  height: 800px;
}
</style>@/utils/api/index/massPoint