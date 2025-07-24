from py2neo import Graph

graph = Graph("bolt://localhost:7687", auth=("neo4j", "613613zzk"))
query = """MATCH (n:operator {framework: 'PyTorch'})-[r:equivalentOperator]->(m: operator {framework: 'PaddlePaddle'}) RETURN n, r, m"""
results = graph.run(query)
PyTorch = []
PaddlePaddle = []
for record in results:
    PyTorch.append(record['n']['full_name'])
    PaddlePaddle.append(record['m']['full_name'])
# print(PyTorch)
# print(PaddlePaddle)
query2 = """MATCH (n:operator)-
[r: equivalentOperator {framework_from: 'PyTorch', framework_to: 'MindSpore'}]->(m: operator)
RETURN n, r, m"""
results2 = graph.run(query2)
PyTorch2 = []
MindSpore = []
for record in results2:
    PyTorch2.append((record['n']['full_name'], record['n']['args_list']))
    MindSpore.append(record['m']['full_name'])
# print(PyTorch2)
reason_parameter = []
a = 0
parameters_torch2ms = []
parameters_ms = []
query_parameter_torch2ms = """MATCH (n:parameter {framework: 'PyTorch'})-
[r: equivalentParameter {framework_from: 'PyTorch', framework_to: 'MindSpore'}]->(m: parameter)
RETURN n, r, m"""
results_parameter_torch2ms = graph.run(query_parameter_torch2ms)
for record in results_parameter_torch2ms:
    parameters_torch2ms.append((record['n']['name'], record['n']['operator']))
    parameters_ms.append((record['m']['name'], record['m']['operator']))

parameters_torch2pp = []
parameters_pp = []
query_parameter_torch2pp = """MATCH (n:parameter {framework: 'PyTorch'})-
[r: equivalentParameter {framework_from: 'PyTorch', framework_to: 'PaddlePaddle'}]->(m: parameter)
RETURN n, r, m"""
results_parameter_torch2pp = graph.run(query_parameter_torch2pp)
for record in results_parameter_torch2pp:
    parameters_torch2pp.append((record['n']['name'], record['n']['operator']))
    parameters_pp.append((record['m']['name'], record['m']['operator']))

for i in range(len(PyTorch2)):
    if PyTorch2[i][0] in PyTorch:
        # 找到 PyTorch 中对应的索引
        index = PyTorch.index(PyTorch2[i][0])
        md_api = MindSpore[i]
        paddle_api = PaddlePaddle[index]  # 使用对应索引
        write = graph.run("""
            MATCH (op1:operator {framework: 'MindSpore', full_name: '%s'})
            MATCH (op2:operator {framework: 'PaddlePaddle', full_name: '%s'})
            CREATE (op2)-[:equivalentOperator {relation: 'Reasoning', framework_from: 'PaddlePaddle', 
              framework_to: 'MindSpore', version_from: op2.version, version_to: op1.version}]->(op1)
            CREATE (op1)-[:equivalentOperator {relation: 'Reasoning', framework_from: 'MindSpore', 
              framework_to: 'PaddlePaddle', version_from: op1.version, version_to: op2.version}]->(op2)
        """ % (md_api, paddle_api))

for i in range(len(parameters_torch2ms)):
    for j in range(len(parameters_torch2pp)):
        if parameters_torch2ms[i] == parameters_torch2pp[j]:
            # 检查是否属于同一个 PyTorch 算子
            if parameters_torch2ms[i][1] == parameters_torch2pp[j][1]:
                a += 1
                paddle_api = parameters_pp[j][1]
                paddle_parameter = parameters_pp[j][0]
                ms_api = parameters_ms[i][1]
                ms_parameter = parameters_ms[i][0]
                write = graph.run("""
                    MATCH (op1:parameter {framework: 'MindSpore', name: '%s', operator: '%s'})
                    MATCH (op2:parameter {framework: 'PaddlePaddle', name: '%s', operator: '%s'})
                    CREATE (op1)-[:equivalentParameter {relation: 'Reasoning', framework_from: 'PaddlePaddle', 
                      framework_to: 'MindSpore', version_from: op2.version, version_to: op1.version}]->(op2)
                    CREATE (op2)-[:equivalentParameter {relation: 'Reasoning', framework_from: 'MindSpore', 
                      framework_to: 'PaddlePaddle', version_from: op1.version, version_to: op2.version}]->(op1)
                """ % (ms_parameter, ms_api, paddle_parameter, paddle_api))

# python src/PaddlePaddle2MindSpore/Reasoning.py