from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import os
import uuid
import subprocess
import sys
from datetime import datetime
from io import BytesIO
import pandas as pd
from pathlib import Path

app = FastAPI(title="考勤管理系统API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "data/attendance.db"
TEMP_DIR = "temp_files"
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs("data", exist_ok=True)

processed_files = {}

class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    token: str
    user: dict

class EmployeeCreate(BaseModel):
    employee_id: str
    name: str
    department: str
    position: str
    hire_date: str
    status: str = "active"

class RulesUpdate(BaseModel):
    work_start_time: str
    work_end_time: str
    late_threshold: int
    early_leave_threshold: int
    lunch_start_time: str
    lunch_end_time: str
    overtime_start_time: str
    daily_standard_hours: float
    work_days: str

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        import hashlib
        admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                   ('admin', admin_password, 'admin'))
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            position TEXT NOT NULL,
            hire_date DATE NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            avatar TEXT DEFAULT 'https://picsum.photos/id/237/40/40'
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            work_start_time TIME NOT NULL DEFAULT '09:00',
            work_end_time TIME NOT NULL DEFAULT '18:00',
            late_threshold INTEGER NOT NULL DEFAULT 15,
            early_leave_threshold INTEGER NOT NULL DEFAULT 15,
            lunch_start_time TIME NOT NULL DEFAULT '12:00',
            lunch_end_time TIME NOT NULL DEFAULT '13:00',
            overtime_start_time TIME NOT NULL DEFAULT '19:00',
            daily_standard_hours REAL NOT NULL DEFAULT 8.0,
            work_days TEXT NOT NULL DEFAULT '1,2,3,4,5',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            check_in_time TIMESTAMP,
            check_out_time TIMESTAMP,
            work_hours REAL,
            overtime_hours REAL,
            status TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
        )
    ''')
    
    cursor.execute("SELECT id FROM attendance_rules LIMIT 1")
    if not cursor.fetchone():
        cursor.execute('INSERT INTO attendance_rules DEFAULT VALUES')
    
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.on_event("startup")
async def startup_event():
    init_db()

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    import hashlib
    hashed_pw = hashlib.sha256(request.password.encode()).hexdigest()
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users WHERE username = ? AND password = ?",
               (request.username, hashed_pw))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user[0],))
        conn.commit()
        conn.close()
        
        import jwt
        token = jwt.encode({"user_id": user[0], "username": user[1]}, "secret", algorithm="HS256")
        return UserResponse(token=token, user={"id": user[0], "username": user[1], "role": user[2]})
    
    raise HTTPException(status_code=401, detail="用户名或密码错误")

@app.get("/api/auth/user")
async def get_current_user():
    return {"username": "admin", "role": "admin"}

@app.get("/api/employees")
async def get_employees(page: int = 1, pageSize: int = 10, keyword: str = ""):
    conn = get_db()
    cursor = conn.cursor()
    
    offset = (page - 1) * pageSize
    query = "SELECT * FROM employees"
    params = []
    
    if keyword:
        query += " WHERE employee_id LIKE ? OR name LIKE ? OR department LIKE ?"
        params = [f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"]
    
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([pageSize, offset])
    
    cursor.execute(query, params)
    employees = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT COUNT(*) FROM employees")
    total = cursor.fetchone()[0]
    
    conn.close()
    return {"employees": employees, "total": total}

@app.post("/api/employees")
async def create_employee(employee: EmployeeCreate):
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO employees (employee_id, name, department, position, hire_date, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (employee.employee_id, employee.name, employee.department,
              employee.position, employee.hire_date, employee.status))
        conn.commit()
        conn.close()
        return {"message": "员工添加成功"}
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="员工编号已存在")

@app.get("/api/rules")
async def get_rules():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attendance_rules ORDER BY updated_at DESC LIMIT 1")
    rule = cursor.fetchone()
    conn.close()
    return dict(rule) if rule else {}

@app.put("/api/rules")
async def update_rules(rules: RulesUpdate):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE attendance_rules 
        SET work_start_time = ?, work_end_time = ?, late_threshold = ?,
            early_leave_threshold = ?, lunch_start_time = ?, lunch_end_time = ?,
            overtime_start_time = ?, daily_standard_hours = ?, work_days = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = (SELECT id FROM attendance_rules ORDER BY updated_at DESC LIMIT 1)
    ''', (rules.work_start_time, rules.work_end_time, rules.late_threshold,
          rules.early_leave_threshold, rules.lunch_start_time, rules.lunch_end_time,
          rules.overtime_start_time, rules.daily_standard_hours, rules.work_days))
    
    conn.commit()
    conn.close()
    return {"message": "规则更新成功"}

@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(TEMP_DIR, f"{file_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    return {"fileId": file_id, "filename": file.filename}

@app.post("/api/files/process")
async def process_excel_file(fileId: str = Form(...), format: str = Form("xlsx")):
    if fileId not in processed_files:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    file_path = processed_files[fileId]
    
    try:
        scripts = [
            "modules/1分割.py",
            "modules/2时间预处理.py",
            "modules/3分列时间.py",
            "modules/4全班.py",
            "modules/66.py",
            "modules/6.py"
        ]
        
        for script in scripts:
            result = subprocess.run(
                [sys.executable, script],
                capture_output=True,
                text=True,
                check=True
            )
        
        final_file = os.path.join(TEMP_DIR, "打卡数据汇总统计.xlsx")
        new_file_id = str(uuid.uuid4())
        processed_files[new_file_id] = final_file
        
        return {"status": "success", "fileId": new_file_id, "format": format}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {e.stderr}")

@app.get("/api/files/download/{file_id}")
async def download_file(file_id: str):
    if file_id not in processed_files:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    file_path = processed_files[file_id]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件已过期")
    
    return FileResponse(file_path)

@app.get("/api/files/temp")
async def get_temp_files():
    files = []
    for filename in os.listdir(TEMP_DIR):
        file_path = os.path.join(TEMP_DIR, filename)
        if os.path.isfile(file_path):
            stat = os.stat(file_path)
            files.append({
                "name": filename,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            })
    return {"files": files}

@app.get("/api/files/temp/{filename}")
async def download_temp_file(filename: str):
    file_path = os.path.join(TEMP_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(file_path)

@app.delete("/api/files/temp/{filename}")
async def delete_temp_file(filename: str):
    file_path = os.path.join(TEMP_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    os.remove(file_path)
    return {"message": "删除成功"}

@app.get("/api/attendance/today-stats")
async def get_today_stats():
    return {
        "totalEmployees": 100,
        "todayAttendance": 85,
        "lateCount": 5,
        "overtimeHours": 12.5
    }

@app.get("/api/attendance/recent")
async def get_recent_records(limit: int = 10):
    records = [
        {
            "avatar": "https://picsum.photos/100/100",
            "name": "张三",
            "department": "技术部",
            "type": "上班打卡",
            "time": "09:02:15",
            "status": "正常"
        }
    ]
    return {"records": records, "total": 42}

@app.get("/api/attendance/records")
async def get_attendance_records(page: int = 1, pageSize: int = 10):
    records = [
        {
            "avatar": "https://picsum.photos/100/100",
            "name": "张三",
            "department": "技术部",
            "checkInTime": "09:02:15",
            "checkOutTime": "18:15:30",
            "workHours": "9.2小时",
            "status": "正常"
        }
    ]
    return {"records": records, "total": 124}

@app.get("/api/reports/stats")
async def get_report_stats():
    return {
        "reports": [],
        "total": 0,
        "stats": {
            "totalDays": 0,
            "totalHours": 0,
            "avgHours": 0,
            "totalOvertime": 0,
            "lateCount": 0,
            "earlyLeaveCount": 0
        }
    }

@app.get("/api/reports/work-hours")
async def get_work_hours():
    return {
        "labels": ["周一", "周二", "周三", "周四", "周五"],
        "workHours": [8, 7.5, 8.5, 9, 7],
        "overtime": [1, 0.5, 2, 1.5, 0]
    }

@app.get("/api/reports/department-stats")
async def get_department_stats():
    return {
        "data": [
            {"value": 30, "name": "技术部"},
            {"value": 20, "name": "市场部"},
            {"value": 10, "name": "人事部"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)