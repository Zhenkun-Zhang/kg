import os
import json
import requests
import re
from bs4 import BeautifulSoup
from Tools import print_hit, dealDefault

# 设置 requests 的通用头部
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36'
}

def safe_request(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        r.raise_for_status()
        return r
    except requests.exceptions.RequestException as e:
        print(f"[Warning] Failed to fetch {url}\nReason: {e}")
        return None

def safe_filename(name):
    return re.sub(r'[\\/:*?"<>|]', '_', name)

def solve(url, save_path, version):
    r = safe_request(url)
    if not r:
        print("[Error] Cannot fetch entry page.")
        return

    print(f"[INFO] Starting from: {url}")
    links = getLink(r.text, version)
    apinum = 0
    for link in links:
        apinum += 1
        print_hit(link)
        r = safe_request(link)
        if not r:
            continue
        info = getInformation(r.text)
        if not info:
            print(f"[Skip] No API info found on {link}")
            continue
        apiName, apiType, params, returns, desc, arg_list = info
        print(apinum, apiName, apiType)
        if len(returns) == 2:
            jsonDumps(apiName, apiType, params, returns, desc, version, save_path, arg_list)

def getLink(r, version):
    soup = BeautifulSoup(r, 'html.parser')
    links = []
    for a in soup.find_all('a'):
        href = a.get('href', '')
        if href.startswith(f"/documentation/docs/en/{version}/api/paddle/") \
                and not href.endswith("index_en.html") \
                and not href.endswith("Overview_en.html"):
            full_url = "https://www.paddlepaddle.org.cn" + href
            if full_url not in links:
                links.append(full_url)
    return links

def getInformation(r):
    soup = BeautifulSoup(r, 'html.parser')    

    # apiType
    apiType = "unknown"
    if not soup.find('dl', {'class': 'py attribute'}):
        apiType = 'attribute'
    if soup.find('dl', {'class': 'py function'}):
        apiType = 'function'
    if soup.find('dl', {'class': 'py class'}):
        apiType = 'class'
    if soup.find('dl', {'class': 'py method'}):
        apiType = 'method'    
    
    # apiName
    api_dt = soup.find('dt', {'class': 'sig sig-object py'})
    if not api_dt:
        return None
    api = api_dt.text.replace('\n', '').replace('\t', '')
    api_name = api.split('(')[0].split('[')[0].replace('class', '').strip()
    
    # description    
    desc = ''
    p = api_dt.findNext('dd').find('p') if api_dt.findNext('dd') else None
    if p:
        desc = p.text.replace('\n', ' ').replace('\t', ' ').replace(";", '.').split('. ')[0].strip()

    # 参数提取
    params = []
    arg_list = []
    arg_default = {}
    arg_type = {}
    if '(' in api:
        raw_args = api.split('(')[1].split(')')[0].split(',')
    else:
        raw_args = api.split(')')[0].split(',')

    for arg in raw_args:
        if ':' in arg:
            name, type_ = arg.split(':')[0].strip(), arg.split(':')[1].strip()
            arg_list.append(name)
            arg_type[name] = type_
            if '=' in arg:
                type_ = arg.split(':')[1].split('=')[0].strip()
                default = arg.split('=')[1].strip()
                arg_type[name] = type_
                arg_default[name] = default.replace(')', '')

    dd = soup.find('dd', {'class': 'field-odd'})
    if not dd:
        for order, name in enumerate(arg_list):
            params.append((name, arg_type.get(name, ''), name in arg_default, arg_default.get(name, ''), '', order))
    else:
        if "Parameters" in dd.findPrevious().text:
            lis = dd.find_all('li')
            for order, li in enumerate(lis):
                p = li.find('p')
                if not p or not p.find('strong'):
                    continue
                name = p.find('strong').text
                if name == 'name':
                    continue
                description = p.text.split('–')[-1].replace('\n', ' ').replace('\t', ' ').split('. ')[0].strip()
                param = (
                    name,
                    arg_type.get(name, ''),
                    name in arg_default,
                    arg_default.get(name, '').replace(')', ''),
                    description,
                    order
                )
                params.append(param)

    # 返回值
    returns = ['', " "]
    if '→' in api:
        returns[0] = api.split('→')[1].split('[')[0].strip()
    if dd:
        dd_return = dd.findNext('dd', {'class': 'field-even'})
        if dd_return and "Returns" in dd_return.findPrevious().text:
            p = dd_return.find('p')
            if p:
                returns[1] = p.text.replace('\\', '').split('. ')[0].strip()
    
    return api_name, apiType, params, returns, desc, arg_list

def jsonDumps(api, apiType, params, returns, desc, version, path, arg_list):
    jsDict = {}
    myParams = []
    myReturn = {'type': returns[0], 'description': returns[1]}
    for i in params:
        temp = {
            'name': i[0],
            'type': i[1],
            'optional': i[2],
            'default': dealDefault(i[3]),
            'description': dealDefault(i[4]),
            'order': i[5]
        }
        myParams.append(temp)    

    jsDict.update({
        'api': api,
        'type': apiType,
        'version': version,
        'description': desc,
        'params': myParams,
        'returns': myReturn,
        'args_list': arg_list
    })

    fileName = safe_filename(api) + '.json'
    filePath = os.path.join(path, fileName)
    if os.path.exists(filePath):
        filePath = filePath.replace(".json", "_2.json")
    os.makedirs(path, exist_ok=True)

    with open(filePath, 'w', encoding='utf-8') as f:
        json.dump(jsDict, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    version = '3.0-beta'
    url = f"https://www.paddlepaddle.org.cn/documentation/docs/en/{version}/api/index_en.html"
    save_path = f"dao/node/PaddlePaddle/{version}/"
    solve(url, save_path, version)

"""
python src/crawler/PaddlePaddleCrawler.py
"""