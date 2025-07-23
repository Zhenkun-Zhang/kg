import os
import json
import shutil

def log_error(message):
    """将错误信息写入日志文件"""
    with open('error_log.txt', 'a', encoding='utf-8') as log_file:
        log_file.write(message + '\n')

def update_order_in_json(input_file_path, output_file_path):
    try:
        # 读取 JSON 文件
        with open(input_file_path, 'r', encoding='utf-8') as infile:
            data = json.load(infile)
        
        # 获取 params 列表
        params = data.get("params", [])
        
        # 按照 `order` 排序参数
        params.sort(key=lambda x: x["order"])
        
        # 更新 `order` 为连续的值
        for i, param in enumerate(params):
            param["order"] = i
        
        # 将修改后的数据写入输出文件
        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile, ensure_ascii=False, indent=4)
        
        print(f"Processed and saved: {output_file_path}")
    
    except json.JSONDecodeError as e:
        error_message = f"Error decoding JSON from file {input_file_path}: {e}"
        print(error_message)
        log_error(error_message)
    
    except IOError as e:
        error_message = f"Error reading or writing file {input_file_path} or {output_file_path}: {e}"
        print(error_message)
        log_error(error_message)
    
    except Exception as e:
        error_message = f"Unexpected error processing file {input_file_path}: {e}"
        print(error_message)
        log_error(error_message)

def process_json_files(input_dir, output_dir):
    # 遍历输入目录中的所有子文件夹和文件
    for root, dirs, files in os.walk(input_dir):
        for file_name in files:
            if file_name.endswith('.json'):
                try:
                    input_file_path = os.path.join(root, file_name)
                    
                    # 计算相对路径，并保持相同的文件夹结构
                    relative_path = os.path.relpath(root, input_dir)
                    output_folder = os.path.join(output_dir, relative_path)
                    os.makedirs(output_folder, exist_ok=True)
                    
                    # 生成输出文件路径
                    output_file_path = os.path.join(output_folder, file_name)
                    
                    # 更新 JSON 文件中的 order 字段
                    update_order_in_json(input_file_path, output_file_path)
                
                except Exception as e:
                    error_message = f"Failed to process {file_name} in {root}: {e}"
                    print(error_message)
                    log_error(error_message)

# 设置输入目录和输出目录
input_directory = 'dao/node/PyTorch/stable2'  # 输入文件所在目录
output_directory = 'dao/node/PyTorch/stable'  # 输出结果保存目录

# 批量处理文件
process_json_files(input_directory, output_directory)