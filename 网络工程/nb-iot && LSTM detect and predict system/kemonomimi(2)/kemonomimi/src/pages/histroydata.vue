<template>
  <div class="history-data-container">
    <h4 class="title">数据条目</h4>
    
    <div class="controls-row">
      <div class="entries-control">
        Show 
        <select v-model="perPage" class="entries-select">
          <option v-for="option in pageOptions" :key="option" :value="option">
            {{ option }}
          </option>
        </select>
        entries
      </div>
      
      <div class="search-control">
        Search: 
        <input 
          v-model="filter" 
          type="search" 
          class="search-input"
          placeholder="Search..."
        >
      </div>
    </div>

    <div class="data-info">
      数据共 {{ tableData.length }} 条
      <div class="button-group">
        <button class="action-button" @click="outputXLSX">导出报表</button>
        <button class="action-button" @click="outputAbnormalData">导出异常数据</button>
      </div>
    </div>

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th 
              v-for="field in fields" 
              :key="field.key"
              @click="sortBy = field.key; sortDesc = !sortDesc"
              class="sortable"
            >
              {{ field.label || field.key }}
              <span class="sort-icon">⌃</span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filteredData" :key="item.时间">
            <td>{{ item.设备ID }}</td>
            <td>{{ item.时间 }}</td>
            <td>{{ item.温度 }}</td>
            <td>{{ item.湿度 }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pagination">
      <button class="page-button" @click="currentPage = 1">«</button>
      <button class="page-button" @click="currentPage = Math.max(1, currentPage - 1)">‹</button>
      
      <template v-for="n in pageNumbers" :key="n">
        <button 
          :class="['page-button', { active: currentPage === n }]"
          @click="currentPage = n"
        >
          {{ n }}
        </button>
      </template>
      
      <button class="page-button" @click="currentPage = Math.min(totalPages, currentPage + 1)">›</button>
      <button class="page-button" @click="currentPage = totalPages">»</button>
    </div>
  </div>
</template>

<script>
import * as XLSX from 'xlsx';

export default {
  name: 'HistoryData',
  data() {
    return {
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
      lastModifiedTime: null,
      fileCheckInterval: null
    };
  },
  computed: {
    rows() {
      return this.tableData.length;
    },
    filteredData() {
      let data = [...this.tableData];
      
      // 搜索过滤
      if (this.filter) {
        const searchTerm = this.filter.toLowerCase();
        data = data.filter(item => 
          Object.values(item).some(val => 
            String(val).toLowerCase().includes(searchTerm)
          )
        );
      }
      
      // 排序
      if (this.sortBy) {
        data.sort((a, b) => {
          let aVal = a[this.sortBy];
          let bVal = b[this.sortBy];
          if (typeof aVal === 'string') aVal = aVal.toLowerCase();
          if (typeof bVal === 'string') bVal = bVal.toLowerCase();
          return this.sortDesc ? (bVal > aVal ? 1 : -1) : (aVal > bVal ? 1 : -1);
        });
      }
      
      // 分页
      const start = (this.currentPage - 1) * this.perPage;
      return data.slice(start, start + this.perPage);
    },
    totalPages() {
      return Math.ceil(this.tableData.length / this.perPage);
    },
    pageNumbers() {
      const total = this.totalPages;
      const current = this.currentPage;
      const delta = 2; // 当前页码前后显示的页数
      
      let start = Math.max(1, current - delta);
      let end = Math.min(total, current + delta);
      
      // 调整开始和结束位置以显示更多页码
      if (start > 1) {
        if (start > 2) {
          start = Math.max(1, end - 4);
        }
      }
      
      if (end < total) {
        if (end < total - 1) {
          end = Math.min(total, start + 4);
        }
      }
      
      const range = [];
      for (let i = start; i <= end; i++) {
        range.push(i);
      }
      
      return range;
    }
  },
  mounted() {
    this.readExcelFile();
    this.fileCheckInterval = setInterval(() => {
      this.checkForUpdates();
    }, 5000);
  },
  beforeDestroy() {
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
      const filePath = '/mqtt_data.xlsx';
      fetch(filePath)
        .then(response => {
          if (!response.ok) throw new Error('文件未找到！');
          return response.arrayBuffer();
        })
        .then(buffer => {
          const workbook = XLSX.read(buffer, { type: 'array' });
          const sheetName = workbook.SheetNames[0];
          const worksheet = workbook.Sheets[sheetName];
          const excelData = XLSX.utils.sheet_to_json(worksheet);

          this.tableData = excelData.map(row => ({
            设备ID: row['deviceId'],
            时间: row['Timestamp'] || '未知时间',
            温度: parseFloat(row['Temperature'] || 0).toFixed(2),
            湿度: parseFloat(row['Humidity'] || 0).toFixed(2)
          }));
          
          this.totalRows = this.tableData.length;
          localStorage.setItem('mqttData', JSON.stringify(this.tableData));
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
      const filePath = '/mqtt_data.xlsx';
      fetch(filePath, { method: 'HEAD' })
        .then(response => {
          if (!response.ok) throw new Error('无法获取文件信息！');
          const lastModified = response.headers.get('Last-Modified');
          if (lastModified && lastModified !== this.lastModifiedTime) {
            this.lastModifiedTime = lastModified;
            console.log('检测到文件更新，重新加载数据...');
            this.readExcelFile();
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

      const processedData = this.tableData.filter(element => {
        const curTemp = parseFloat(element.温度);
        const curHumi = parseFloat(element.湿度);
        return (curTemp > TEMP_MAX || curTemp < TEMP_MIN || 
                curHumi > HUMI_MAX || curHumi < HUMI_MIN);
      }).map(element => {
        const curTemp = parseFloat(element.温度);
        const curHumi = parseFloat(element.湿度);
        const status = [];
        
        if (curTemp > TEMP_MAX || curTemp < TEMP_MIN) status.push('温度异常');
        if (curHumi > HUMI_MAX || curHumi < HUMI_MIN) status.push('湿度异常');
        
        return {
          设备ID: element.设备ID,
          时间: element.时间,
          温度: element.温度,
          湿度: element.湿度,
          状态: status.join('、'),
          正常温度范围: `${TEMP_MIN}℃ ~ ${TEMP_MAX}℃`,
          正常湿度范围: `${HUMI_MIN}% ~ ${HUMI_MAX}%`
        };
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

<style scoped>
.history-data-container {
  padding: 20px;
  background-color: #fff;
  max-width: 1600px;
  margin: 0 auto;
  width: 95%;
}

.title {
  font-size: 18px;
  margin-bottom: 20px;
  color: #333;
}

.controls-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.entries-control {
  display: flex;
  align-items: center;
  gap: 8px;
}

.entries-select {
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 70px;
}

.search-control {
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-input {
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 200px;
}

.data-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 15px 0;
}

.button-group {
  display: flex;
  gap: 10px;
}

.action-button {
  padding: 6px 12px;
  background-color: #f0f2ff;
  border: 1px solid #d4d6e4;
  border-radius: 4px;
  color: #5c6ac4;
  cursor: pointer;
}

.action-button:hover {
  background-color: #e6e8ff;
}

.data-table {
  width: 100%;
  min-width: 1200px;
  border-collapse: collapse;
  margin: 20px 0;
}

.data-table th,
.data-table td {
  padding: 12px 20px;
  white-space: nowrap;
}

.data-table th:nth-child(1),
.data-table td:nth-child(1) {
  width: 15%;
}

.data-table th:nth-child(2),
.data-table td:nth-child(2) {
  width: 35%;
}

.data-table th:nth-child(3),
.data-table td:nth-child(3),
.data-table th:nth-child(4),
.data-table td:nth-child(4) {
  width: 25%;
}

.data-table th {
  background-color: #f8f9fa;
  padding: 12px;
  text-align: left;
  border-bottom: 2px solid #dee2e6;
  color: #495057;
  font-weight: 500;
  cursor: pointer;
}

.data-table td {
  padding: 12px;
  border-bottom: 1px solid #dee2e6;
  color: #212529;
}

.sortable {
  position: relative;
  padding-right: 20px;
}

.sort-icon {
  position: absolute;
  right: 6px;
  opacity: 0.3;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  gap: 4px;
  margin-top: 20px;
  padding: 10px 0;
}

.page-button {
  min-width: 32px;
  height: 32px;
  padding: 0 4px;
  margin: 0 2px;
  border: 1px solid #dee2e6;
  background-color: #fff;
  color: #6c757d;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.page-button.active {
  background-color: #6366f1;
  color: #fff;
  border-color: #6366f1;
}

.page-button:hover:not(.active) {
  background-color: #f8f9fa;
}
</style>
