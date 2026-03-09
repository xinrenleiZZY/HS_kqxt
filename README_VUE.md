# 考勤管理系统 - Vue 3 + Vite 版本

## 项目架构

本项目采用前后端分离架构：

- **前端**: Vue 3 + Vite + Element Plus + ECharts
- **后端**: FastAPI (Python)
- **数据库**: SQLite
- **部署方案**: Render (API服务器) + GitHub Pages (前端)

## 项目结构

```
attendance-system-admin/
├── frontend-vue/           # Vue 3 前端项目
│   ├── src/
│   │   ├── api/           # API 接口封装
│   │   ├── assets/        # 静态资源
│   │   ├── components/     # 公共组件
│   │   ├── layouts/        # 布局组件
│   │   ├── router/         # 路由配置
│   │   ├── stores/         # Pinia 状态管理
│   │   ├── utils/          # 工具函数
│   │   ├── views/          # 页面组件
│   │   ├── App.vue
│   │   └── main.js
│   ├── .env.development   # 开发环境配置
│   ├── .env.production    # 生产环境配置
│   ├── vite.config.js      # Vite 配置
│   └── package.json
├── modules/               # Excel 处理脚本
├── data/                  # 数据库文件
├── temp_files/            # 临时文件目录
├── api_server.py          # FastAPI 后端服务器
├── api_requirements.txt    # 后端依赖
├── render.yaml            # Render 部署配置
└── .github/workflows/      # GitHub Actions 工作流
```

## 功能模块

### 前端功能

1. **登录页面** - 用户认证
2. **仪表盘** - 数据统计和图表展示
3. **打卡记录** - 查看和管理打卡数据
4. **Excel处理终端** - 上传和处理考勤数据文件
5. **员工管理** - 员工信息管理
6. **工时报表** - 工时统计和报表
7. **考勤规则** - 设置考勤规则
8. **系统设置** - 系统配置

### 后端功能

1. **用户认证** - 登录、登出、用户信息
2. **员工管理** - CRUD 操作
3. **考勤规则** - 规则设置和获取
4. **文件处理** - Excel 文件上传和处理
5. **数据统计** - 考勤数据统计

## 技术栈

### 前端

- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 下一代前端构建工具
- **Vue Router** - Vue.js 官方路由
- **Pinia** - Vue 状态管理库
- **Element Plus** - Vue 3 UI 组件库
- **ECharts** - 数据可视化图表库
- **Axios** - HTTP 客户端

### 后端

- **FastAPI** - 现代、快速（高性能）的 Web 框架
- **Uvicorn** - ASGI 服务器
- **SQLite** - 轻量级数据库
- **Pandas** - 数据处理
- **OpenPyXL** - Excel 文件处理

## 本地开发

### 前端开发

```bash
cd frontend-vue
npm install
npm run dev
```

前端将在 `http://localhost:5173` 运行

### 后端开发

```bash
pip install -r api_requirements.txt
python api_server.py
```

后端 API 将在 `http://localhost:8000` 运行

## 部署

### 后端部署到 Render

1. 将代码推送到 GitHub
2. 在 Render 创建新的 Web Service
3. 连接 GitHub 仓库
4. 配置构建和启动命令
5. 部署完成后获得 API URL

### 前端部署到 GitHub Pages

1. 在 GitHub 仓库设置中启用 GitHub Pages
2. 配置 GitHub Actions 工作流
3. 推送代码到 main 分支
4. 自动构建并部署到 GitHub Pages

### 环境变量配置

在部署时需要配置以下环境变量：

**Render (后端):**
- `PORT`: 8000 (或自定义端口)

**GitHub Pages (前端):**
- `API_URL`: 你的 Render API 地址
- `GITHUB_TOKEN`: GitHub 访问令牌

## API 接口文档

启动后端服务器后，访问 `http://localhost:8000/docs` 查看完整的 API 文档。

### 主要接口

- `POST /api/auth/login` - 用户登录
- `GET /api/employees` - 获取员工列表
- `POST /api/employees` - 创建员工
- `GET /api/rules` - 获取考勤规则
- `PUT /api/rules` - 更新考勤规则
- `POST /api/files/upload` - 上传 Excel 文件
- `POST /api/files/process` - 处理 Excel 文件
- `GET /api/files/download/{file_id}` - 下载处理后的文件

## Excel 处理流程

1. **数据拆分** - 按日期拆分为多个工作表
2. **时间预处理** - 处理和优化打卡时间
3. **时间分列** - 拆分打卡时间到多个列
4. **班次处理** - 根据班次计算考勤信息
5. **夜班补贴** - 计算夜班补贴时长
6. **数据汇总** - 生成每日统计和总汇总

## 开发注意事项

1. **跨域问题**: 前端开发时使用 Vite 代理解决跨域
2. **API 地址**: 生产环境需要配置正确的 API 地址
3. **文件路径**: Excel 处理脚本使用相对路径，确保在正确目录运行
4. **数据库**: SQLite 数据库文件需要正确的读写权限

## 许可证

MIT License