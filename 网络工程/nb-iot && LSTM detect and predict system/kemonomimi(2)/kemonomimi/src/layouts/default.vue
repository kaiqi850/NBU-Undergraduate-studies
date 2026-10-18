<template>
  <v-layout class="rounded rounded-md">
    <v-navigation-drawer expand-on-hover rail>
      <v-list density="compact" nav>
        <v-list-item prepend-icon="mdi-home-circle-outline" title="首页" value="myfiles" to="/"></v-list-item>
        <v-list-item prepend-icon="mdi-video" title="视频监控" value="shared" to="/video"></v-list-item>
        <v-list-item prepend-icon="mdi-remote" title="数据分析" value="starred" to="/analysis"></v-list-item> 
        <v-list-item prepend-icon="mdi-lock-reset" title="修改密码"  value="modify" to="/modify"></v-list-item>
        <v-list-item prepend-icon="mdi-map-marker-circle" title="model"  value="model" to="/model"></v-list-item>
        <v-list-item prepend-icon="mdi-history" title="历史数据"  value="histroydata" to="/histroydata"></v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-main class="d-flex align-center justify-center" style="min-height: 1000px;">
      <router-view />
    </v-main>
  </v-layout>
</template>

<script setup>
//
</script>

<route lang="yaml">
name: default
layout: default
children:
  - path: /analysis
    name: analysis
    component: /analysis/index.vue
</route>
