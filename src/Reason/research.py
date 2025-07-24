import json, os

# 图谱中“指定要求”数目
# equivalentOperator
query = """
MATCH (n:operator)-
[r: equivalentOperator {framework_from: 'PyTorch', framework_to: 'MindSpore'}]->(m: operator)
RETURN n, r, m
"""
query = """
MATCH (n:operator {framework: 'PyTorch'})-
[r: equivalentOperator]->(m: operator {framework: 'PaddlePaddle'})
RETURN n, r, m
"""
query = """
MATCH (n:operator {framework: 'MindSpore'})-
[r: equivalentOperator]->(m: operator {framework: 'PyTorch'})
RETURN n, r, m
"""
query = """
MATCH (n:operator {framework: 'PaddlePaddle'})-
[r: equivalentOperator]->(m: operator {framework: 'PyTorch'})
RETURN n, r, m
"""
query = """
MATCH (n:operator {framework: 'MindSpore'})-
[r: equivalentOperator]->(m: operator {framework: 'PaddlePaddle'})
RETURN n, r, m
"""
query = """
MATCH (n:operator {framework: 'PaddlePaddle'})-
[r: equivalentOperator]->(m: operator {framework: 'MindSpore'})
RETURN n, r, m
"""

# equivalentParameter
query = """
MATCH (n:parameter {framework: 'PyTorch'})-
[r: equivalentParameter]->(m: parameter {framework: 'MindSpore'})
RETURN n, r, m
"""
query = """
MATCH (n:parameter {framework: 'MindSpore'})-
[r: equivalentParameter]->(m: parameter {framework: 'PaddlePaddle'})
RETURN n, r, m
"""
query = """
MATCH (n:parameter {framework: 'MindSpore'})-
[r: equivalentParameter]->(m: parameter {framework: 'PyTorch'})
RETURN n, r, m
"""
query = """
MATCH (n:parameter {framework: 'PaddlePaddle'})-
[r: equivalentParameter]->(m: parameter {framework: 'MindSpore'})
RETURN n, r, m
"""
query = """
MATCH (n:parameter {framework: 'PaddlePaddle'})-
[r: equivalentParameter]->(m: parameter {framework: 'PyTorch'})
RETURN n, r, m
"""
query = """
MATCH (n:parameter {framework: 'PyTorch'})-
[r: equivalentParameter]->(m: parameter {framework: 'PaddlePaddle'})
RETURN n, r, m
"""

# operator
query = """
MATCH (n:operator {framework: 'PyTorch'}) RETURN n
"""
query = """
MATCH (n:operator {framework: 'MindSpore'}) RETURN n
"""
query = """
MATCH (n:operator {framework: 'PaddlePaddle'}) RETURN n
"""

# subClassOfClass
query = """
MATCH (n:module {framework: 'PyTorch'})-
[r: subClassOfClass]->(m: module {framework: 'PyTorch'})
RETURN n, r, m
"""
query = """
MATCH (n:module {framework: 'PaddlePaddle'})-
[r: subClassOfClass]->(m: module {framework: 'PaddlePaddle'})
RETURN n, r, m
"""
query = """
MATCH (n:module {framework: 'MindSpore'})-
[r: subClassOfClass]->(m: module {framework: 'MindSpore'})
RETURN n, r, m
"""

# operatorOfClass
query = """
MATCH (n:module {framework: 'PyTorch'})-
[r: operatorOfClass]->(m: operator {framework: 'PyTorch'})
RETURN n, r, m
"""
query = """
MATCH (n:module {framework: 'PaddlePaddle'})-
[r: operatorOfClass]->(m: operator {framework: 'PaddlePaddle'})
RETURN n, r, m
"""
query = """
MATCH (n:module {framework: 'MindSpore'})-
[r: operatorOfClass]->(m: operator {framework: 'MindSpore'})
RETURN n, r, m
"""

# parameterOfOperator
query = """
MATCH (n:operator {framework: 'PyTorch'})-
[r: parameterOfOperator]->(m: parameter {framework: 'PyTorch'})
RETURN n, r, m
"""
query = """
MATCH (n:operator {framework: 'PaddlePaddle'})-
[r: parameterOfOperator]->(m: parameter {framework: 'PaddlePaddle'})
RETURN n, r, m
"""
query = """
MATCH (n:operator {framework: 'MindSpore'})-
[r: parameterOfOperator]->(m: parameter {framework: 'MindSpore'})
RETURN n, r, m
"""

# returnOfOperator
query = """
MATCH (n:operator {framework: 'PyTorch'})-
[r: returnOfOperator]->(m: return {framework: 'PyTorch'})
RETURN n, r, m
"""
query = """
MATCH (n:operator {framework: 'MindSpore'})-
[r: returnOfOperator]->(m: return {framework: 'MindSpore'})
RETURN n, r, m
"""
query = """
MATCH (n:operator {framework: 'PaddlePaddle'})-
[r: returnOfOperator]->(m: return {framework: 'PaddlePaddle'})
RETURN n, r, m
"""

# 算子json
directory = 'dao/node/MindSpore'
directory = 'dao/node/PaddlePaddle'
# irectory = 'dao/node/PyTorch'
directory = 'dao/node/Transformers'
json_files = []
for root, dirs, files in os.walk(directory):
    for file in files:
        if file.endswith('.json'):
            json_files.append(os.path.join(root, file))
print(f"在 {directory} 及其子文件夹中有 {len(json_files)} 个.json文件")

# 算子对md
# data/PyTorch2PaddlePaddle计算该文件夹内md文件的数量
directory = 'data/PyTorch2PaddlePaddle'
md_files = []
for root, dirs, files in os.walk(directory):
    for file in files:
        if file.endswith('.md'):
            md_files.append(os.path.join(root, file))
print(f"在 {directory} 及其子文件夹中有 {len(md_files)} 个.md文件")

# 算子对json
with open('dao/relation/PyTorch_stable--PaddlePaddle_develop/relationship_PyTorch2PaddlePaddle.json', 'r', encoding='utf-8') as file:
# with open('dao/relation/PyTorch_stable--MindSpore_master/relationship_PyTorch2MindSpore.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
relationship_list = data["relationship"]
list_length = len(relationship_list)
# 把文件路径也打印出来
print(f"算子对文件路径为: {file}")
print(f"算子对数目为: {list_length}")


# Cypher 
folder_path = "result/relation/PyTorch-PaddlePaddle"
# folder_path = "result/node/PaddlePaddle"
# folder_path = "result/node/PyTorch"
# folder_path = "result/node/MindSpore"
# folder_path = "result/relation/PyTorch-MindSpore"
txt_count = 0
for root, dirs, files in os.walk(folder_path):
    for file in files:
        if file.endswith('.txt'):
            txt_count += 1
print(f"在 {folder_path} 中有 {txt_count} 个 .txt 文件")
