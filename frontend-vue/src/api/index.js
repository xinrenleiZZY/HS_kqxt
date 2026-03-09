import request from '@/utils/request'

export const authApi = {
  login(data) {
    return request.post('/auth/login', data)
  },
  logout() {
    return request.post('/auth/logout')
  },
  getCurrentUser() {
    return request.get('/auth/user')
  }
}

export const employeeApi = {
  getList(params) {
    return request.get('/employees', { params })
  },
  getById(id) {
    return request.get(`/employees/${id}`)
  },
  create(data) {
    return request.post('/employees', data)
  },
  update(id, data) {
    return request.put(`/employees/${id}`, data)
  },
  delete(id) {
    return request.delete(`/employees/${id}`)
  },
  search(keyword) {
    return request.get('/employees/search', { params: { keyword } })
  }
}

export const attendanceApi = {
  getRecords(params) {
    return request.get('/attendance/records', { params })
  },
  getTodayStats() {
    return request.get('/attendance/today-stats')
  },
  getRecentRecords(limit = 10) {
    return request.get('/attendance/recent', { params: { limit } })
  },
  exportData(params) {
    return request.get('/attendance/export', { params, responseType: 'blob' })
  }
}

export const reportApi = {
  getStats(params) {
    return request.get('/reports/stats', { params })
  },
  getWorkHours(params) {
    return request.get('/reports/work-hours', { params })
  },
  getDepartmentStats(params) {
    return request.get('/reports/department-stats', { params })
  }
}

export const rulesApi = {
  getRules() {
    return request.get('/rules')
  },
  updateRules(data) {
    return request.put('/rules', data)
  }
}

export const fileApi = {
  uploadExcel(file) {
    const formData = new FormData()
    formData.append('file', file)
    return request.post('/files/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  processExcel(fileId, format = 'xlsx') {
    return request.post('/files/process', { fileId, format })
  },
  downloadProcessedFile(fileId) {
    return request.get(`/files/download/${fileId}`, { responseType: 'blob' })
  },
  getTempFiles() {
    return request.get('/files/temp')
  },
  downloadTempFile(filename) {
    return request.get(`/files/temp/${filename}`, { responseType: 'blob' })
  }
}