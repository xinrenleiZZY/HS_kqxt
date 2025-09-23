import pandas as pd
import openpyxl
from datetime import datetime
import os

# 输入文件路径（使用带补贴时长的处理后数据）
current_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(current_dir, '../temp_files/员工打卡记录_带补贴时长.xlsx')
output_file = os.path.join(current_dir, '../temp_files/打卡数据汇总统计.xlsx')

# 读取工作簿中的所有工作表
xls = pd.ExcelFile(input_file)
sheet_names = xls.sheet_names

# 筛选需要处理的工作表（排除'原始数据'）
process_sheets = [name for name in sheet_names if name != '原始数据']

if not process_sheets:
    print("没有需要处理的工作表（除原始数据外）")
else:
    # 存储所有工作表的每日统计结果（用于最终汇总）
    daily_summaries = []
    
    # 处理迟到时间转换函数
    def parse_late_time(time_str):
        if pd.isna(time_str) or str(time_str).strip() in ["", "0分钟"]:
            return 0
        time_str = str(time_str).strip()
        hours = 0
        minutes = 0
        if '小时' in time_str:
            h_part = time_str.split('小时')[0]
            hours = int(h_part) if h_part.isdigit() else 0
            remaining = time_str.split('小时')[1]
            if '分钟' in remaining:
                m_part = remaining.split('分钟')[0]
                minutes = int(m_part) if m_part.isdigit() else 0
        elif '分钟' in time_str:
            m_part = time_str.split('分钟')[0]
            minutes = int(m_part) if m_part.isdigit() else 0
        return hours * 60 + minutes  # 返回总分钟数

    # 处理早退时间转换函数（将"X小时"转换为小时数）
    def parse_early_leave(time_str):
        if pd.isna(time_str) or str(time_str).strip() in ["", "0小时"]:
            return 0.0
        time_str = str(time_str).strip()
        if '小时' in time_str:
            h_part = time_str.split('小时')[0]
            return float(h_part) if h_part.isdigit() else 0.0
        return 0.0

    # 转换分钟数为时间字符串
    def format_late_time(total_minutes):
        if total_minutes == 0:
            return "0分钟"
        hours = total_minutes // 60
        minutes = total_minutes % 60
        parts = []
        if hours > 0:
            parts.append(f"{hours}小时")
        if minutes > 0:
            parts.append(f"{minutes}分钟")
        return "".join(parts)

    # 分组统计函数（包含早退时间处理）
    def aggregate_func(group, sheet_name):
        work_days = group[group['打卡状态'] == '正常'].shape[0]
        attendance_hours = work_days * 8
        day_ot = group['白天加班时长(小时)'].sum()
        night_ot = group['晚上加班时长(小时)'].sum()
        subsidy_ot = group['夜班补贴时长(小时)'].sum()
        
        # 计算早退总小时数（新增）
        if '早退时间' in group.columns:
            group['早退小时数'] = group['早退时间'].apply(parse_early_leave)
            zt_ot = group['早退小时数'].sum()
            total_early_leave = zt_ot  # 保留原始早退小时数用于显示
        else:
            zt_ot = 0
            total_early_leave = 0
        
        # 总工时计算（扣除早退时间）
        total_hours = attendance_hours + day_ot + night_ot + subsidy_ot - zt_ot

        # 迟到时间处理
        total_late_minutes = group['迟到分钟数'].sum()
        late_str = format_late_time(total_late_minutes)

        # 基础信息
        dept = group['部门'].iloc[0] if not group['部门'].empty else ""
        shift = group['班次'].iloc[0] if not group['班次'].empty else ""
        
        return pd.Series({
            '日期': sheet_name,
            '部门': dept,
            '班次': shift,
            '上班天数': work_days,
            '出勤时间': attendance_hours,
            '白天加班': round(day_ot, 1),
            '晚上加班': round(night_ot, 1),
            '早退时间(小时)': round(total_early_leave, 1),  # 新增：显示每日早退小时数
            '出勤总工时': round(total_hours, 1),
            '夜班补贴': round(subsidy_ot, 1),
            '迟到总时间': late_str
        })

    # 创建ExcelWriter用于写入每日统计和总汇总
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # 1. 处理每个工作表（每天）并生成每日统计
        for sheet in process_sheets:
            df = pd.read_excel(xls, sheet_name=sheet)
            
            # 检查必要列（新增早退时间列检查）
            required_cols = [
                '姓名', '员工ID', '部门', '班次', '打卡状态',
                '白天加班时长(小时)', '晚上加班时长(小时)', '迟到时间', '夜班补贴时长(小时)'
            ]
            # 早退时间列非必需，仅做提示
            if '早退时间' not in df.columns:
                print(f"警告：工作表 {sheet} 缺少'早退时间'列，将按0处理")
            
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                print(f"警告：工作表 {sheet} 缺少列 {missing_cols}，已跳过")
                continue
            
            # 数据预处理
            df['白天加班时长(小时)'] = pd.to_numeric(df['白天加班时长(小时)'], errors='coerce').fillna(0)
            df['晚上加班时长(小时)'] = pd.to_numeric(df['晚上加班时长(小时)'], errors='coerce').fillna(0)
            df['夜班补贴时长(小时)'] = pd.to_numeric(df['夜班补贴时长(小时)'], errors='coerce').fillna(0)
            df['迟到分钟数'] = df['迟到时间'].apply(parse_late_time)
            
            # 按员工分组计算每日统计
            daily_summary = df.groupby(['姓名', '员工ID']).apply(
                lambda x: aggregate_func(x, sheet)
            ).reset_index()
            
            # 调整列顺序（新增早退时间列）
            daily_summary = daily_summary[['日期', '姓名', '员工ID', '部门', '班次',
                                           '上班天数', '出勤时间', '白天加班',
                                           '晚上加班', '早退时间(小时)',  # 新增列
                                           '出勤总工时', '夜班补贴', '迟到总时间']]
            
            # 写入当前工作表的统计结果
            daily_summary.to_excel(writer, sheet_name=f'{sheet}_统计', index=False)
            daily_summaries.append(daily_summary)
            print(f"已生成 {sheet} 的每日统计")

        # 2. 生成总汇总表（所有日期合并，包含早退汇总）
        if daily_summaries:
            all_daily = pd.concat(daily_summaries, ignore_index=True)
            
            # 先将每日迟到时间转换为分钟数，再求和
            all_daily['迟到总分钟数'] = all_daily['迟到总时间'].apply(parse_late_time)
            
            # 按员工分组计算总汇总
            total_summary = all_daily.groupby(['姓名', '员工ID']).apply(lambda group: pd.Series({
                '部门': group['部门'].iloc[0] if not group['部门'].empty else "",
                '班次': group['班次'].iloc[0] if not group['班次'].empty else "",
                '总上班天数': group['上班天数'].sum(),
                '总出勤时间': group['出勤时间'].sum(),
                '总白天加班': round(group['白天加班'].sum(), 1),
                '总晚上加班': round(group['晚上加班'].sum(), 1),
                '总早退时间(小时)': round(group['早退时间(小时)'].sum(), 1),  # 新增：总早退时间
                '总出勤总工时': round(group['出勤总工时'].sum(), 1),
                '总夜班补贴': round(group['夜班补贴'].sum(), 1),
                '总迟到时间': format_late_time(group['迟到总分钟数'].sum())
            })).reset_index()
            
            # 调整总汇总列顺序（新增总早退时间列）
            total_summary = total_summary[['姓名', '员工ID', '部门', '班次',
                                           '总上班天数', '总出勤时间', '总白天加班',
                                           '总晚上加班', '总早退时间(小时)',  # 新增列
                                           '总出勤总工时', '总夜班补贴', '总迟到时间']]
            
            # 写入总汇总表
            total_summary.to_excel(writer, sheet_name='总汇总统计', index=False)
            print("已生成总汇总统计")

    print(f"所有统计完成！结果已保存到 {output_file}")