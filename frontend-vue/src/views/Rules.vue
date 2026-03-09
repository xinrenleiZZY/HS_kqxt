<template>
  <div class="rules">
    <div class="page-header">
      <h2>考勤规则</h2>
      <p>设置和管理考勤规则</p>
      <el-button type="primary" :icon="Check" @click="saveRules">保存规则</el-button>
    </div>

    <el-card class="rules-card">
      <el-form :model="rules" label-width="150px" v-loading="loading">
        <el-divider content-position="left">工作时间</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="上班时间">
              <el-time-picker
                v-model="rules.workStartTime"
                format="HH:mm"
                value-format="HH:mm"
                placeholder="选择时间"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="下班时间">
              <el-time-picker
                v-model="rules.workEndTime"
                format="HH:mm"
                value-format="HH:mm"
                placeholder="选择时间"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">考勤阈值</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="迟到阈值">
              <el-input-number
                v-model="rules.lateThreshold"
                :min="0"
                :max="60"
                controls-position="right"
              />
              <span style="margin-left: 8px">分钟</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="早退阈值">
              <el-input-number
                v-model="rules.earlyLeaveThreshold"
                :min="0"
                :max="60"
                controls-position="right"
              />
              <span style="margin-left: 8px">分钟</span>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">午休时间</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="午休开始">
              <el-time-picker
                v-model="rules.lunchStartTime"
                format="HH:mm"
                value-format="HH:mm"
                placeholder="选择时间"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="午休结束">
              <el-time-picker
                v-model="rules.lunchEndTime"
                format="HH:mm"
                value-format="HH:mm"
                placeholder="选择时间"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">加班设置</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="加班开始时间">
              <el-time-picker
                v-model="rules.overtimeStartTime"
                format="HH:mm"
                value-format="HH:mm"
                placeholder="选择时间"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="每日标准工时">
              <el-input-number
                v-model="rules.dailyStandardHours"
                :min="0"
                :max="24"
                :step="0.5"
                controls-position="right"
              />
              <span style="margin-left: 8px">小时</span>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">工作日设置</el-divider>
        
        <el-form-item label="工作日">
          <el-checkbox-group v-model="workDays">
            <el-checkbox label="1">周一</el-checkbox>
            <el-checkbox label="2">周二</el-checkbox>
            <el-checkbox label="3">周三</el-checkbox>
            <el-checkbox label="4">周四</el-checkbox>
            <el-checkbox label="5">周五</el-checkbox>
            <el-checkbox label="6">周六</el-checkbox>
            <el-checkbox label="7">周日</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="preview-card">
      <template #header>
        <h3>规则预览</h3>
      </template>
      
      <el-descriptions :column="2" border>
        <el-descriptions-item label="工作时段">
          {{ rules.workStartTime }} - {{ rules.workEndTime }}
        </el-descriptions-item>
        <el-descriptions-item label="标准工时">
          {{ rules.dailyStandardHours }} 小时
        </el-descriptions-item>
        <el-descriptions-item label="午休时段">
          {{ rules.lunchStartTime }} - {{ rules.lunchEndTime }}
        </el-descriptions-item>
        <el-descriptions-item label="加班开始">
          {{ rules.overtimeStartTime }}
        </el-descriptions-item>
        <el-descriptions-item label="迟到阈值">
          {{ rules.lateThreshold }} 分钟
        </el-descriptions-item>
        <el-descriptions-item label="早退阈值">
          {{ rules.earlyLeaveThreshold }} 分钟
        </el-descriptions-item>
        <el-descriptions-item label="工作日" :span="2">
          {{ workDaysText }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Check } from '@element-plus/icons-vue'
import { rulesApi } from '@/api'

const loading = ref(false)

const rules = reactive({
  workStartTime: '09:00',
  workEndTime: '18:00',
  lateThreshold: 15,
  earlyLeaveThreshold: 15,
  lunchStartTime: '12:00',
  lunchEndTime: '13:00',
  overtimeStartTime: '19:00',
  dailyStandardHours: 8.0
})

const workDays = ref(['1', '2', '3', '4', '5'])

const workDaysText = computed(() => {
  const days = {
    '1': '周一',
    '2': '周二',
    '3': '周三',
    '4': '周四',
    '5': '周五',
    '6': '周六',
    '7': '周日'
  }
  return workDays.value.map(day => days[day]).join('、')
})

const loadRules = async () => {
  loading.value = true
  try {
    const data = await rulesApi.getRules()
    if (data) {
      Object.assign(rules, data)
      if (data.workDays) {
        workDays.value = data.workDays.split(',')
      }
    }
  } catch (error) {
    ElMessage.error('加载规则失败')
  } finally {
    loading.value = false
  }
}

const saveRules = async () => {
  loading.value = true
  try {
    await rulesApi.updateRules({
      ...rules,
      workDays: workDays.value.join(',')
    })
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadRules()
})
</script>

<style scoped>
.rules {
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

.rules-card,
.preview-card {
  margin-bottom: 20px;
}

.rules-card h3,
.preview-card h3 {
  font-size: 16px;
  font-weight: bold;
}
</style>