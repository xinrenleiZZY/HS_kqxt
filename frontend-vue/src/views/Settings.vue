<template>
  <div class="settings">
    <div class="page-header">
      <h2>系统设置</h2>
      <p>配置系统参数和偏好设置</p>
    </div>

    <el-row :gutter="20">
      <el-col :xs="24" :lg="16">
        <el-card class="settings-card">
          <template #header>
            <h3>基本设置</h3>
          </template>
          
          <el-form :model="settings" label-width="120px">
            <el-form-item label="系统名称">
              <el-input v-model="settings.systemName" />
            </el-form-item>
            
            <el-form-item label="系统Logo">
              <el-upload
                class="logo-uploader"
                :show-file-list="false"
                :on-change="handleLogoChange"
                accept="image/*"
              >
                <img v-if="settings.logo" :src="settings.logo" class="logo-preview" />
                <el-icon v-else class="logo-uploader-icon"><Plus /></el-icon>
              </el-upload>
            </el-form-item>
            
            <el-form-item label="主题颜色">
              <el-color-picker v-model="settings.themeColor" />
            </el-form-item>
            
            <el-form-item label="每页显示">
              <el-select v-model="settings.pageSize">
                <el-option label="10条" :value="10" />
                <el-option label="20条" :value="20" />
                <el-option label="50条" :value="50" />
                <el-option label="100条" :value="100" />
              </el-select>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :lg="8">
        <el-card class="info-card">
          <template #header>
            <h3>系统信息</h3>
          </template>
          
          <el-descriptions :column="1" border>
            <el-descriptions-item label="系统版本">
              v1.0.0
            </el-descriptions-item>
            <el-descriptions-item label="Vue版本">
              3.4.0
            </el-descriptions-item>
            <el-descriptions-item label="Element版本">
              2.4.0
            </el-descriptions-item>
            <el-descriptions-item label="最后更新">
              2024-01-01
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="actions-card">
      <template #header>
        <h3>操作</h3>
      </template>
      
      <div class="action-buttons">
        <el-button type="primary" :icon="Check" @click="saveSettings">
          保存设置
        </el-button>
        <el-button :icon="RefreshLeft" @click="resetSettings">
          重置默认
        </el-button>
        <el-button type="warning" :icon="Download" @click="exportSettings">
          导出配置
        </el-button>
        <el-button type="success" :icon="Upload" @click="importSettings">
          导入配置
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Check, RefreshLeft, Download, Upload } from '@element-plus/icons-vue'

const settings = reactive({
  systemName: '考勤管理系统',
  logo: '',
  themeColor: '#409EFF',
  pageSize: 10
})

const handleLogoChange = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    settings.logo = e.target.result
  }
  reader.readAsDataURL(file.raw)
}

const saveSettings = () => {
  localStorage.setItem('systemSettings', JSON.stringify(settings))
  ElMessage.success('设置保存成功')
}

const resetSettings = () => {
  Object.assign(settings, {
    systemName: '考勤管理系统',
    logo: '',
    themeColor: '#409EFF',
    pageSize: 10
  })
  ElMessage.success('已重置为默认设置')
}

const exportSettings = () => {
  const data = JSON.stringify(settings, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'settings.json'
  link.click()
  URL.revokeObjectURL(url)
  ElMessage.success('配置导出成功')
}

const importSettings = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  input.onchange = (e) => {
    const file = e.target.files[0]
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target.result)
        Object.assign(settings, data)
        ElMessage.success('配置导入成功')
      } catch (error) {
        ElMessage.error('配置文件格式错误')
      }
    }
    reader.readAsText(file)
  }
  input.click()
}

onMounted(() => {
  const saved = localStorage.getItem('systemSettings')
  if (saved) {
    Object.assign(settings, JSON.parse(saved))
  }
})
</script>

<style scoped>
.settings {
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

.settings-card,
.info-card,
.actions-card {
  margin-bottom: 20px;
}

.settings-card h3,
.info-card h3,
.actions-card h3 {
  font-size: 16px;
  font-weight: bold;
}

.logo-uploader {
  width: 100px;
  height: 100px;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s;
}

.logo-uploader:hover {
  border-color: #409EFF;
}

.logo-preview {
  width: 100px;
  height: 100px;
  object-fit: cover;
}

.logo-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.action-buttons {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}
</style>