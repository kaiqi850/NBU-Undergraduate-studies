<template>
  <v-card>
    <v-tabs v-model="_tab" bg-color="primary">
      <v-tab value="one">最新数据</v-tab>
      <v-tab value="two">历史数据</v-tab>
      <v-tab value="three">天气预报</v-tab>
    </v-tabs>

    <v-card-text>
      <v-window v-model="_tab">

        <!-- <div class="text-center" v-show="MapContainerData.isLoading">
          <v-progress-circular color="primary" indeterminate></v-progress-circular>
        </div> -->
        <!-- <div class="text-caption" v-if="MapContainerData.isShowNoData">未选择设备</div> -->
        <div class="text-center" v-show="_isLoading.value">
          <v-progress-circular color="primary" indeterminate></v-progress-circular>
        </div>
        <div class="text-caption text-center" v-if="_selectDeviceId.value == -1">未选择设备</div>

        <v-window-item value="one">
          <v-table class="text-caption" density="compact" v-show="_isRequestSuccess.value">
            <tbody>
              <tr align="right" style="white-space: nowrap;">
                <th>数据时间:</th>
                <td>{{ _latestData.value.dateTime?.replace("T", " ") }}</td>
              </tr>

              <tr align="right">
                <th>设备名:</th>
                <td>{{ _latestData.value.deviceName }}</td>
              </tr>

              <tr align="right">
                <th>设备地址:</th>
                <td>{{ _geoAddress.value.regeocode?.formatted_address }}</td>
              </tr>

              <tr align="right">
                <th>空气温度:</th>
                <td>{{ _latestData.value.airTemperature }}</td>
              </tr>

              <tr align="right">
                <th>空气湿度:</th>
                <td>{{ _latestData.value.airTemperature }}</td>
              </tr>

              <tr align="right">
                <th>土壤温度:</th>
                <td>{{ _latestData.value.soilTemperature }}</td>
              </tr>

              <tr align="right">
                <th>土壤湿度:</th>
                <td>{{ _latestData.value.soilHumidity }}</td>
              </tr>

              <tr align="right">
                <th>光照强度:</th>
                <td>{{ _latestData.value.light }}</td>
              </tr>

              <tr align="right" style="white-space: nowrap;">
                <th>二氧化碳浓度:</th>
                <td>{{ _latestData.value.co2 }}</td>
              </tr>
            </tbody>
          </v-table>
        </v-window-item>

        <v-window-item value="two">
          <div v-if="_isRequestSuccess.value">
            <div class="text-caption text-center">设备名:{{ _latestData.value.deviceName }}</div>

            <v-select label="选择数据" variant="underlined" :items="_selectList" v-model="_selectType">
            </v-select>

            <v-menu v-model="_showMenu" :close-on-content-click="false" location="bottom"
              transition="scroll-y-transition" min-width="auto">
              <template v-slot:activator="{ props }">
                <v-text-field label="选择时间" readonly v-bind="props" variant="underlined"
                  v-model="timeRangeComputed"></v-text-field>
              </template>

              <DatePicker v-model.range="_range" mode="date" />
            </v-menu>

            <v-btn block variant="text" :loading="_buttonLoading" @click="searchHistoryDataMethod">
              搜索
            </v-btn>
          </div>
        </v-window-item>

        <v-window-item value="three">
        </v-window-item>
      </v-window>

    </v-card-text>

    <!-- 弹窗组件 -->
    <v-dialog v-model="_showDialog" width="auto">
      <v-card max-width="1000">
        <v-card-text>
          <div id="echarts" style="width: 1000px;height:400px;"></div>
        </v-card-text>

        <template v-slot:actions>
          <v-btn class="ms-auto" text="Ok" @click="_showDialog = false"></v-btn>
        </template>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script setup>
import { ref, defineProps } from 'vue';
import { DatePicker } from 'v-calendar';
import 'v-calendar/style.css';
import * as echarts from 'echarts';
import axiosRequest from '@/utils/request';
import { _startTime, _endTime } from '@/utils/api/index/date'
import { nextTick } from 'vue';
import { watch } from 'vue';

const props = defineProps([
  '_isRequestSuccess',
  '_isLoading',
  '_selectDeviceId',
  '_latestData',
  '_geoAddress'
])
// 选择数据类型列表
const _selectList = ref([
  { title: '空气温度', value: 1 },
  { title: '空气湿度', value: 2 },
  { title: '土壤温度', value: 3 },
  { title: '土壤湿度', value: 4 },
  { title: '光照强度', value: 5 },
  { title: '二氧化碳浓度', value: 6 },
])
// 被选择的数据类型
const _selectType = ref(null);
// 历史数据下进行数据搜索的按钮
const _buttonLoading = ref(false);
// 弹窗开关,用于展示图表数据
const _showDialog = ref(false);

const _tab = ref("one");
const _showMenu = ref(false);
const _range = ref({
  start: new Date(),
  end: new Date(),
});

// 搜索历史数据，并进行图表展示
function searchHistoryDataMethod() {
  if (props._selectDeviceId.value == -1 || _selectType.value == null) return;

  _buttonLoading.value = true;

  axiosRequest.get('/api/device/historyData', {
    params: {
      id: props._selectDeviceId.value,
      dataType: _selectType.value,
      startDate: _startTime(_range.value.start),
      endDate: _endTime(_range.value.end)
    }
  })
    .then(async (res) => {
      _buttonLoading.value = false;
      _showDialog.value = true;

      // dialog没有渲染，直接读DOM会报错
      await nextTick();

      let myChart = echarts.init(document.getElementById('echarts'));
      let option;
      // let base = new Date(res[0].dateTime);
      // let oneDay = 24 * 3600 * 1000;
      let date = [];
      let data = [];

      for (let i = 0; i < res.length; i++) {
        let now = new Date(res[i].dateTime);
        date.push([now.getFullYear(), now.getMonth() + 1, now.getDate()].join('/') + " " + [now.getHours(), now.getMinutes(), now.getSeconds()].join(':'));
        data.push(res[i].value);
      }

      option = {
        tooltip: {
          trigger: 'axis',
          position: function (pt) {
            return [pt[0], '10%'];
          }
        },
        title: {
          // left: 'center',
          // text: 'Large Area Chart'
        },
        toolbox: {
          feature: {
            dataZoom: {
              yAxisIndex: 'none'
            },
            restore: {},
            saveAsImage: {}
          }
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: date
        },
        yAxis: {
          type: 'value',
          boundaryGap: [0, '100%']
        },
        dataZoom: [
          {
            type: 'inside',
            start: 0,
            end: 10
          },
          {
            start: 0,
            end: 10
          }
        ],
        series: [
          {
            name: _selectList.value[_selectType.value].title,
            type: 'line',
            symbol: 'none',
            sampling: 'lttb',
            itemStyle: {
              color: 'rgb(255, 70, 131)'
            },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                {
                  offset: 0,
                  color: 'rgb(255, 158, 68)'
                },
                {
                  offset: 1,
                  color: 'rgb(255, 70, 131)'
                }
              ])
            },
            data: data
          }
        ]
      };

      option && myChart.setOption(option);
    })
}

const timeRangeComputed = computed(() => {
  return _range.value.start.toLocaleDateString() + ' - ' + _range.value.end.toLocaleDateString();
})

// 监听刷新事件，重置数据
watch(props._isLoading, () => {
  _selectType.value = null;
  _range.value.start = new Date();
  _range.value.end = new Date();
})

</script>

<script>
export default {
  data() {
    return {
      selected: null
    }
  }
}
</script>