import pandas as pd
from datetime import datetime
import os


def process_checkin_time(time_str):
    """处理打卡时间，空值直接返回不处理
    规则：如果第一次打卡时间小于12:00则处理，大于12:00则不处理
    """
    # 检查是否为空值或空字符串
    if pd.isna(time_str) or str(time_str).strip() == '':
        return time_str

    # 分割多个打卡时间
    times = [t.strip() for t in str(time_str).split(';') if t.strip()]
    if len(times) <= 4:
        return time_str

    # 转换为datetime对象便于比较
    try:
        time_objs = [datetime.strptime(t, '%H:%M') for t in times]
    except ValueError:
        return time_str  # 格式错误时返回原始值

    # 获取第一次打卡时间，判断是否需要处理
    first_checkin = min(time_objs)  # 最早的打卡时间
    noon = datetime.strptime('12:00', '%H:%M')

    # 如果第一次打卡时间大于12:00，不处理
    if first_checkin > noon:
        return time_str

    # 定义时间界限
    end_limit = datetime.strptime('17:30', '%H:%M')

    # 分类时间
    before_noon = [t for t in time_objs if t < noon]
    between = [t for t in time_objs if noon <= t <= end_limit]
    after = [t for t in time_objs if t > end_limit]

    # 按规则筛选
    result = []
    # 小于12:00的保留最后一个
    if before_noon:
        result.append(max(before_noon))
    # 12:00到17:30保留第一个和最后一个
    if between:
        result.append(min(between))
        if len(between) > 1:
            result.append(max(between))
    # 剩下的时间取最后一个作为第四次打卡
    if after:
        result.append(max(after))

    # 转换回字符串格式
    return ';'.join([t.strftime('%H:%M') for t in result])


def process_excel_file(file_path, output_path):
    """处理Excel文件，忽略原始数据工作表"""
    # 读取所有工作表
    xls = pd.ExcelFile(file_path)
    sheet_names = xls.sheet_names

    # 创建ExcelWriter用于写入结果
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for sheet in sheet_names:
            # 跳过原始数据工作表
            if sheet == '原始数据':
                continue

            # 读取工作表数据
            df = pd.read_excel(xls, sheet_name=sheet)

            # 检查是否存在"打卡时间"列
            if '打卡时间' in df.columns:
                # 处理所有打卡时间（根据第一次打卡时间自动判断是否需要处理）
                mask = (df['打卡时间'].notna()) & (df['打卡时间'].astype(str).str.strip() != '')
                df.loc[mask, '打卡时间'] = df.loc[mask, '打卡时间'].apply(process_checkin_time)

            # 写入处理后的工作表
            df.to_excel(writer, sheet_name=sheet, index=False)

    print(f"处理完成，结果已保存至: {output_path}")


# 使用示例
if __name__ == "__main__":
    # 读取Excel文件
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(current_dir, '../temp_files/按日期分表的打卡数据.xlsx')
    output_file = os.path.join(current_dir, '../temp_files/按日期分表的处理打卡数据.xlsx')
    process_excel_file(input_file, output_file)