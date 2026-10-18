
import http from '../utils/request'

//请求数据
export const getData = () => {
    return http.get('/api/data')
}

export const getCount = () => {
    return http.get('api/count')
}

export const getAllData = () => {
    return http.get('api/alldatas')
}

export const getAvgTemp = () => {
    return http.get('api/avgtemp')
}

export const getAvgHum = () => {
    return http.get('api/avghum')
}

export const getLatestDataById = (params) => {
    return http.get('api/latestdata/' + params)
}

export const getIotById = (params) => {
    return http.get('api/getIotById/' + params)
}

export const getAllIot = () => {
    return http.get('api/getAllIot')
}

export const getIotCount = () => {
    return http.get('api/getIotCount')
}

export const getAbnormalTempData = () => {
    return http.get('api/abnormaltempdata')
}

export const getAbnormalHumiData = () => {
    return http.get('api/abnormalhumidata')
}

export const editIot = (data) => {
    return http.put('/api/updateIot', data)
}

export const deleteIot = (params) => {
    return http.delete('/api/deleteIot/' + params)
}

export const appendIot = (data) => {
    return http.post('api/addIot', data)
}