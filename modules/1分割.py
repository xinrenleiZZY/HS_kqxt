import pandas as pd

# 读取Excel文件
file_path = '../temp_files/原始文件.xlsx'
xls = pd.ExcelFile(file_path)

# 获取第一个工作表的名称作为tm值
first_sheet_name = xls.sheet_names[0]  # 获取第一个工作表的名称
tm = first_sheet_name  # 将工作表名称赋值给tm
print(f"获取到的工作表前缀（第一个工作表名称）: {tm}")

# 读取第一个工作表的主要数据
df = pd.read_excel(xls, sheet_name=first_sheet_name)

# 创建一个新的Excel写入器
output_file = '../temp_files/按日期分表的打卡数据.xlsx'
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    # 首先写入原始数据作为第一个工作表
    df.to_excel(writer, sheet_name='原始数据', index=False)
    # 统计有效日期列的数量
    valid_days = 0

    # 循环处理每一天（1到31）
    for day in range(1, 100):
        # 检查该日期列是否存在（列名是数字类型）
        if day in df.columns:
            # 选择需要的列
            selected_columns = ['姓名', '员工ID', '部门', '班次', day]
            # 复制选定的列到新的DataFrame
            day_df = df[selected_columns].copy()
            # 将日期列重命名为'打卡时间'
            day_df.rename(columns={day: '打卡时间'}, inplace=True)

            if not day_df.empty:
                # 使用第一个工作表名称作为前缀创建工作表名称（例如：2025年7月1日）
                sheet_name = f'{tm}{day}日'
                day_df.to_excel(writer, sheet_name=sheet_name, index=False)
                valid_days += 1
                print(f"已创建 {sheet_name} 工作表，包含 {len(day_df)} 条记录")

    print(f"\n总计创建了 {valid_days} 个日期工作表")

print(f"\n已成功将数据按日期拆分到 {output_file} 中的多个工作表")
