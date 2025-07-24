import json
import os
import sys
from Tools import deal_op, deal_return_MindSpore
stdoutbak = sys.stdout
stderrbak = sys.stderr

def deal_class_and_op(frame, version, name, type, desc, args_list):
    classes = name.split('.')
    print('merge (: framework {name: "%s", version: "%s"});' % (frame, version))
    for i in range(len(classes) - 1):
        clas = classes[i]
        print('merge (: module {framework: "%s", name: "%s", version: "%s"});' % (frame, clas, version))
        if i == 0:
            print('match')
            print(' (m1: framework {name: "%s", version: "%s"}),' % (frame, version))
            print(' (m2: module {framework: "%s", name: "%s", version: "%s"})' % (frame, clas, version))
            print('merge (m1) -[: classOfFramework {name: "%s"}]-> (m2);' % clas)
        else:
            print('match')
            print(' (m1: module {framework: "%s", name: "%s", version: "%s"}),' % (frame, classes[i - 1], version))
            print(' (m2: module {framework: "%s", name: "%s", version: "%s"})' % (frame, clas, version))
            print('merge (m1) -[: subClassOfClass {name: "%s"}]-> (m2);' % clas)
    print('merge (: operator {framework: "%s", name: "%s", full_name: "%s", version: "%s", type: "%s", description:  "%s", args_list: "%s"});' % (
        frame, classes[-1], name, version, type, desc, args_list))
    print('match')
    print(' (m3: module {framework: "%s", name: "%s", version: "%s"}),' % (frame, classes[-2], version))
    print(' (m4: operator {framework: "%s", name: "%s", full_name: "%s", version: "%s"})' % (
        frame, classes[-1], name, version))
    print('merge (m3) -[: operatorOfClass {name: "%s"}]-> (m4);' % (classes[-1]))

def deal_params(frame, version, op, params):
    for i in range(len(params)):
        param = params[i]
        print('merge (: parameter {framework: "%s", version: "%s", '
            'operator: "%s", name: "%s", description: "%s"' % (frame, 
            version, op, param["name"], param['description']), end='')
        print(', dtype: "%s"' % (param["type"]), end='')
        print(', optional: "%s"' % (param["optional"]), end='')
        print(', default: "%s"' % (param["default"]), end='')
        print(', order: "%s"' % (param["order"]), end='')
        print('});')
    print('match')
    print(' (m11: operator {framework: "%s", full_name: "%s", version: "%s"}),' % (frame, op, version))
    print(' (n11: parameter)')
    print('where n11.operator = "%s" and n11.framework = "%s" and n11.version = "%s"' % (op, frame, version))
    print('merge (m11) -[: parameterOfOperator {name: n11.name, framework: "%s", version: n11.version}] -> (n11);' % (frame))

def deal_return(frame, version, op, rets):
    print('merge (: return {framework: "%s", version: "%s", operator: "%s", name: "return", type: "%s", description: "%s"});' % (
        frame, version, op, rets['type'], rets['description']))
    print('match')
    print(' (m11: operator {framework: "%s", full_name: "%s", version: "%s"}),' % (frame, op, version))
    print(' (n11: return)')
    print('where n11.operator = "%s" and n11.framework = "%s" and n11.version = "%s"' % (op, frame, version))
    print('merge (m11) -[: returnOfOperator {name: "return", framework: "%s", version: n11.version}] -> (n11);' % (frame))

def process_project(path, json_num=0):
    if os.path.exists(path):
        file_list = os.listdir(path)
        for f in file_list:
            f = os.path.join(path, f)
            if os.path.isdir(f):
                json_num = process_project(f, json_num)
            else:
                file_name, extension = os.path.splitext(f)
                if extension == '.json':
                    try:
                        json_num += 1
                        cypherMaker(f)
                        # print(f"成功处理文件: {f}")
                    except Exception as e:
                        print(f"处理文件 {f} 时出错: {e}")
    return json_num

def cypherMaker(file_path):
    try:
        with open(file_path, 'r', encoding='utf8') as json_f:
            fra = ''
            json_data = json.load(json_f)
            args_list = json_data['args_list']
            args_list = ','.join(args_list)
            params = []           
            op = json_data["api"]
            if 'paddle' in op:
                fra = 'PaddlePaddle'
                params = json_data['params']
            if 'mindspore' in op:
                fra = 'MindSpore'
                params = json_data['Parameters']
            if 'torch' in op:
                fra = 'PyTorch'
                params = json_data['params']
            """
            if 'transformers' in op:
                fra = 'Transformers'
            
            if 'paddlenlp' in op:
                fra = 'PaddleNLP'
            """
            desc = ""
            if "description" in json_data.keys():
                desc = json_data["description"].replace("\\", "")                
            txt = "result/node/" + fra + "/" + json_data["version"] + "/" + op + ".txt"
            dir_path = os.path.dirname(txt)  
            if not os.path.exists(dir_path):  
                os.makedirs(dir_path)
            with open(txt, "w", encoding='utf8') as f:
                sys.stdout = f              
                if fra == "MindSpore":
                    deal_op(fra, json_data["version"], json_data["api"], json_data["type"], desc, args_list, json_data["Raises"], json_data["Supported_Platforms"])
                    deal_params(fra, json_data["version"], op, params)
                    deal_return_MindSpore(fra, json_data["version"], op, json_data["Returns"])
                else:
                    deal_class_and_op(fra, json_data["version"], json_data["api"], json_data["type"], desc, args_list)
                    deal_params(fra, json_data["version"], op, params)
                    if json_data["returns"]['type'] or json_data["returns"]['description']:
                        deal_return(fra, json_data["version"], op, json_data["returns"])
                sys.stdout = sys.__stdout__
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")

def main():
    project_path = "dao/node"
    # project_path = "dao/node/MindSpore"
    process_project(project_path)
    # project_path = "dao/node/PaddlePaddle"
    # process_project(project_path)
    # project_path = "dao/node/PyTorch"
    # process_project(project_path)
    

if __name__ == '__main__':
    main()
# python3 src/knowledge_graph/WithinCyphermaker.py 