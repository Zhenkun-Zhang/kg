import json
import os
import sys

stdoutbak = sys.stdout
stderrbak = sys.stderr


def get_op(name):
    classes = name.split('.')
    return classes[-1]

def between_op(op1, op2, name1, name2, ver1, ver2, typeJudgement, fra1, fra2, opRelation):
    print('MATCH (m1:operator {framework: "%s", name: "%s", full_name: "%s", version: "%s"})' % (fra1, name1, op1, ver1))
    print('MATCH (m2:operator {framework: "%s", name: "%s", full_name: "%s", version: "%s"})' % (fra2, name2, op2, ver2))
    print('MERGE (m1)-[:equivalentOperator {framework_from: "%s", framework_to: "%s", typeJudgement: "%s", version_from: "%s", version_to: "%s", opRelation: "%s"}]->(m2)'  
          % (fra1, fra2, typeJudgement, ver1, ver2, opRelation))
    print('MERGE (m2)-[:equivalentOperator {framework_from: "%s", framework_to: "%s", typeJudgement: "%s", version_from: "%s", version_to: "%s", opRelation: "%s"}]->(m1);' 
          % (fra2, fra1, typeJudgement, ver2, ver1, opRelation))
    
def between_params(op1, op2, param, ver1, ver2, fra1, fra2):
    print('MATCH (m1: parameter {framework: "%s", operator: "%s", name: "%s", version: "%s"})' % (fra1, op1, list(param.values())[0], ver1))
    print('MATCH (m2: parameter {framework: "%s", operator: "%s", name: "%s", version: "%s"})' % (fra2, op2, list(param.values())[1], ver2))
    print(
        'MERGE (m1) -[: equivalentParameter {framework_from: "%s", framework_to: "%s", '
        'operator_from: "%s", operator_to: "%s", parameter_from: "%s", parameter_to : '
        '"%s", version_from:  "%s", version_to:  "%s", paRelation: "%s"}]-> (m2)' % (
        fra1, fra2, op1, op2, list(param.values())[0], list(param.values())[1], ver1, ver2, param["paRelation"]))
    print(
        'MERGE (m2) -[: equivalentParameter {framework_from: "%s", framework_to: "%s", '
        'operator_from: "%s", operator_to: "%s", parameter_from: "%s", parameter_to : '
        '"%s", version_from:  "%s", version_to:  "%s", paRelation: "%s"}]-> (m1);' % (
        fra2, fra1, op2, op1, list(param.values())[1], list(param.values())[0], ver2, ver1, param["paRelation"]))
    
def relationMaker(file_path, fra1, fra2):
    #print(file_path)
    with open(file_path, 'r', encoding='utf8') as fp:
        data = json.load(fp)
        ver1 = data[list(data.keys())[0]]
        ver2 = data[list(data.keys())[1]]
        relations = data["relationship"]
        for relation in relations:
            op1 = relation[list(relation.keys())[0]]
            op2 = relation[list(relation.keys())[1]]
            if op1 == "" or op2 == "":
                continue
            name1 = op1.split('.')[-1]
            name2 = op2.split('.')[-1]
            txt = "result/relation/" + fra1 + "-" + fra2 + "/" + ver1 + "_" + ver2 + "/" + op1 + "_" + op2 + ".txt"
            print(txt)
            dir_path = os.path.dirname(txt)  
            if not os.path.exists(dir_path):  
                os.makedirs(dir_path)
            with open(txt, "w", encoding='utf8') as f:
                sys.stdout = f
                between_op(op1, op2, name1, name2, ver1, ver2, relation["typeJudgement"], fra1, fra2, relation["opRelation"])
                params = relation['params']
                for i in params:
                    between_params(op1, op2, i, ver1, ver2, fra1, fra2)
                sys.stdout = stdoutbak

def process_project(path, fra1, fra2):
    if os.path.exists(path):
        file_list = os.listdir(path)
        for f in file_list:
            f = os.path.join(path, f)
            if os.path.isdir(f):
                process_project(f)
            else:
                file_name, extension = os.path.splitext(f)
                if extension == '.json':
                    print(f)
                    relationMaker(f, fra1, fra2)

if __name__ == '__main__': 

    fra1 = 'PyTorch'
    fra2 = 'PaddlePaddle'
    relation_path = "dao/relation/PyTorch2PaddlePaddle"
    process_project(relation_path, fra1, fra2)

    fra1 = 'PyTorch'
    fra2 = 'MindSpore'
    relation_path = "dao/relation/PyTorch2MindSpore"
    process_project(relation_path, fra1, fra2)

# python src/Cypher/BetweenCypher.py 