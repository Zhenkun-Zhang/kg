import json
import os

# 爬虫阶段算子数目
directory = 'dao/node/MindSpore'
json_files = []
for root, dirs, files in os.walk(directory):
    for file in files:
        if file.endswith('.json'):
            json_files.append(os.path.join(root, file))
print(f"在 {directory} 及其子文件夹中有 {len(json_files)} 个.json文件")

directory = 'dao/node/PyTorch'
json_files = []
for root, dirs, files in os.walk(directory):
    for file in files:
        if file.endswith('.json'):
            json_files.append(os.path.join(root, file))
print(f"在 {directory} 及其子文件夹中有 {len(json_files)} 个.json文件")

# 映射表算子对数目
directory = 'data/PyTorch2PaddlePaddle/api_difference'
md_file_count = 0
for root, dirs, files in os.walk(directory):
    gitkeep_path = os.path.join(root, '.gitkeep')
    if os.path.exists(gitkeep_path):
        os.remove(gitkeep_path)
        print(f"已删除 {gitkeep_path}")
    for file in files:
        if file.endswith('.md'):
            md_file_count += 1
# print(f".md 文件总数: {md_file_count}")

# 爬取阶段算子对数目
with open('dao/relation/PyTorch2MindSpore/relationship_stable--master.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
relationship_list = data["relationship"]
list_length = len(relationship_list)
print(f"算子对数目为: {list_length}")

with open('dao/relation/PyTorch2PaddlePaddle/relationship_stable--3.0-beta.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
relationship_list = data["relationship"]
list_length = len(relationship_list)
# print(f"算子对数目为: {list_length}")

# Cypher语句算子（对）数目
folder_path = "result/relation/PyTorch-PaddlePaddle"
txt_count = 0
for root, dirs, files in os.walk(folder_path):
    for file in files:
        if file.endswith('.txt'):
            txt_count += 1
# print(f"在 {folder_path} 中有 {txt_count} 个 .txt 文件")