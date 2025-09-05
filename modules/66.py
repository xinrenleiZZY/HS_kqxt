import pandas as pd
from datetime import datetime, timedelta
import os


def calculate_overtime(file_path, output_path):
    # 读取Excel文件中的所有工作表
    excel_file = pd.ExcelFile(file_path)
    sheet_names = excel_file.sheet_names

    # 创建一个ExcelWriter对象用于写入结果
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # 遍历每个工作表
        for sheet_name in sheet_names:
            # 读取当前工作表数据
            df = pd.read_excel(excel_file, sheet_name=sheet_name)

            # 确保"下班卡类型"列是字符串类型
            df['下班卡类型'] = df['下班卡类型'].astype(str)

            # 定义函数计算补贴加班时长
            def calculate_subsidy(time_str):
                try:
                    # 尝试解析时间（假设格式为HH:MM）
                    time_time = time_str.replace("下班卡", "")
                    time_obj = datetime.strptime(time_time, '%H:%M').time()
                    print(time_obj)

                    # 定义时间范围：4:00到9:00
                    start_time = datetime.strptime('04:00', '%H:%M').time()
                    end_time = datetime.strptime('09:00', '%H:%M').time()

                    # 检查时间是否在4:00到9:00之间
                    if start_time < time_obj < end_time:
                        print(time_obj)
                        # 计算与4:00的差值（小时）
                        time_diff = datetime.combine(datetime.today(), time_obj) - datetime.combine(datetime.today(),
                                                                                                    start_time)
                        print(time_diff)
                        return time_diff.total_seconds() / 3600  # 转换为小时
                    else:
                        return 0.0
                except:
                    # 处理无法解析的情况
                    return 0.0

            # 应用函数计算补贴加班时长并添加为新列
            df['补贴加班时长(小时)'] = df['下班卡类型'].apply(calculate_subsidy)

            # 将处理后的工作表写入新的Excel文件
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"处理完成！结果已保存至: {output_path}")


# 使用示例
if __name__ == "__main__":
    # 输入文件路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(current_dir, '../temp_files/全班次处理后的打卡数据.xlsx')
    # input_file = "全班次处理后的打卡数据.xlsx"
    # # 输出文件路径
    # output_file = "员工打卡记录_带补贴时长.xlsx"
    output_file = os.path.join(current_dir, '../temp_files/员工打卡记录_带补贴时长.xlsx')
    # 调用函数进行处理
    calculate_overtime(input_file, output_file)
