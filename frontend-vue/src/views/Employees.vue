<template>
  <div class="employees">
    <div class="page-header">
      <h2>员工管理</h2>
      <p>管理员工信息和档案</p>
      <el-button type="primary" :icon="Plus" @click="showAddDialog">添加员工</el-button>
    </div>

    <el-card class="table-card">
      <div class="table-header">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索员工..."
          style="width: 300px"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      
      <el-table :data="employees" stripe v-loading="loading">
        <el-table-column prop="employeeId" label="员工编号" width="120" />
        <el-table-column label="姓名" width="150">
          <template #default="{ row }">
            <div class="employee-cell">
              <el-avatar :size="32" :src="row.avatar" />
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="department" label="部门" />
        <el-table-column prop="position" label="职位" />
        <el-table-column prop="hireDate" label="入职日期" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '在职' : '离职' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" link>查看</el-button>
            <el-button type="warning" link>编辑</el-button>
            <el-button type="danger" link>删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          layout="total, prev, pager, next, jumper"
          @current-change="loadEmployees"
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="employeeForm" :rules="formRules" label-width="100px">
        <el-form-item label="员工编号" prop="employeeId">
          <el-input v-model="employeeForm.employeeId" />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="employeeForm.name" />
        </el-form-item>
        <el-form-item label="部门" prop="department">
          <el-select v-model="employeeForm.department" style="width: 100%">
            <el-option label="技术部" value="技术部" />
            <el-option label="市场部" value="市场部" />
            <el-option label="人力资源" value="人力资源" />
          </el-select>
        </el-form-item>
        <el-form-item label="职位" prop="position">
          <el-input v-model="employeeForm.position" />
        </el-form-item>
        <el-form-item label="入职日期" prop="hireDate">
          <el-date-picker
            v-model="employeeForm.hireDate"
            type="date"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="employeeForm.status">
            <el-radio label="active">在职</el-radio>
            <el-radio label="inactive">离职</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEmployee">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { employeeApi } from '@/api'

const loading = ref(false)
const employees = ref([])
const searchKeyword = ref('')
const dialogVisible = ref(false)
const dialogTitle = computed(() => '添加员工')

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const employeeForm = reactive({
  employeeId: '',
  name: '',
  department: '',
  position: '',
  hireDate: '',
  status: 'active'
})

const formRules = {
  employeeId: [{ required: true, message: '请输入员工编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  department: [{ required: true, message: '请选择部门', trigger: 'change' }],
  position: [{ required: true, message: '请输入职位', trigger: 'blur' }],
  hireDate: [{ required: true, message: '请选择入职日期', trigger: 'change' }]
}

const loadEmployees = async () => {
  loading.value = true
  try {
    const response = await employeeApi.getList({
      page: pagination.page,
      pageSize: pagination.pageSize,
      keyword: searchKeyword.value
    })
    employees.value = response.employees || []
    pagination.total = response.total || 0
  } catch (error) {
    ElMessage.error('加载员工列表失败')
  } finally {
    loading.value = false
  }
}

const showAddDialog = () => {
  Object.assign(employeeForm, {
    employeeId: '',
    name: '',
    department: '',
    position: '',
    hireDate: '',
    status: 'active'
  })
  dialogVisible.value = true
}

const saveEmployee = async () => {
  try {
    await employeeApi.create(employeeForm)
    ElMessage.success('添加成功')
    dialogVisible.value = false
    loadEmployees()
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

onMounted(() => {
  loadEmployees()
})
</script>

<style scoped>
.employees {
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

.table-card {
  margin-bottom: 20px;
}

.table-header {
  margin-bottom: 16px;
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