const sparklineChartData = {
    sparkChart1: [
        6,
        2,
        8,
        4,
        3,
        8,
        1,
        3,
        6,
        5,
        9,
        2,
        8,
        1,
        4,
        8,
        9,
        8,
        2,
        1
    ],
    sparkChart2: [
        6,
        2,
        8,
        4,
        -3,
        8,
        1,
        -3,
        6,
        -5,
        9,
        2,
        -8,
        1,
        4,
        8,
        9,
        8,
        2,
        1
    ],
    sparkChart3: [
        6,
        2,
        8,
        4,
        3,
        8,
        1,
        3,
        6,
        5,
        9,
        2,
        8,
        1,
        4,
        8,
        9,
        8,
        2,
        1
    ],
    reflineStyle: {
        strokeOpacity: 1,
        strokeDasharray: "3, 3"
    },
    style: {
        stroke: "#02a499",
        fill: "#02a499"
    }
};

const salesDonutChart = {
    data: {
        series: [54, 28, 17],
        labels: [1, 2, 3]
    },
    options: {
        donut: true,
        showLabel: false
    }
};

const radialBarChart = {
    chartOptions: {
        plotOptions: {
            radialBar: {
                hollow: {
                    size: "45%"
                },
                dataLabels: {
                    value: {
                        show: false
                    },
                    name: {
                        show: false
                    }
                }
            }
        },
        colors: ["#02a499"]
    }
};

export { sparklineChartData, salesDonutChart, radialBarChart }