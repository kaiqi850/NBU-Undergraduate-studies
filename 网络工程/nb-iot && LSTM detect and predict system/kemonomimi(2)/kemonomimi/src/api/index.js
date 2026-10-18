import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:5000', // 你的 Flask 应用的地址
  withCredentials: true, // 这个设置取决于你的后端是否需要 cookies
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json'
  }
});

export default apiClient;