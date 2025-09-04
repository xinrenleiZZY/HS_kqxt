import pandas as pd
import openpyxl

# 输入文件路径（处理后的打卡数据）
input_file = '../temp_files/全班次处理后的打卡数据.xlsx'
# 输出文件路径（汇总结果）
output_file = '../temp_files/打卡数据汇总统计.xlsx'

# 读取工作簿中的所有工作表
xls = pd.ExcelFile(input_file)
sheet_names = xls.sheet_names

# 筛选需要处理的工作表（排除'原始数据'）
process_sheets = [name for name in sheet_names if name != '原始数据']

if not process_sheets:
    print("没有需要处理的工作表（除原始数据外）")
else:
    # 合并所有需要处理的工作表数据
    all_data = []
    for sheet in process_sheets:
        df = pd.read_excel(xls, sheet_name=sheet)
        all_data.append(df)

    combined_df = pd.concat(all_data, ignore_index=True)

    # 确保必要的列存在
    required_cols = [
        '姓名', '员工ID', '部门', '班次',
        '打卡状态', '白天加班时长(小时)',
        '晚上加班时长(小时)', '迟到时间'
    ]
    missing_cols = [col for col in required_cols if col not in combined_df.columns]
    if missing_cols:
        print(f"错误：数据缺少必要列 {missing_cols}，无法进行汇总")
    else:
        # 处理迟到时间转换（将字符串转换为分钟数）
        def parse_late_time(time_str):
            """将迟到时间字符串（如"1小时30分钟"）转换为总分钟数"""
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
            return hours * 60 + minutes


        # 处理加班时长（确保为数值类型）
        combined_df['白天加班时长(小时)'] = pd.to_numeric(
            combined_df['白天加班时长(小时)'], errors='coerce').fillna(0)
        combined_df['晚上加班时长(小时)'] = pd.to_numeric(
            combined_df['晚上加班时长(小时)'], errors='coerce').fillna(0)

        # 计算迟到分钟数
        combined_df['迟到分钟数'] = combined_df['迟到时间'].apply(parse_late_time)


        # 按员工分组汇总
        def aggregate_func(group):
            # 上班天数：打卡状态为"正常"的数量
            work_days = group[group['打卡状态'] == '正常'].shape[0]

            # 出勤时间：上班天数 * 8小时
            attendance_hours = work_days * 8

            # 白天加班总和
            day_ot = group['白天加班时长(小时)'].sum()

            # 晚上加班总和
            night_ot = group['晚上加班时长(小时)'].sum()

            # 出勤总工时
            total_hours = attendance_hours + day_ot + night_ot

            # 迟到总时间（分钟转换为"X小时Y分钟"格式）
            total_late_minutes = group['迟到分钟数'].sum()
            late_hours = total_late_minutes // 60
            late_mins = total_late_minutes % 60
            if late_hours == 0 and late_mins == 0:
                late_str = "0分钟"
            else:
                parts = []
                if late_hours > 0:
                    parts.append(f"{late_hours}小时")
                if late_mins > 0:
                    parts.append(f"{late_mins}分钟")
                late_str = "".join(parts)

            # 取员工的基本信息（取第一个值）
            dept = group['部门'].iloc[0] if not group['部门'].empty else ""
            shift = group['班次'].iloc[0] if not group['班次'].empty else ""

            return pd.Series({
                '部门': dept,
                '班次': shift,
                '上班天数': work_days,
                '出勤时间': attendance_hours,
                '白天加班': round(day_ot, 1),
                '晚上加班': round(night_ot, 1),
                '出勤总工时': round(total_hours, 1),
                '迟到总时间': late_str
            })


        # 按姓名和员工ID分组汇总
        summary_df = combined_df.groupby(['姓名', '员工ID']).apply(
            lambda x: aggregate_func(x)
        ).reset_index()
        # 调整列顺序
        summary_df = summary_df[['姓名', '员工ID', '部门', '班次',
                                 '上班天数', '出勤时间', '白天加班',
                                 '晚上加班', '出勤总工时', '迟到总时间']]

        # 保存结果
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            summary_df.to_excel(writer, sheet_name='汇总统计', index=False)

        print(f"汇总完成！共处理 {len(process_sheets)} 个工作表，结果已保存到 {output_file}")