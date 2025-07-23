import markdown
import os
import json
import re
from bs4 import BeautifulSoup
from Tools import Empty

def contains_chinese(text):
    return bool(re.search('[\u4e00-\u9fa5]', text))

def PyTorch2PaddlePaddle(url, root_path, save_path, PyTorchVersion, PaddlePaddleVersion):
    list = []
    for root, dirs, files in os.walk(url):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file) 
                with open(file_path, 'r', encoding='utf-8') as f:
                    md_content = f.read() 
                md = markdown.Markdown(extensions=['extra'])
                html_output = md.convert(md_content)
                Relation = getRelation(html_output, root_path, PyTorchVersion, PaddlePaddleVersion)
                list.extend(Relation)
    JsonDumps(list, save_path, PyTorchVersion, PaddlePaddleVersion)

def getRelation(req, root_path,  PyTorchVersion, PaddlePaddleVersion):
    Relation = []
    soup = BeautifulSoup(req, 'html.parser')
    name = soup.findAll('code', class_="language-python")
    if len(name) < 2:
        return []
    PyTorchName = name[0].text.split('(')[0].strip()
    if '\n' in PyTorchName:
        PyTorchName = PyTorchName.split('\n')[1].strip()
    PaddlePaddleName = name[1].text.split('(')[0].strip()
    if '\n' in PaddlePaddleName:
        PaddlePaddleName = PaddlePaddleName.split('\n')[1].strip()
    if 'paddle' not in PaddlePaddleName.lower():
        PaddlePaddleName = ''
    opRelation = soup.find('h2').text.split(']')[0].split('[')[1].strip()
    typeJudgement = ""
    params = []
    table = soup.find('tbody')     
    if table:
        trList = table.find_all('tr')
        for tr in trList:
            tdList = tr.find_all('td')
            params.append({"PyTorch": tdList[0].text, "PaddlePaddle": tdList[1].text, "paRelation": tdList[2].text.replace('；', '.').replace('\"', '')})
    typeJudgement = getFromJson(PyTorchName, PaddlePaddleName, root_path, PyTorchVersion, PaddlePaddleVersion)
    if typeJudgement:
        Relation.append((PyTorchName, PaddlePaddleName, opRelation, typeJudgement, params))
    return Relation

def getFromJson(PyTorchName, PaddlePaddleName, root_path, PyTorchVersion, PaddlePaddleVersion):
    flag = False
    path = 'dao/relation/empty_PyTorch2PaddlePaddle.txt'
    typeJudgement = "True"
    PyTorchType = ""
    for file in os.listdir(root_path + 'PyTorch/' + PyTorchVersion):
        for secondFile in os.listdir(root_path + 'PyTorch/' + PyTorchVersion + '/' + file):
            # print(secondFile, torchName)
            if secondFile.lower() == PyTorchName.lower() + '.json':
                with open(root_path + 'PyTorch/' + PyTorchVersion + '/' +file + '/' + secondFile, 'r', encoding='utf-8') as f:
                    PyTorchFile = json.load(f)
                    PyTorchType = PyTorchFile['type']
                flag = True
                break
    if not flag:
        Empty(path, PyTorchName)
        return False
    flag = False
    PaddlePaddleType = ""
    for file in os.listdir(root_path + 'PaddlePaddle/' + PaddlePaddleVersion):
        if file.lower() == PaddlePaddleName.lower() + '.json':
            with open(root_path + 'PaddlePaddle/' + PaddlePaddleVersion + '/' + file, 'r', encoding='utf-8') as f:
                PaddlePaddleFile = json.load(f)
                PaddlePaddleType = PaddlePaddleFile['type']
            flag = True
            break
    if not flag:
        Empty(path, PaddlePaddleName)
        return False
    if PaddlePaddleType != PyTorchType:
        typeJudgement = "False"
    return typeJudgement

def JsonDumps(Relation, path, PyTorchVersion, PaddlePaddleVersion):
    jsDict = {}
    jsDict['PyTorchVersion'] = PyTorchVersion
    jsDict['PaddlePaddleVersion'] = PaddlePaddleVersion
    relationShip = []
    for apis in Relation:
        relationShip.append({'PyTorch': apis[0], 'PaddlePaddle': apis[1], 'opRelation': apis[2], 'typeJudgement': apis[3], 'params': apis[4]})
    jsDict['relationship'] = relationShip
    if not os.path.exists(path):
        os.makedirs(path)
    with open(path + 'relationship_' + PyTorchVersion + '--' + PaddlePaddleVersion + '.json', 'w', encoding='utf-8') as f:
        json.dump(jsDict, f, ensure_ascii = False, indent=4)

def main():
    PyTorchVersion = 'stable'
    PaddlePaddleVersion = '3.0-beta'
    url = "data/api_difference/"
    root_path = "dao/node/"
    save_path = "dao/relation/PyTorch2PaddlePaddle/"
    PyTorch2PaddlePaddle(url, root_path, save_path, PyTorchVersion, PaddlePaddleVersion)

if __name__ == '__main__':
    main()
    with open('dao/relation/PyTorch2PaddlePaddle/relationship_stable--3.0-beta.json', 'r', encoding='utf-8') as file:
       data = json.load(file)
    relationship_list = data["relationship"]
    list_length = len(relationship_list)
    print(f"算子对文件路径为: {file}")
    print(f"算子对数目为: {list_length}")

# python src/crawler/PyTorch2PaddlePaddle.py
