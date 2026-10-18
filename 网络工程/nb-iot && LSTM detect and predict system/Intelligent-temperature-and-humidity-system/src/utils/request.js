//axios二次封装
import axios from 'axios'

const http = axios.create({
    //通用请求地址前缀
    baseURL:'http://localhost:9090',
    timeout:10000,
})

http.interceptors.request.use(function(config) {
    return config;
},function(error) {
    return Promise.reject(error);
});

http.interceptors.response.use(function(response) {
    return response;
},function(error) {
    return Promise.reject(error);
});

export default http