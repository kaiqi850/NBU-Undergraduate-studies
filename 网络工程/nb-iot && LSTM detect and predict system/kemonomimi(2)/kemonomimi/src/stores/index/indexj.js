// Utilities
import { defineStore } from 'pinia'

export const useMapContainerStore = defineStore('MapContainer', {
	state: () => ({
		// 地图组件的key
		// mapKey: 'c08c1da9af99050f1c68373c0dfc4e53',
		// 高德地图服务的key
		// apiKey: 'REPLACE_WITH_YOUR_VALUE',
		// 初始缩放大小
		// initZoom: 5,
		// 高德地图对象
		// AMap: null,
		// 高德地图实例化对象
		// map: null,
		// 被选中的设备id
		selectedPointId: 0,
		// 原始坐标集合
		originalPoints: [],
		// 高德地图上的聚合点图层，用于后续的修改
		cluster: null,
		// 高德地图上的海量点，用于后续的修改
		layer: null,
		// 设备的最新数据
		latestData: {},
		// 设备地理地址和天气数据
		geoAddress: {},
		// 展示未点击设备的图标
		isShowNoData: true,
		// 是否显示loading图标
		isLoading: false,
		// 是否成功从后端获取数据
		isRequestSuccess: false
	})
	// getters: {
	// 	// 点聚合坐标
	// 	clusterPoints: (state) => {
	// 		let points = []

	// 		state.originalPoints.forEach((value) => {
	// 			let point = { 'lnglat': [] }
	// 			point.lnglat.push(value.longitude)
	// 			point.lnglat.push(value.latitude)

	// 			points.push(point)
	// 		})

	// 		return points
	// 	},
	// 	// 海量点坐标
	// 	massPoints: (state) => {
	// 		let points = []

	// 		state.originalPoints.forEach((value) => {
	// 			let point = []
	// 			point.push(value.longitude)
	// 			point.push(value.latitude)

	// 			points.push(point)
	// 		})

	// 		return points
	// 	}
	// }
})
