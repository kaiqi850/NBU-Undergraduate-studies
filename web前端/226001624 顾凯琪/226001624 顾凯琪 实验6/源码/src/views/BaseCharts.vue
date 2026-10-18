<script>
import Schart from "vue-schart";
export default {
    name: "basecharts",
    components: {
        Schart,
    },
    setup() {
        const options1 = {
            type: "bar",
            title: {
                text: "最近一周编写代码量",
            },
            bgColor: "#fbfbfb",
            labels: ["周一", "周二", "周三", "周四", "周五"],
            datasets: [
                {
                    label: "c/c++",
                    fillColor: "rgba(241, 49, 74, 0.5)",
                    data: [233, 233, 233, 233, 233],
                },
                {
                    label: "java",
                    data: [233, 233, 3, 2, 1],
                }
                {
                    label: "python",
                    data: [233, 1, 1, 2, 1],
                },
            ],
        };
        const options2 = {
            type: "line",
            title: {
                text: "最近几个月代码提交情况趋势图",
            },
            bgColor: "#fbfbfb",
            labels: ["1月", "2月", "3月", "4月", "5月"],
            datasets: [
                {
                    label: "accent",
                    data: [233, 233, 233, 233, 233],
                },
                {
                    label: "wrong answer",
                    data: [23, 233, 2333, 233, 23],
                },
                {
                    label: "time exceed limited",
                    data: [114, 514, 200, 233, 666],
                },
            ],
        };
        return {
            options1,
            options2,
        };
    },
};
</script>

<style scoped>
.schart-box {
    display: inline-block;
    margin: 20px;
}
.schart {
    width: 600px;
    height: 400px;
}
.content-title {
    clear: both;
    font-weight: 400;
    line-height: 50px;
    margin: 10px 0;
    font-size: 22px;
    color: #1f2f3d;
}
</style>