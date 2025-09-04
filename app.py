import streamlit as st
from streamlit.components.v1 import html
import os
import json
from modules import auth, employees, rules, reports
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from io import BytesIO
import subprocess
import uuid

# 确保数据目录存在
os.makedirs('data', exist_ok=True)
# 确保临时目录存在
os.makedirs('temp_files', exist_ok=True)
TEMP_DIR = 'temp_files'
# 初始化FastAPI应用（如果使用Streamlit+FastAPI混合模式）
app = FastAPI()
@app.post("/process_excel")
async def process_excel(excel_file: UploadFile = File(...)):
    result = process_excel_file(excel_file)
    return JSONResponse(result)

@app.get("/download_excel")
async def download_excel(file_id: str):
    excel_data = get_processed_file(file_id)
    if not excel_data:
        return JSONResponse({"status": "error", "error": "文件不存在"})
    return FileResponse(
        excel_data,
        filename="打卡数据汇总统计.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# 初始化数据库表
def init_all_tables():
    """初始化所有数据库表结构"""
    auth.init_users_table()
    employees.init_employees_table()
    rules.init_attendance_rules()
    reports.init_attendance_records()

# 读取前端HTML文件
def load_frontend_html():
    """加载前端HTML模板文件"""
    try:
        with open(os.path.join("frontend", "index.html"), "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        st.error("前端模板文件未找到，请确保frontend/index.html存在")
        return "<h1>前端资源加载失败</h1>"

# 准备后端数据
def get_backend_data():
    """获取需要传递给前端的后端数据"""
    attendance_rules = rules.get_attendance_rules()
    # 调试：打印获取到的考勤规则
    print("考勤规则数据:", attendance_rules)
    return {
        "current_user": st.session_state.get("username", "管理员"),
        "user_role": st.session_state.get("role", "admin"),
        "stats": {
            "total_employees": employees.get_total_count(),
            "today_attendance": reports.get_today_attendance(),
            "late_count": reports.get_late_count(),
            "overtime_hours": reports.get_overtime_hours()
        },
        "attendance_rules": rules.get_attendance_rules(),
        "recent_records": reports.get_recent_records()
    }

# 存储处理后的文件（内存中，实际项目可使用数据库或文件系统）
processed_files = {}

def process_excel_file(file):
    """处理上传的Excel文件（替换为你的实际业务逻辑）"""
    try:
        # 1. 保存上传的文件为"原始文件.xlsx"
        original_path = os.path.join(TEMP_DIR, "原始文件.xlsx")
        with open(original_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # 2. 执行1分割.py
        subprocess.run(
            ["python", "modules/1分割.py"],
            check=True,
            capture_output=True,
            text=True
        )

        # 3. 执行2时间预处理.py
        subprocess.run(
            ["python", "modules/2时间预处理.py"],
            check=True,
            capture_output=True,
            text=True
        )

        # 4. 执行3分列时间.py
        subprocess.run(
            ["python", "modules/3分列时间.py"],
            check=True,
            capture_output=True,
            text=True
        )

        # 5. 执行4全班.py
        subprocess.run(
            ["python", "modules/4全班.py"],
            check=True,
            capture_output=True,
            text=True
        )

        # 6. 执行5汇总.py
        subprocess.run(
            ["python", "modules/5汇总.py"],
            check=True,
            capture_output=True,
            text=True
        )

        # 生成文件ID用于下载
        file_id = str(uuid.uuid4())
        # 存储最终文件路径
        final_file_path = os.path.join(TEMP_DIR, "打卡数据汇总统计.xlsx")
        processed_files[file_id] = final_file_path

        return {"status": "success", "file_id": file_id}

    except subprocess.CalledProcessError as e:
        return {"status": "error", "error": f"处理脚本出错: {e.stderr}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def get_processed_file(file_id):
    """获取处理后的最终文件"""
    if file_id not in processed_files:
        return None
    file_path = processed_files[file_id]
    if not os.path.exists(file_path):
        return None
    
    # 读取文件内容
    with open(file_path, "rb") as f:
        excel_data = BytesIO(f.read())
    return excel_data

# 主应用
def main():
    # 设置页面配置
    st.set_page_config(
        layout="wide",  # 宽屏布局
        initial_sidebar_state="collapsed",  # 折叠侧边栏
        menu_items={"Get help": None, "Report a bug": None, "About": None}
    )
    # 初始化数据库
    init_all_tables()
    
    # 检查登录状态
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        # 显示登录页面
        auth.login_page()
    else:
        # 获取后端数据
        backend_data = get_backend_data()
        # 将后端数据转换为JavaScript变量
        data_script = f"window.backendData = {json.dumps(backend_data)};"
        
        excel_action = st.query_params.get("excel_action")
        if excel_action == "process":
            # 处理上传的文件
            uploaded_file = st.file_uploader("上传Excel", type=["xlsx", "xls"], key="excel_upload")
            if uploaded_file:
                result = process_excel_file(uploaded_file)
                st.write(result)  # 返回结果给前端
        elif excel_action == "download":
            # 处理下载请求
            file_id = st.query_params.get("file_id", [None])[0]
            if file_id:
                excel_data = get_processed_file(file_id)
                if excel_data:
                    st.download_button(
                        label="下载处理后的文件",
                        data=excel_data,
                        file_name="processed_attendance.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

        # 加载并修改HTML内容
        html_content = load_frontend_html()
        # 将数据脚本插入到HTML头部
        html_content = html_content.replace("</head>", f"<script>{data_script}</script></head>")
        
        # 添加前后端交互脚本
        interaction_script = """
        <script>
            window.Streamlit = window.parent.Streamlit;
            // 处理文件上传响应
            window.parent.Streamlit.onMessage = (event) => {
                const data = event.data;
                if (data.type === "excel_process_result") {
                    if (data.status === "success") {
                        document.getElementById('process-message').textContent = "处理完成，可导出";
                        document.getElementById('download-excel-btn').disabled = false;
                        window.processedFileId = data.file_id;
                    } else {
                        document.getElementById('process-message').textContent = `错误: ${data.error}`;
                    }
                }
            };
            // 填充考勤规则表单
            const rules = window.backendData.attendance_rules;
            if (rules) {
                document.querySelector('input[value="09:00"]').value = rules.work_start_time;
                document.querySelector('input[value="18:00"]').value = rules.work_end_time;
                document.querySelector('input[value="15"][min="0"][max="60"]').value = rules.late_threshold;
                document.querySelector('input[value="12:00"]').value = rules.lunch_start_time;
            }
            // 填充统计数据
            if (window.backendData) {
                // 更新用户信息
                document.querySelector('.font-medium.text-sm').textContent = window.backendData.current_user;
                
                // 更新统计卡片
                const stats = window.backendData.stats;
                document.querySelector('.stats-total-employees').textContent = stats.total_employees;
                document.querySelector('.stats-today-attendance').textContent = stats.today_attendance;
                document.querySelector('.stats-late-count').textContent = stats.late_count;
                document.querySelector('.stats-overtime-hours').textContent = stats.overtime_hours + 'h';
                // 更新最近打卡记录
                updateRecentRecords(window.backendData.recent_records);
            }
            
            // 更新打卡记录表格
            function updateRecentRecords(records) {
                const tableBody = document.querySelector('#recent-records-table tbody');
                if (!tableBody) return;
                
                tableBody.innerHTML = '';
                records.forEach(record => {
                    const row = document.createElement('tr');
                    row.className = 'hover:bg-light-1/50 transition-colors';
                    row.innerHTML = `
                        <td class="px-6 py-4">
                            <div class="flex items-center gap-3">
                                <img src="${record.avatar}" alt="员工头像" class="w-8 h-8 rounded-full">
                                <span>${record.name}</span>
                            </div>
                        </td>
                        <td class="px-6 py-4">${record.department}</td>
                        <td class="px-6 py-4">${record.type}</td>
                        <td class="px-6 py-4">${record.time}</td>
                        <td class="px-6 py-4">
                            <span class="px-2 py-1 ${record.status_class} text-xs rounded-full">${record.status}</span>
                        </td>
                        <td class="px-6 py-4">
                            <button class="text-primary hover:text-primary/80">详情</button>
                        </td>
                    `;
                    tableBody.appendChild(row);
                });
            }
        </script>
        """
        
        # 将交互脚本插入到HTML底部
        html_content = html_content.replace("</body>", f"{interaction_script}</body>")
        
        # 自定义Streamlit样式，移除默认边距和限制
        st.markdown("""
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                .reportview-container .main .block-container,
                .reportview-container .main 
                #app-container ,
                main.flex-1,
                .horizontal-container {
                    max-width: 100% !important;
                    width: 100% !important;
                    margin: 0 !important;
                    padding: 0 !important;
                }
                .reportview-container {
                    padding: 0 !important;
                    margin: 0 !important;
                }
                html, body {
                    overflow: auto !important;
                    width: 100% !important;
                    height: 100% !important;
                    margin: 0 !important;
                    padding: 0 !important;
                }
                #app-container {
                    display: flex !important;
                    height: 100vh !important;
                    overflow: hidden !important;
                }
                #sidebar {
                    margin: 0 !important;
                    padding: 0 !important;
                    flex-shrink: 0 !important;
                }
                #app-container main.flex-1 {
                    margin-left: 0 !important;
                    padding-left: 0 !important;
                    overflow-y: auto !important;
                    flex: 1 1 auto !important;
                }
                iframe {
                    width: 100% !important;
                    height: 100vh !important;
                    overflow: hidden !important; 
                    border: none !important;
                }
                #MainMenu, .stDeployButton, footer {
                    display: none !important;
                }
                #page-content {
                    height: 100% !important;
                    overflow-y: auto !important;
                }
            </style>
        """, unsafe_allow_html=True)
        # 渲染完整页面
        html(html_content, height=0, scrolling=True)

if __name__ == "__main__":
    main()