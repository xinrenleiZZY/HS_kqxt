<template>
  <div class="attendance">
    <div class="page-header">
      <h2>打卡记录</h2>
      <p>查看和管理员工的打卡记录</p>
    </div>

    <el-card class="filter-card">
      <el-form :inline="true" :model="filters">
        <el-form-item label="部门">
          <el-select v-model="filters.department" placeholder="全部部门" clearable>
            <el-option label="全部部门" value="" />
            <el-option label="技术部" value="技术部" />
            <el-option label="市场部" value="市场部" />
            <el-option label="人力资源" value="人力资源" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="日期">
          <el-date-picker
            v-model="filters.date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        
        <el-form-item label="员工">
          <el-input
            v-model="filters.keyword"
            placeholder="搜索员工..."
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="loadRecords">搜索</el-button>
          <el-button :icon="Refresh" @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <el-table :data="records" stripe v-loading="loading">
        <el-table-column label="员工" width="200">
          <template #default="{ row }">
            <div class="employee-cell">
              <el-avatar :size="32" :src="row.avatar" />
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="department" label="部门" />
        <el-table-column prop="checkInTime" label="上班时间" />
        <el-table-column prop="checkOutTime" label="下班时间" />
        <el-table-column prop="workHours" label="工作时长" />
        <el-table-column label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
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
          @current-change="loadRecords"
          @size-change="loadRecords"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import { attendanceApi } from '@/api'

const loading = ref(false)
const records = ref([])

const filters = reactive({
  department: '',
  date: '',
  keyword: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const getStatusType = (status) => {
  if (status === '正常') return 'success'
  if (status === '迟到' || status === '早退') return 'warning'
  return 'info'
}

const loadRecords = async () => {
  loading.value = true
  try {
    const response = await attendanceApi.getRecords({
      ...filters,
      page: pagination.page,
      pageSize: pagination.pageSize
    })
    records.value = response.records || []
    pagination.total = response.total || 0
  } catch (error) {
    ElMessage.error('加载记录失败')
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.department = ''
  filters.date = ''
  filters.keyword = ''
  pagination.page = 1
  loadRecords()
}

onMounted(() => {
  loadRecords()
})
</script>

<style scoped>
.attendance {
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
}

.filter-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
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