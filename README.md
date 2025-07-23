# 项目目录

KGForDLFrame

- dao: 存放爬虫所得数据，json；X2paddle数据，md
  
- doc: 算子知识图谱设计文档

- result: 生成的cypher语句, txt

- src: 运行程序
  - crawler: 爬虫程序
    - Crawler.py: 爬取信息
    - Tools.py: 爬虫信息所需函数
  - kg: 生成cypher语句及构建图谱程序
    - knowledheGraph.py:
  - convert: 生成paconvert中的json文件
    - paconvert.py:

## 项目流程

1. 爬取算子信息、框架间算子对应信息等存入dao, json;
  ‘’‘
  python3 src/crawler/Crawler.py
  ’‘’

2. 将json信息转成Cypher语句并存入图谱
  ’‘’
  python3 kg/knowledgeGraph.py
  ’‘’

3. 利用图谱生成paconvert中的json文件
  ’‘’
  python3 convert/paconvert.py
  ’‘’