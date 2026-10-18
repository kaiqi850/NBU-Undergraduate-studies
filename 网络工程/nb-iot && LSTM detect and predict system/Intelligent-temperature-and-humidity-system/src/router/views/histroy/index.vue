<script>
import Layout from "../../layouts/main";
import PageHeader from "@/components/page-header";
import appConfig from "@/app.config";
import * as XLSX from 'xlsx';

/**
 * 历史信息组件
 */
export default {
  page: {
    title: "历史数据",
    meta: [{ name: "description", content: appConfig.description }]
  },
  components: { Layout, PageHeader },
  data() {
    return {
      title: "历史数据",
      items: [
        {
          text: "温湿度监测系统",
          href: "/"
        },
        {
          text: "历史数据",
          active: true
        }
      ],
      totalRows: 1,
      currentPage: 1,
      perPage: 10,
      pageOptions: [10, 25, 50, 100],
      filter: null,
      filterOn: [],
      sortBy: "age",
      sortDesc: false,
      fields: [
        { key: "设备ID", sortable: true },
        { key: "时间", sortable: true },
        { key: "温度", label: "温度（℃）", sortable: true },
        { key: "湿度", label: "湿度（%）", sortable: true }
      ],
      tableData: [],
      lastModifiedTime: null, // 保存文件的最后修改时间
      fileCheckInterval: null // 定时器引用
    };
  },
  computed: {
    rows() {
      return this.tableData.length;
    }
  },
  mounted() {
    this.readExcelFile(); // 初始加载数据

    // 定期检查 Excel 文件是否更新
    this.fileCheckInterval = setInterval(() => {
      this.checkForUpdates();
    }, 5000); // 每5秒检查一次
  },
  beforeDestroy() {
    // 清理定时器
    if (this.fileCheckInterval) {
      clearInterval(this.fileCheckInterval);
    }
  },
  methods: {
    onFiltered(filteredItems) {
      this.totalRows = filteredItems.length;
      this.currentPage = 1;
    },
    readExcelFile() {
      const filePath = '/mqtt_data.xlsx'; // 假设文件放在 public 文件夹下
      fetch(filePath)
        .then(response => {
          if (!response.ok) {
            throw new Error('文件未找到！');
          }
          return response.arrayBuffer();
        })
        .then(buffer => {
          const workbook = XLSX.read(buffer, { type: 'array' });
          const sheetName = workbook.SheetNames[0];
          const worksheet = workbook.Sheets[sheetName];
          const excelData = XLSX.utils.sheet_to_json(worksheet);

          // 处理前 100 条数据
          const processedData = excelData.map(row => ({
            设备ID: row['deviceId'],
            时间: row['Timestamp'] || '未知时间',
            温度: parseFloat(row['Temperature'] || 0).toFixed(2),
            湿度: parseFloat(row['Humidity'] || 0).toFixed(2)
          }));

          this.tableData = processedData; // 显示前 50 条数据
          this.totalRows = this.tableData.length;

          // 存储到 localStorage
          localStorage.setItem('mqttData', JSON.stringify(processedData));
        })
        .catch(error => {
          console.error('读取文件失败:', error);
          this.$message({
            type: 'error',
            message: '读取文件失败，请确保 mqtt_data.xlsx 文件存在！'
          });
        });
    },
    checkForUpdates() {
      const filePath = '/mqtt_data.xlsx'; // Excel 文件路径

      fetch(filePath, { method: 'HEAD' })
        .then(response => {
          if (!response.ok) {
            throw new Error('无法获取文件信息！');
          }

          const lastModified = response.headers.get('Last-Modified');
          if (lastModified && lastModified !== this.lastModifiedTime) {
            this.lastModifiedTime = lastModified; // 更新最后修改时间
            console.log('检测到文件更新，重新加载数据...');
            this.readExcelFile(); // 文件更新时重新加载数据
          }
        })
        .catch(error => {
          console.error('检查文件更新失败:', error);
        });
    },
    outputXLSX() {
      const savedData = localStorage.getItem('mqttData');
      if (!savedData) {
        this.$message({
          type: 'error',
          message: '没有可导出的数据！'
        });
        return;
      }

      const tableData = JSON.parse(savedData);

      const wb = XLSX.utils.book_new();
      const ws = XLSX.utils.json_to_sheet(tableData);
      XLSX.utils.book_append_sheet(wb, ws, 'Sheet1');

      XLSX.writeFile(wb, 'mqtt_data.xlsx');

      this.$message({
        type: 'success',
        message: '导出成功！'
      });
    },
    outputAbnormalData() {
      const TEMP_MAX = 25;
      const TEMP_MIN = 0;
      const HUMI_MAX = 100;
      const HUMI_MIN = 20;

      const processedData = [];
      
      this.tableData.forEach(element => {
        const curTemp = parseFloat(element.温度);
        const curHumi = parseFloat(element.湿度);
        
        let isAbnormal = false;
        let status = [];
        
        if (curTemp > TEMP_MAX || curTemp < TEMP_MIN) {
          status.push('温度异常');
          isAbnormal = true;
        }
        
        if (curHumi > HUMI_MAX || curHumi < HUMI_MIN) {
          status.push('湿度异常');
          isAbnormal = true;
        }
        
        if (isAbnormal) {
          processedData.push({
            设备ID: element.设备ID,
            时间: element.时间,
            温度: element.温度,
            湿度: element.湿度,
            状态: status.join('、'),
            正常温度范围: `${TEMP_MIN}℃ ~ ${TEMP_MAX}℃`,
            正常湿度范围: `${HUMI_MIN}% ~ ${HUMI_MAX}%`
          });
        }
      });

      if (processedData.length === 0) {
        this.$message({
          type: 'info',
          message: '没有发现异常数据！'
        });
        return;
      }

      const wb = XLSX.utils.book_new();
      const ws = XLSX.utils.json_to_sheet(processedData);
      XLSX.utils.book_append_sheet(wb, ws, "Sheet1");
      XLSX.writeFile(wb, "AbnormalRecords.xlsx");

      this.$message({
        type: 'success',
        message: `成功导出 ${processedData.length} 条异常数据！`
      });
    }
  }
};
</script>

<template>
  <Layout>
    <PageHeader :title="title" :items="items" />

    <div class="row">
      <div class="col-12">
        <div class="card">
          <div class="card-body">
            <h4 class="card-title">数据条目</h4>
            <p class="card-title-desc"></p>
            <div class="row mb-md-2">
              <div class="col-sm-12 col-md-6">
                <div id="tickets-table_length" class="dataTables_length">
                  <label class="d-inline-flex align-items-center">
                    Show
                    <b-form-select class="form-control form-control-sm form-select form-select-sm" v-model="perPage"
                      size="sm" :options="pageOptions"></b-form-select>entries
                  </label>
                </div>
              </div>
              <div class="col-sm-12 col-md-6">
                <div id="tickets-table_filter" class="dataTables_filter text-md-end">
                  <label class="d-inline-flex align-items-center">
                    Search:
                    <b-form-input v-model="filter" type="search" placeholder="Search..."
                      class="form-control form-control-sm ml-2"></b-form-input>
                  </label>
                </div>
              </div>
              <div style="margin-top: 15px;">
                数据共 {{ this.tableData.length }} 条 &nbsp; <b-button variant="outline-primary"
                  @click="outputXLSX">导出报表</b-button>
                <b-button variant="outline-primary" @click="outputAbnormalData"
                  style="margin-left: 10px;">导出异常数据</b-button>
              </div>
            </div>

            <div class="table-responsive mb-0 datatables">
              <b-table :items="tableData" :fields="fields" responsive="sm" :per-page="perPage"
                :current-page="currentPage" :sort-by.sync="sortBy" :sort-desc.sync="sortDesc" :filter="filter"
                :filter-included-fields="filterOn" @filtered="onFiltered"></b-table>
            </div>

            <div class="row">
              <div class="col">
                <div class="dataTables_paginate paging_simple_numbers float-end">
                  <ul class="pagination pagination-rounded mb-0">
                    <b-pagination v-model="currentPage" :total-rows="rows" :per-page="perPage"></b-pagination>
                  </ul>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>