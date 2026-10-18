<template>
  <v-container>
    <v-row align="center" justify="center">
      <v-col cols="auto">
        <v-card :text="onlineCount" title="在线设备" width="200"></v-card>
      </v-col>
      <v-col cols="auto">
        <v-card :text="totalCount" title="总设备数" width="200"></v-card>
      </v-col>
      <v-col cols="auto">
        <v-card text="报警等硬件" title="设备报警" width="200"></v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
<script setup>
import axiosRequest from '@/utils/request';
import axios from 'axios';
import { onMounted } from 'vue';

const onlineCount = ref(0);
const totalCount = ref(0);

onMounted(() => {
  axiosRequest.get("/api/device/onlineCount")
    .then(res => onlineCount.value = res);
  axiosRequest.get("/api/device/totalCount")
    .then(res => totalCount.value = res);
})

</script>