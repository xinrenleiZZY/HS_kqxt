<template>
  <div class="excel-processor">
    <div class="page-header">
      <h2>Excel打卡记录处理</h2>
      <p>导入、处理和导出打卡记录Excel文件</p>
    </div>

    <el-row :gutter="20">
      <el-col :xs="24" :lg="12">
        <el-card class="upload-card">
          <template #header>
            <h3>文件上传</h3>
          </template>
          
          <el-upload
            ref="uploadRef"
            class="upload-area"
            drag
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            accept=".xlsx,.xls"
          >
            <el-icon class="upload-icon"><UploadFilled /></el-icon>
            <div class="upload-text">
              <p>将文件拖到此处，或<em>点击上传</em></p>
              <p class="upload-tip">支持 .xlsx 和 .xls 格式</p>
            </div>
          </el-upload>
          
          <div v-if="uploadedFile" class="file-info">
            <el-icon><Document /></el-icon>
            <span>{{ uploadedFile.name }}</span>
            <el-button type="danger" :icon="Delete" circle @click="clearFile" />
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :lg="12">
        <el-card class="options-card">
          <template #header>
            <h3>处理选项</h3>
          </template>
          
          <el-form :model="options" label-width="120px">
            <el-form-item label="输出格式">
              <el-radio-group v-model="options.format">
                <el-radio label="xlsx">Excel (.xlsx)</el-radio>
                <el-radio label="csv">CSV (.csv)</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="处理脚本">
              <el-checkbox-group v-model="options.scripts">
                <el-checkbox label="1分割">数据分割</el-checkbox>
                <el-checkbox label="2时间预处理">时间预处理</el-checkbox>
                <el-checkbox label="3分列时间">时间分列</el-checkbox>
                <el-checkbox label="4全班">班次处理</el-checkbox>
                <el-checkbox label="66">夜班补贴</el-checkbox>
                <el-checkbox label="6">数据汇总</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="action-card">
      <div class="action-buttons">
        <el-button
          type="primary"
          size="large"
          :loading="processing"
          :disabled="!uploadedFile"
          @click="processExcel"
        >
          <el-icon><Operation /></el-icon>
          处理Excel文件
        </el-button>
        
        <el-button
          type="success"
          size="large"
          :disabled="!processedFileId"
          @click="downloadProcessedFile"
        >
          <el-icon><Download /></el-icon>
          下载处理结果
        </el-button>
      </div>
      
      <el-progress
        v-if="processing"
        :percentage="processProgress"
        :status="processStatus"
      >
        <span>{{ processMessage }}</span>
      </el-progress>
    </el-card>

    <el-card v-if="processResult" class="result-card">
      <template #header>
        <h3>处理结果</h3>
      </template>
      
      <el-descriptions :column="2" border>
        <el-descriptions-item label="状态">
          <el-tag :type="processResult.status === 'success' ? 'success' : 'danger'">
            {{ processResult.status === 'success' ? '成功' : '失败' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="文件ID">
          {{ processResult.fileId || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="输出格式" :span="2">
          {{ options.format.toUpperCase() }}
        </el-descriptions-item>
        <el-descriptions-item v-if="processResult.error" label="错误信息" :span="2">
          <el-text type="danger">{{ processResult.error }}</el-text>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="files-card">
      <template #header>
        <h3>临时文件</h3>
      </template>
      
      <el-table :data="tempFiles" stripe>
        <el-table-column prop="name" label="文件名" />
        <el-table-column prop="size" label="大小" width="120">
          <template #default="{ row }">
            {{ formatFileSize(row.size) }}
          </template>
        </el-table-column>
        <el-table-column prop="modified" label="修改时间" width="180" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" link :icon="Download" @click="downloadTempFile(row.name)">
              下载
            </el-button>
            <el-button type="danger" link :icon="Delete" @click="deleteTempFile(row.name)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  UploadFilled, Document, Delete, Operation, Download
} from '@element-plus/icons-vue'
import { fileApi } from '@/api'

const uploadRef = ref(null)
const uploadedFile = ref(null)
const processing = ref(false)
const processProgress = ref(0)
const processStatus = ref('')
const processMessage = ref('')
const processedFileId = ref('')
const processResult = ref(null)
const tempFiles = ref([])

const options = reactive({
  format: 'xlsx',
  scripts: ['1分割', '2时间预处理', '3分列时间', '4全班', '66', '6']
})

const handleFileChange = (file) => {
  uploadedFile.value = file
  processedFileId.value = ''
  processResult.value = null
}

const clearFile = () => {
  uploadedFile.value = null
  uploadRef.value?.clearFiles()
}

const processExcel = async () => {
  if (!uploadedFile.value) {
    ElMessage.warning('请先上传文件')
    return
  }

  processing.value = true
  processProgress.value = 0
  processStatus.value = ''
  processMessage.value = '正在上传文件...'

  try {
    const uploadResponse = await fileApi.uploadExcel(uploadedFile.value.raw)
    processProgress.value = 30
    processMessage.value = '正在处理文件...'

    const processResponse = await fileApi.processExcel(
      uploadResponse.fileId,
      options.format
    )
    
    processProgress.value = 100
    processStatus.value = 'success'
    processMessage.value = '处理完成'
    processedFileId.value = processResponse.fileId
    processResult.value = processResponse
    
    ElMessage.success('文件处理完成')
    loadTempFiles()
  } catch (error) {
    processProgress.value = 100
    processStatus.value = 'exception'
    processMessage.value = '处理失败'
    processResult.value = {
      status: 'error',
      error: error.message || '处理失败'
    }
    ElMessage.error(error.message || '处理失败')
  } finally {
    processing.value = false
  }
}

const downloadProcessedFile = async () => {
  if (!processedFileId.value) {
    ElMessage.warning('没有可下载的文件')
    return
  }

  try {
    const data = await fileApi.downloadProcessedFile(processedFileId.value)
    const blob = new Blob([data], {
      type: options.format === 'csv'
        ? 'text/csv'
        : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `打卡数据汇总统计.${options.format}`
    link.click()
    URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

const loadTempFiles = async () => {
  try {
    const response = await fileApi.getTempFiles()
    tempFiles.value = response.files || []
  } catch (error) {
    console.error('加载临时文件失败:', error)
  }
}

const downloadTempFile = async (filename) => {
  try {
    const data = await fileApi.downloadTempFile(filename)
    const blob = new Blob([data])
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.click()
    URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

const deleteTempFile = async (filename) => {
  try {
    await ElMessageBox.confirm('确定要删除这个文件吗？', '提示', {
      type: 'warning'
    })
    
    await fileApi.deleteTempFile(filename)
    ElMessage.success('删除成功')
    loadTempFiles()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

onMounted(() => {
  loadTempFiles()
})
</script>

<style scoped>
.excel-processor {
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

.upload-card,
.options-card,
.action-card,
.result-card,
.files-card {
  margin-bottom: 20px;
}

.upload-card h3,
.options-card h3,
.action-card h3,
.result-card h3,
.files-card h3 {
  font-size: 16px;
  font-weight: bold;
}

.upload-area {
  width: 100%;
}

.upload-icon {
  font-size: 48px;
  color: #409EFF;
  margin-bottom: 16px;
}

.upload-text {
  font-size: 14px;
  color: #606266;
}

.upload-text em {
  color: #409EFF;
  font-style: normal;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-top: 16px;
}

.action-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-bottom: 20px;
}
</style>