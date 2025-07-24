from py2neo import Graph
import pandas as pd
import os

# 连接数据库
graph = Graph("bolt://localhost:7687", auth=("neo4j", "613613zzk"))

# 执行查询
framework = 'PyTorch'
framework = 'MindSpore'
query = 'MATCH (n:operator {framework: "%s"}) RETURN n' % (framework)
results = graph.run(query)

# 初始化列表
API = []
Relation = []
for record in results:
    api = record['n']    
    frame = api['framework']
    version = api['version']
    full_name = api['full_name']
    name = api['name']
    type = api['type']
    desc = api['description']
    args_list = api['args_list']
    API.append((frame, version, full_name, name, type, desc, args_list))
# 将列表转换为DataFrame
df = pd.DataFrame(API, columns=['Framework', 'Version', 'Full Name', 'Name', 'Type', 'Description', 'Args List'])

# 指定保存路径
save_path = 'dao/node/PyTorch'
save_path = 'dao/node/PaddlePaddle'
save_path = 'dao/node/MindSpore'
os.makedirs(save_path, exist_ok=True)  # 确保目录存在

# 写入Excel文件
file_path = os.path.join(save_path, '%s-operators.xlsx' % (framework))
df.to_excel(file_path, index=False)

