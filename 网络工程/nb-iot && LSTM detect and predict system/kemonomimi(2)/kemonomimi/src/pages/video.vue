<template>
	<v-container>
	  <v-row>
		<v-row align="center" justify="center">
		  <v-col cols="auto">
			<v-btn density="default" @click="realTimeMethod">实时监控</v-btn>
		  </v-col>
		  <v-col cols="auto">
			<v-btn density="default" @click="playbackMethod">历史回放</v-btn>
		  </v-col>
		</v-row>
	  </v-row>
  
	  <v-row>
		<v-row class="justify-center align-center" style="height: 100vh;">
		  <!-- 实时监控视频 -->
		  <video 
			v-if="mode === 'realTime'" 
			ref="webcamVideo" 
			autoplay 
			muted 
			playsinline 
			style="width: 1000px; height: 1000px; border: 1px solid #ccc;">
			您的浏览器不支持视频标签。
		  </video>
  
		  <!-- 历史回放视频 -->
		  <iframe 
			v-else-if="mode === 'playback'" 
			:src="videoUri" 
			frameborder="0" 
			style="width: 1000px; height: 1000px; border: 1px solid #ccc;">
		  </iframe>
  
		  <!-- 默认视频或占位符 -->
		  <div v-else class="text-center text-gray-700">
			请点击“实时监控”或“历史回放”按钮以查看视频。
		  </div>
		</v-row>
	  </v-row>
	</v-container>
  </template>
  
  <script setup>
  import { ref, onBeforeUnmount } from 'vue';
  import axiosRequest from "@/utils/request";
  
  // 视频的URI地址
  const videoUri = ref("");
  
  // 当前模式：'realTime' 或 'playback' 或 'none'
  const mode = ref("none");
  
  // 摄像头的MediaStream
  const webcamStream = ref(null);
  
  // 视频元素的引用
  const webcamVideo = ref(null);
  
  // 实时视频监控方法
  async function realTimeMethod() {
	try {
	  // 停止任何现有的视频流
	  stopWebcam();
  
	  // 访问用户的摄像头
	  const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
	  webcamStream.value = stream;
  
	  // 将流赋值给视频元素
	  if (webcamVideo.value) {
		webcamVideo.value.srcObject = stream;
	  }
  
	  // 设置当前模式
	  mode.value = 'realTime';
	  videoUri.value = ""; // 清空历史视频URI
	} catch (error) {
	  console.error("无法访问摄像头:", error);
	  alert("无法访问摄像头，请检查权限设置。");
	}
  }
  
  // 历史回放方法
  function playbackMethod() {
	// 停止任何现有的视频流
	stopWebcam();
  
	// 设置当前模式
	mode.value = 'playback';
  
	// 从API获取历史视频URI
	axiosRequest.get("/api/video/playback")
	  .then(res => {
		// 假设API返回的是视频的URL字符串
		videoUri.value = res.data.uri; // 根据API返回的数据结构调整
	  })
	  .catch(error => {
		console.error("获取历史回放视频失败:", error);
		alert("无法获取历史回放视频，请稍后再试。");
	  });
  }
  
  // 停止摄像头流的方法
  function stopWebcam() {
	if (webcamStream.value) {
	  webcamStream.value.getTracks().forEach(track => track.stop());
	  webcamStream.value = null;
	}
	mode.value = 'none';
  }
  
  // 组件销毁前清理摄像头流
  onBeforeUnmount(() => {
	stopWebcam();
  });
  </script>
  
  <style scoped>
  .text-center {
	text-align: center;
  }
  
  .text-gray-700 {
	color: #4a5568;
  }
  
  .v-btn {
	margin: 0 10px;
  }
  </style>
  