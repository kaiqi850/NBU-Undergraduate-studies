import axios from "axios";

axios.defaults.headers['Content-Type'] = 'application/json;charset=utf-8';

const axiosRequest = axios.create({
    baseURL: 'http://47.98.138.228:81',
    // 超时
    timeout: 10000
});

// const axiosMyBatisRequest = axios.create({
//     baseURL: 'http://47.98.138.228:81',
//     // 超时
//     timeout: 10000
// });

axiosRequest.interceptors.response.use(res => {
    return res.data;
});

function axiosOnenetCommand(deviceId, controlType) {
    axios.post("https://iot-api.heclouds.com/thingmodel/call-service",
        {
            "product_id": "06h4QR2F17",
            "device_name": "5",
            "identifier": "command",
            "params": {
                "deviceId": String(deviceId),
                "controlType": String(controlType)
            }
        },
        {
            headers: {
                "authorization": "version=2022-05-01&res=userid%2F370210&et=1739786859&method=sha256&sign=BLdKB%2FOv3B9mYiaMFU8SGIxIsWbdhEOCFz8KLsSc7%2FI%3D"
            }
        })
        .then(res => console.log(res));
}

function axiosOnenetPumpCommand(deviceId, controlType) {
    axios.post("https://iot-api.heclouds.com/thingmodel/call-service",
        {
            "product_id": "06h4QR2F17",
            "device_name": "6",
            "identifier": "command",
            "params": {
                "deviceId": String(deviceId),
                "controlType": String(controlType)
            }
        },
        {
            headers: {
                "authorization": "version=2022-05-01&res=userid%2F370210&et=1739786859&method=sha256&sign=BLdKB%2FOv3B9mYiaMFU8SGIxIsWbdhEOCFz8KLsSc7%2FI%3D"
            }
        })
        .then(res => console.log(res));
}

export default axiosRequest;
export { axiosOnenetCommand, axiosOnenetPumpCommand };