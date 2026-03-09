<template>
  <div class="dashboard">
    <div class="page-header">
      <h2>仪表盘</h2>
      <p>欢迎回来，今天是 {{ currentDate }}</p>
      <div class="header-actions">
        <el-button type="primary" :icon="Download">导出报表</el-button>
        <el-button type="success" :icon="Refresh" @click="loadData">刷新数据</el-button>
      </div>
    </div>

    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <p class="stat-label">总员工数</p>
              <h3 class="stat-value">{{ stats.totalEmployees }}</h3>
              <p class="stat-trend positive">
                <el-icon><TrendCharts /></el-icon>
                <span>2.4%</span>
                <span class="stat-trend-text">较上月</span>
              </p>
            </div>
            <div class="stat-icon">
              <el-icon color="#409EFF"><User /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <p class="stat-label">今日出勤</p>
              <h3 class="stat-value">{{ stats.todayAttendance }}</h3>
              <p class="stat-trend positive">
                <el-icon><TrendCharts /></el-icon>
                <span>5.2%</span>
                <span class="stat-trend-text">较昨日</span>
              </p>
            </div>
            <div class="stat-icon">
              <el-icon color="#67C23A"><CircleCheck /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <p class="stat-label">迟到人数</p>
              <h3 class="stat-value">{{ stats.lateCount }}</h3>
              <p class="stat-trend negative">
                <el-icon><TrendCharts /></el-icon>
                <span>1.8%</span>
                <span class="stat-trend-text">较昨日</span>
              </p>
            </div>
            <div class="stat-icon">
              <el-icon color="#E6A23C"><Warning /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <p class="stat-label">加班时长</p>
              <h3 class="stat-value">{{ stats.overtimeHours }}h</h3>
              <p class="stat-trend positive">
                <el-icon><TrendCharts /></el-icon>
                <span>3.1%</span>
                <span class="stat-trend-text">较昨日</span>
              </p>
            </div>
            <div class="stat-icon">
              <el-icon color="#36CFC9"><Clock /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <h3>工时统计</h3>
          </template>
          <div ref="workHoursChartRef" class="chart"></div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <h3>部门分布</h3>
          </template>
          <div ref="departmentChartRef" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="records-card">
      <template #header>
        <div class="card-header">
          <h3>最近打卡记录</h3>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索员工..."
            style="width: 200px"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
      </template>
      
      <el-table :data="recentRecords" stripe>
        <el-table-column label="员工" width="200">
          <template #default="{ row }">
            <div class="employee-cell">
              <el-avatar :size="32" :src="row.avatar" />
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="department" label="部门" />
        <el-table-column prop="type" label="打卡类型" />
        <el-table-column prop="time" label="时间" />
        <el-table-column label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default>
            <el-button type="primary" link>详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          @current-change="loadRecentRecords"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Download, Refresh, User, CircleCheck, Warning, Clock,
  TrendCharts, Search
} from '@element-plus/icons-vue'
import { attendanceApi, reportApi } from '@/api'

const workHoursChartRef = ref(null)
const departmentChartRef = ref(null)
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const stats = ref({
  totalEmployees: 0,
  todayAttendance: 0,
  lateCount: 0,
  overtimeHours: 0
})

const recentRecords = ref([])
const currentDate = ref('')

const getStatusType = (status) => {
  if (status === '正常') return 'success'
  if (status === '迟到' || status === '早退') return 'warning'
  return 'info'
}

const loadData = async () => {
  try {
    const [todayStats, recent] = await Promise.all([
      attendanceApi.getTodayStats(),
      attendanceApi.getRecentRecords()
    ])
    
    stats.value = {
      totalEmployees: todayStats.totalEmployees || 0,
      todayAttendance: todayStats.todayAttendance || 0,
      lateCount: todayStats.lateCount || 0,
      overtimeHours: todayStats.overtimeHours || 0
    }
    
    recentRecords.value = recent.records || []
    total.value = recent.total || 0
  } catch (error) {
    ElMessage.error('加载数据失败')
  }
}

const loadRecentRecords = async (page = 1) => {
  currentPage.value = page
  try {
    const response = await attendanceApi.getRecentRecords({
      page: page,
      pageSize: pageSize.value,
      keyword: searchKeyword.value
    })
    recentRecords.value = response.records || []
    total.value = response.total || 0
  } catch (error) {
    ElMessage.error('加载记录失败')
  }
}

const initCharts = async () => {
  await nextTick()
  
  try {
    const workHoursData = await reportApi.getWorkHours()
    const departmentData = await reportApi.getDepartmentStats()
    
    if (workHoursChartRef.value) {
      const workHoursChart = echarts.init(workHoursChartRef.value)
      workHoursChart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: {
          type: 'category',
          data: workHoursData.labels || ['周一', '周二', '周三', '周四', '周五']
        },
        yAxis: { type: 'value' },
        series: [{
          name: '工时',
          type: 'bar',
          data: workHoursData.values || [8, 7.5, 8.5, 9, 7],
          itemStyle: { color: '#409EFF' }
        }]
      })
    }
    
    if (departmentChartRef.value) {
      const departmentChart = echarts.init(departmentChartRef.value)
      departmentChart.setOption({
        tooltip: { trigger: 'item' },
        legend: { orient: 'vertical', left: 'left' },
        series: [{
          name: '部门分布',
          type: 'pie',
          radius: '50%',
          data: departmentData.data || [
            { value: 30, name: '技术部' },
            { value: 20, name: '市场部' },
            { value: 10, name: '人事部' }
          ],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      })
    }
  } catch (error) {
    console.error('初始化图表失败:', error)
  }
}

onMounted(() => {
  const now = new Date()
  currentDate.value = `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`
  loadData()
  initCharts()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  font-size: 24px;
  margin-bottom: 8px;
}

.page-header p {
  color: #909399;
  margin-bottom: 16px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  color: #909399;
  font-size: 14px;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 8px;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
}

.stat-trend.positive {
  color: #67C23A;
}

.stat-trend.negative {
  color: #F56C6C;
}

.stat-trend-text {
  color: #909399;
}

.stat-icon {
  font-size: 48px;
  opacity: 0.1;
}

.charts-row {
  margin-bottom: 20px;
}

.chart-card {
  height: 400px;
}

.chart-card h3 {
  font-size: 16px;
  font-weight: bold;
}

.chart {
  height: 320px;
}

.records-card {
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

.employee-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  padding: 20px 0;
}
</style>