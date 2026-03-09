<template>
  <div class="reports">
    <div class="page-header">
      <h2>工时报表</h2>
      <p>查看和分析员工工时统计</p>
      <el-button type="primary" :icon="Download">导出报表</el-button>
    </div>

    <el-row :gutter="20">
      <el-col :xs="24" :lg="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <h3>工时趋势</h3>
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                value-format="YYYY-MM-DD"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
              />
            </div>
          </template>
          <div ref="trendChartRef" class="chart"></div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :lg="8">
        <el-card class="stats-card">
          <template #header>
            <h3>统计概览</h3>
          </template>
          <div class="stats-list">
            <div class="stat-item">
              <div class="stat-label">总出勤天数</div>
              <div class="stat-value">{{ stats.totalDays }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">总工时</div>
              <div class="stat-value">{{ stats.totalHours }}h</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">平均工时</div>
              <div class="stat-value">{{ stats.avgHours }}h</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">加班总时长</div>
              <div class="stat-value">{{ stats.totalOvertime }}h</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">迟到次数</div>
              <div class="stat-value">{{ stats.lateCount }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">早退次数</div>
              <div class="stat-value">{{ stats.earlyLeaveCount }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <h3>工时明细</h3>
          <div class="table-actions">
            <el-select v-model="filters.department" placeholder="全部部门" style="width: 150px" clearable>
              <el-option label="全部部门" value="" />
              <el-option label="技术部" value="技术部" />
              <el-option label="市场部" value="市场部" />
              <el-option label="人力资源" value="人力资源" />
            </el-select>
            <el-button type="primary" :icon="Search" @click="loadReports">查询</el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="reports" stripe v-loading="loading">
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="department" label="部门" />
        <el-table-column prop="totalDays" label="出勤天数" />
        <el-table-column prop="totalHours" label="总工时" />
        <el-table-column prop="dayOvertime" label="白天加班" />
        <el-table-column prop="nightOvertime" label="晚上加班" />
        <el-table-column prop="subsidy" label="夜班补贴" />
        <el-table-column label="操作" width="80">
          <template #default>
            <el-button type="primary" link>详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          layout="total, prev, pager, next, jumper"
          @current-change="loadReports"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Search } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { reportApi } from '@/api'

const trendChartRef = ref(null)
const loading = ref(false)
const dateRange = ref([])
const reports = ref([])

const filters = reactive({
  department: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const stats = ref({
  totalDays: 0,
  totalHours: 0,
  avgHours: 0,
  totalOvertime: 0,
  lateCount: 0,
  earlyLeaveCount: 0
})

const loadReports = async () => {
  loading.value = true
  try {
    const response = await reportApi.getStats({
      ...filters,
      page: pagination.page,
      pageSize: pagination.pageSize,
      startDate: dateRange.value?.[0],
      endDate: dateRange.value?.[1]
    })
    reports.value = response.reports || []
    pagination.total = response.total || 0
    stats.value = response.stats || stats.value
  } catch (error) {
    ElMessage.error('加载报表失败')
  } finally {
    loading.value = false
  }
}

const initChart = async () => {
  await nextTick()
  if (!trendChartRef.value) return
  
  try {
    const data = await reportApi.getWorkHours({
      startDate: dateRange.value?.[0],
      endDate: dateRange.value?.[1]
    })
    
    const chart = echarts.init(trendChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['工时', '加班'] },
      xAxis: {
        type: 'category',
        data: data.labels || ['周一', '周二', '周三', '周四', '周五']
      },
      yAxis: { type: 'value' },
      series: [
        {
          name: '工时',
          type: 'line',
          data: data.workHours || [8, 7.5, 8.5, 9, 7],
          smooth: true,
          itemStyle: { color: '#409EFF' }
        },
        {
          name: '加班',
          type: 'line',
          data: data.overtime || [1, 0.5, 2, 1.5, 0],
          smooth: true,
          itemStyle: { color: '#67C23A' }
        }
      ]
    })
  } catch (error) {
    console.error('初始化图表失败:', error)
  }
}

onMounted(() => {
  loadReports()
  initChart()
})
</script>

<style scoped>
.reports {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  font-size: 24px;
  margin-bottom: 8px;
}

.page-header p {
  color: #909399;
  margin-right: auto;
}

.chart-card,
.stats-card,
.table-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  font-size: 16px;
  font-weight: bold;
}

.chart {
  height: 350px;
}

.stats-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
}

.stat-label {
  color: #606266;
  font-size: 14px;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.table-actions {
  display: flex;
  gap: 10px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  padding: 20px 0;
}
</style>