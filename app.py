import streamlit as st
from streamlit.components.v1 import html
import os
import json
import subprocess
import uuid
from datetime import datetime, timedelta
from modules import auth, employees, rules, reports
from io import BytesIO

# 确保数据目录和临时目录存在
os.makedirs('data', exist_ok=True)
os.makedirs('temp_files', exist_ok=True)
TEMP_DIR = 'temp_files'
processed_files = {}  # 存储处理后的文件ID与路径映射


def init_all_tables():
    """初始化所有数据库表结构"""
    auth.init_users_table()
    employees.init_employees_table()
    rules.init_attendance_rules()
    reports.init_attendance_records()


def load_frontend_html():
    """加载前端HTML模板文件"""
    try:
        with open(os.path.join("frontend", "index.html"), "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        st.error("前端模板文件未找到，请确保frontend/index.html存在")
        return "<h1>前端资源加载失败</h1>"


def get_backend_data():
    """获取需要传递给前端的后端数据"""
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
        "recent_records": reports.get_recent_records(),
        "excel_status": {
            "has_uploaded": st.session_state.get("uploaded_file") is not None,
            "processing": st.session_state.get("processing", False),
            "processed": st.session_state.get("processed_file_id") is not None,
            "uploaded_filename": st.session_state["uploaded_file"].name if st.session_state.get("uploaded_file") else None,
            "process_result": st.session_state.get("process_result")
        }
    }


def clean_temp_files(max_age=3600):
    """清理过期临时文件（默认1小时）"""
    now = time.time()
    for filename in os.listdir(TEMP_DIR):
        file_path = os.path.join(TEMP_DIR, filename)
        if os.path.isfile(file_path) and now - os.path.getmtime(file_path) > max_age:
            os.remove(file_path)


def process_excel_file():
    """处理已上传的Excel文件"""
    if not st.session_state.get("uploaded_file"):
        return {"status": "error", "error": "未找到上传的文件"}

    try:
        st.session_state["processing"] = True
        
        # 保存上传的文件
        original_path = os.path.join(TEMP_DIR, "原始文件.xlsx")
        with open(original_path, "wb") as f:
            f.write(st.session_state["uploaded_file"].getbuffer())

        # 执行处理脚本
        scripts = [
            "1分割.py", "2时间预处理.py", 
            "3分列时间.py", "4全班.py", "5汇总.py"
        ]
        
        for script in scripts:
            result = subprocess.run(
                ["python", os.path.join("modules", script)],
                check=True,
                capture_output=True,
                text=True
            )
            # 输出脚本执行日志（调试用）
            print(f"脚本 {script} 执行结果: {result.stdout}")

        # 生成文件ID并存储路径
        file_id = str(uuid.uuid4())
        final_file_path = os.path.join(TEMP_DIR, "打卡数据汇总统计.xlsx")
        processed_files[file_id] = final_file_path

        # 更新状态
        st.session_state["processing"] = False
        st.session_state["processed_file_id"] = file_id
        clean_temp_files()  # 清理过期文件
        return {"status": "success", "file_id": file_id}

    except subprocess.CalledProcessError as e:
        st.session_state["processing"] = False
        return {"status": "error", "error": f"脚本执行错误: {e.stderr}"}
    except Exception as e:
        st.session_state["processing"] = False
        return {"status": "error", "error": str(e)}


def get_processed_file(file_id):
    """获取处理后的文件数据"""
    if file_id not in processed_files:
        return None
    file_path = processed_files[file_id]
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, "rb") as f:
        return BytesIO(f.read())


def main():
    st.set_page_config(
        layout="wide",
        initial_sidebar_state="collapsed",
        menu_items={"Get help": None, "Report a bug": None, "About": None}
    )
    
    # 初始化数据库
    init_all_tables()
    
    # 初始化session_state
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "uploaded_file" not in st.session_state:
        st.session_state["uploaded_file"] = None
    if "processing" not in st.session_state:
        st.session_state["processing"] = False
    if "processed_file_id" not in st.session_state:
        st.session_state["processed_file_id"] = None
    if "process_result" not in st.session_state:
        st.session_state["process_result"] = None

    # 登录状态检查
    if not st.session_state["logged_in"]:
        auth.login_page()
        return

    # 处理文件上传
    def handle_file_upload():
        uploaded_file = st.session_state["file_uploader"]
        if uploaded_file:
            st.session_state["uploaded_file"] = uploaded_file
            st.session_state["processed_file_id"] = None  # 重置处理结果
            st.session_state["process_result"] = None
            st.success(f"文件上传成功: {uploaded_file.name}")

    # 处理文件按钮回调
    def handle_process():
        result = process_excel_file()
        st.session_state["process_result"] = result
        if result["status"] == "success":
            st.success("文件处理完成！")
        else:
            st.error(f"处理失败: {result['error']}")

    # 侧边栏控制区
    with st.sidebar:
        st.subheader("Excel打卡记录处理")
        
        # 文件上传组件
        st.file_uploader(
            "选择Excel文件",
            type=["xlsx", "xls"],
            key="file_uploader",
            on_change=handle_file_upload
        )
        
        # 处理按钮（仅在有文件且未处理时可用）
        st.button(
            "处理Excel文件",
            on_click=handle_process,
            disabled=not st.session_state["uploaded_file"] or st.session_state["processing"]
        )
        
        # 显示处理状态
        if st.session_state["processing"]:
            st.info("正在处理文件...")
        
        # 下载按钮（仅在处理成功后显示）
        if st.session_state["processed_file_id"]:
            excel_data = get_processed_file(st.session_state["processed_file_id"])
            if excel_data:
                st.download_button(
                    label="下载处理结果",
                    data=excel_data,
                    file_name="打卡数据汇总统计.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_btn"
                )

    # 准备前端数据
    backend_data = get_backend_data()
    data_script = f"window.backendData = {json.dumps(backend_data)};"
    
    # 加载并修改HTML内容
    html_content = load_frontend_html()
    html_content = html_content.replace("</head>", f"<script>{data_script}</script></head>")
    
    # 前后端交互脚本
    interaction_script = """
    <script>
        // 绑定文件上传区域点击事件到Streamlit上传组件
        document.getElementById('file-upload-area')?.addEventListener('click', () => {
            // 触发Streamlit的文件上传组件点击
            const streamlitUploader = window.parent.document.querySelector('input[type="file"][data-testid="stFileUploader"]');
            if (streamlitUploader) {
                streamlitUploader.click();
            }
        });

        // 绑定处理按钮点击事件到Streamlit处理按钮
        document.getElementById('process-excel-btn')?.addEventListener('click', () => {
            // 触发Streamlit的处理按钮点击
            const streamlitProcessBtn = window.parent.document.querySelector('button:has(div p:contains("处理Excel文件"))');
            if (streamlitProcessBtn) {
                streamlitProcessBtn.click();
            }
        });

        // 绑定下载按钮点击事件到Streamlit下载按钮（已存在，可保留）
        document.getElementById('download-excel-btn')?.addEventListener('click', () => {
            if (window.backendData?.excel_status?.processed) {
                const streamlitDownloadBtn = window.parent.document.querySelector('button[aria-label="下载处理结果"]');
                if (streamlitDownloadBtn) streamlitDownloadBtn.click();
            }
        });

        // 监听Streamlit文件上传状态变化，同步到前端
        const observer = new MutationObserver((mutations) => {
            mutations.forEach(mutation => {
                if (mutation.type === 'childList') {
                    // 强制同步状态，更新前端显示
                    syncState();
                }
            });
        });

        // 监视Streamlit文件上传区域变化
        const streamlitFileUploadContainer = window.parent.document.querySelector('.stFileUploader');
        if (streamlitFileUploadContainer) {
            observer.observe(streamlitFileUploadContainer, {
                childList: true,
                subtree: true
            });
        }
        // 更新Excel处理区域状态
        function updateExcelStatus() {
            const backendData = window.backendData || {};
            const excelStatus = backendData.excel_status || {};
            const uploadedFilename = document.getElementById('uploaded-filename');
            
            // 更新上传文件名显示
            if (excelStatus.uploaded_filename) {
                uploadedFilename.textContent = `已上传: ${excelStatus.uploaded_filename}`;
                uploadedFilename.classList.remove('hidden');
            } else {
                uploadedFilename.classList.add('hidden');
            }
            
            // 处理错误信息显示
            if (excelStatus.process_result?.status === 'error') {
                processMessage.textContent = `处理失败: ${excelStatus.process_result.error}`;
                processStatus.classList.remove('hidden');
            }
        }

        // 同步Streamlit状态到前端
        function syncState() {
            const backendData = window.backendData || {};
            const excelStatus = backendData.excel_status || {};
            
            // 获取所有相关元素
            const processBtn = document.getElementById('process-excel-btn');
            const downloadBtn = document.getElementById('download-excel-btn');
            const processStatus = document.getElementById('process-status');
            const processMessage = document.getElementById('process-message');
            const uploadedFilename = document.getElementById('uploaded-filename');

            // 更新按钮状态
            if (processBtn) {
                processBtn.disabled = !excelStatus.has_uploaded || excelStatus.processing;
            }
            if (downloadBtn) {
                downloadBtn.disabled = !excelStatus.processed;
            }

            // 更新处理状态显示
            if (excelStatus.processing) {
                if (processStatus) processStatus.classList.remove('hidden');
                if (processMessage) processMessage.textContent = "正在处理文件...";
            } else if (excelStatus.processed) {
                if (processStatus) processStatus.classList.remove('hidden');
                if (processMessage) processMessage.textContent = "处理完成，可点击导出";
            } else if (excelStatus.has_uploaded) {
                if (processStatus) processStatus.classList.remove('hidden');
                if (processMessage) processMessage.textContent = "文件已上传，请点击处理";
            } else {
                if (processStatus) processStatus.classList.add('hidden');
            }

            // 更新上传文件名（从后端同步）
            if (backendData.excel_status?.uploaded_filename && uploadedFilename) {
                uploadedFilename.textContent = `已上传: ${backendData.excel_status.uploaded_filename}`;
                uploadedFilename.classList.remove('hidden');
            }
        }
        
        // 初始化时同步状态
        syncState();
        // 定时同步状态（每500ms）
        setInterval(syncState, 500);
        
        // 填充统计数据和考勤规则
        if (window.backendData) {
            // 更新用户信息
            document.querySelector('#user-display-name').textContent = window.backendData.current_user;
            
            // 更新统计卡片
            const stats = window.backendData.stats;
            if (stats) {
                document.querySelector('.stats-total-employees').textContent = stats.total_employees;
                document.querySelector('.stats-today-attendance').textContent = stats.today_attendance;
                document.querySelector('.stats-late-count').textContent = stats.late_count;
                document.querySelector('.stats-overtime-hours').textContent = stats.overtime_hours + 'h';
            }
            
            // 更新最近打卡记录
            updateRecentRecords(window.backendData.recent_records);
            
            // 填充考勤规则
            const rules = window.backendData.attendance_rules;
            if (rules) {
                document.getElementById('work-start-time').value = rules.work_start_time || '09:00';
                document.getElementById('work-end-time').value = rules.work_end_time || '18:00';
                document.getElementById('late-threshold').value = rules.late_threshold || 15;
                document.getElementById('lunch-start-time').value = rules.lunch_start_time || '12:00';
            }
        }
        
        // 更新打卡记录表格
        function updateRecentRecords(records) {
            const tableBody = document.querySelector('#recent-records-table tbody');
            if (!tableBody || !records) return;
            
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
        
        // 绑定下载按钮事件
        document.getElementById('download-excel-btn')?.addEventListener('click', () => {
            if (window.backendData?.excel_status?.processed) {
                // 触发Streamlit下载按钮点击
                const streamlitDownloadBtn = window.parent.document.querySelector('button[aria-label="下载处理结果"]');
                if (streamlitDownloadBtn) streamlitDownloadBtn.click();
            }
        });
    </script>
    """
    
    # 插入交互脚本
    html_content = html_content.replace("</body>", f"{interaction_script}</body>")
    
    # 自定义样式移除Streamlit默认样式
    st.markdown("""
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            .reportview-container, .main .block-container {
                max-width: 100% !important;
                width: 100% !important;
                margin: 0 !important;
                padding: 0 !important;
            }
            #MainMenu, .stDeployButton, footer { display: none !important; }
            iframe {
                width: 100% !important;
                height: 100vh !important;
                border: none !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # 渲染前端页面
    html(html_content, height=0, scrolling=True)


if __name__ == "__main__":
    main()