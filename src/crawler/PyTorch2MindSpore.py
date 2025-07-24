import os
import requests
import json
from bs4 import BeautifulSoup

def getRelation(req, root_path, PyTorchVersion, MindSporeVersion):
    soup = BeautifulSoup(req, 'html.parser')
    tbodyList = soup.find_all('tbody')[1:] # the first tbody isn't needed
    Relation = []
    api_num = 0
    for tbody in tbodyList:
        trList = tbody.find_all('tr')
        for tr in trList:
            tdList = tr.find_all('td')
            if len(tdList) == 3:
                api_num += 1
                href = ['diff', 
                        'The functions are consistent, but the number or sequence of parameters is inconsistent.', 
                        'The functions are consistent, but the parameter data types are inconsistent', 
                        'The functions are consistent, but the parameter default values are inconsistent.']
                paramsRelation = []
                params = []
                if tdList[2].text in href:
                    params, paramsRelation = getDifferencePage(params, paramsRelation, requests.get(tdList[2].find('a')['href']).text)
                PyTorch_name = tdList[0].text.strip()
                MindSpore_name = tdList[1].text.strip()
                if '：' in PyTorch_name:
                    PyTorch_name = PyTorch_name.split('：')[1]
                if '\n' in PyTorch_name:
                    PyTorch_name = PyTorch_name.split('\n')[1]
                typeJudgement, paramsRelation = getFromJson(params, paramsRelation, PyTorch_name, MindSpore_name, root_path, PyTorchVersion, MindSporeVersion)
                Relation.append((PyTorch_name, MindSpore_name, tdList[2].text.replace('"', '').replace(";", '.').strip(), typeJudgement, paramsRelation))                      
    print(api_num)
    return Relation

def getDifferencePage(params, paramsRelation, req):
    soup = BeautifulSoup(req,  'html.parser')
    tbodyList = soup.find_all('tbody')
    if len(tbodyList) == 0:
        return params, paramsRelation
    for table in tbodyList:
        trList = table.find_all('tr')
        for tr in trList:
            tdList = tr.find_all('td')
            if len(tdList) != 5:
                continue
            if (tdList[2].text, tdList[3].text) in params:
                continue
            params.append((tdList[2].text, tdList[3].text))
            paramsRelation.append((tdList[2].text, tdList[3].text, tdList[4].text.replace('"', '').replace(";", '.').strip()))
    return params, paramsRelation

def getFromJson(params, paramsRelation, PyTorchName, MindSporeName, root_path, PyTorchVersion, MindSporeVersion):
    typeJudgement = "True"
    PyTorchParam = []
    flag = False
    PyTorchType = ""
    for file in os.listdir(root_path + 'PyTorch/' + PyTorchVersion):
        for secondFile in os.listdir(root_path + 'PyTorch/' + PyTorchVersion + '/' + file):
            if secondFile.lower() == PyTorchName.lower() + '.json':
                with open(root_path + 'PyTorch/' + PyTorchVersion + '/' + file + '/' + secondFile, 'r', encoding='utf-8') as f:
                    PyTorchFile = json.load(f)
                    PyTorchType = PyTorchFile['type']
                    for dic in PyTorchFile['params']:
                        PyTorchParam.append(dic['name'])
                flag = True
                break
    if not flag:
        return "", []
    flag = False
    MindSporeParam = []
    MindSporeType = ""
    for file in os.listdir(root_path + 'MindSpore/' + MindSporeVersion):
        for secondFile in os.listdir(root_path + 'MindSpore/' + MindSporeVersion + '/' + file):
            if secondFile.lower() == MindSporeName.lower() + '.json':
                with open(root_path + 'MindSpore/' + MindSporeVersion + '/' + file + '/' + secondFile, 'r', encoding='utf-8') as f:
                    MindSporeFile = json.load(f)
                    MindSporeType = MindSporeFile['type']
                    for dic in MindSporeFile['Parameters']:
                        MindSporeParam.append(dic['name'])
                flag = True
                break
    if not flag:
        return "", []
    for i in PyTorchParam:
        if (i, i) in params:
            continue
        if i in MindSporeParam:
            paramsRelation.append((i, i, 'The names of the parameters are consistent.'))
    if PyTorchType != MindSporeType:
        typeJudgement = "False"
    for i in paramsRelation:
        if i[0] not in PyTorchParam:
            paramsRelation.remove(i)
            for j in PyTorchParam:
                if i[0] in j:
                    paramsRelation.append((j, i[1], i[2]))
                    
    return typeJudgement, paramsRelation

def jsonDumps(Relation, path, PyTorchVersion, MindSporeVersion):
    jsDict = {}
    jsDict['PyTorchVersion'] = PyTorchVersion
    jsDict['MindSporeVersion'] = MindSporeVersion
    relationShip = []
    for name1, name2, opRelation, typeJudgement, params in Relation:
        tempParams = []
        for param1, param2, paRelation in params:
            tempParams.append({'PyTorch': param1, 'MindSpore': param2, 'paRelation': paRelation})
        relationShip.append({'PyTorch': name1, 'MindSpore': name2, 'opRelation': opRelation, 'typeJudgement': typeJudgement, 'params': tempParams})
    jsDict['relationship'] = relationShip
    if not os.path.exists(path):
        os.makedirs(path)
    file_path = os.path.join(path, 'relationship_' + PyTorchVersion + '--' + MindSporeVersion + '.json')
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(jsDict, f, indent=4)

def main():
    PyTorchVersion = 'stable'
    MindSporeVersion = 'master'
    url = "https://www.mindspore.cn/docs/en/" + MindSporeVersion + "/note/api_mapping/pytorch_api_mapping.html"
    # print(url)
    root_path = "dao/node/"
    save_path = "dao/relation/PyTorch2MindSpore/"
    r = requests.get(url)
    Relation = getRelation(r.text, root_path, PyTorchVersion, MindSporeVersion)
    jsonDumps(Relation, save_path, PyTorchVersion, MindSporeVersion)

  
if __name__ == '__main__':
    main()
    


# python src/crawler/PyTorch2MindSpore.py