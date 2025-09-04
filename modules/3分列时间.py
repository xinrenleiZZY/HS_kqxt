import pandas as pd
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(current_dir, '../temp_files/按日期分表的处理打卡数据.xlsx')
output_file = os.path.join(current_dir, '../temp_files/按打卡时间分列的打卡数据.xlsx')

# 加载工作簿
wb = openpyxl.load_workbook(input_file)
# 创建新工作簿用于保存处理后的数据
new_wb = openpyxl.Workbook()
# 移除默认创建的工作表
default_sheet = new_wb.active
new_wb.remove(default_sheet)

# 复制"原始数据"工作表到新工作簿
if '原始数据' in wb.sheetnames:
    original_sheet = wb['原始数据']
    new_ws = new_wb.create_sheet(title='原始数据')
    for row in original_sheet.iter_rows(values_only=True):
        new_ws.append(row)

# 处理其他工作表
processed_sheets = 0
for sheet_name in wb.sheetnames:
    # 跳过"原始数据"工作表
    if sheet_name == '原始数据':
        continue

    # 读取当前工作表数据
    df = pd.read_excel(input_file, sheet_name=sheet_name)

    # 检查是否包含"打卡时间"列
    if '打卡时间' not in df.columns:
        print(f"警告：工作表 '{sheet_name}' 中未找到 '打卡时间' 列，已跳过")
        continue

    # 处理打卡时间列，按";"拆分
    # 最多拆分为4列（第一次到第四次打卡）
    punch_times = df['打卡时间'].str.split(';', expand=True, n=3)
    punch_times.columns = ['第一次打卡', '第二次打卡', '第三次打卡', '第四次打卡']

    # 合并原始数据和拆分后的打卡时间
    # 先删除原始的"打卡时间"列，再合并
    result_df = df.drop(columns=['打卡时间']).join(punch_times)

    # 确保时间格式正确（去除可能的空字符）
    for col in ['第一次打卡', '第二次打卡', '第三次打卡', '第四次打卡']:
        if col in result_df.columns:
            result_df[col] = result_df[col].str.strip()

    # 创建新工作表并写入处理后的数据
    new_ws = new_wb.create_sheet(title=sheet_name)
    for r in dataframe_to_rows(result_df, index=False, header=True):
        new_ws.append(r)

    processed_sheets += 1
    print(f"已处理工作表：{sheet_name}，拆分了 {len(result_df)} 条打卡记录")

# 保存处理后的文件
new_wb.save(output_file)
print(f"\n处理完成！共处理 {processed_sheets} 个工作表，结果已保存到 {output_file}")
