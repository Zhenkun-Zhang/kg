# pytorch_crawler_full.py
import os
import json
import re
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from Tools import print_hit, dealDefault, get_args

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36'
}

apis = ['torch', 'nn', 'nn.functional', 'tensors', 'autograd', 'accelerator',
        'cpu', 'cuda', 'mps', 'xpu', 'mtia', 'mtia.memory', 'fft', 
        'fx.experimental', 'jit', 'linalg', 'signal', 'nn.attention', 'optim',
        'sparse', 'utils', 'logging']
# apis = []
directApis = ['tensors', 'tensor_attributes', 'amp', 'autograd', 'library',
              'torch_cuda_memory', 'backends', 'export', 'distributed',
              'distributed.tensor', 'distributed.algorithms.join', 'fsdp',
              'distributed.fsdp.fully_shard', 'distributed.tensor.parallel',
              'distributed.optim', 'distributed.pipelining',
              'distributed.checkpoint', 'distributions', 'futures', 'fx',
              'hub', 'jit', 'monitor', 'special', 'torch.overrides', 'package',
              'profiler', 'nn.init', 'optim', 'ddp_comm_hooks', 'rpc', 'random',
              'nested', 'size', 'storage', 'testing', 'benchmark_utils', 
              'checkpoint', 'cpp_extension', 'data', 'deterministic', 'dlpack',
              'model_zoo', 'tensorboard', 'module_tracker', 'named_tensor',
              'config_mod', 'future_mod']
# directApis = []

specialName = {"torch.torch.dtype": "torch.dtype", "torch.torch.device": "torch.device", "torch.torch.layout": "torch.layout", "torch.torch.memory_format": "torch.memory_format"}

def safe_request(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        return r
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch {url}: {e}")
        return None

def safe_filename(name):
    return re.sub(r'[\\/:*?"<>|]', '_', name)

def solve(version='stable', max_workers=8):
    root = f"https://pytorch.org/docs/{version}/"
    save_path = os.path.join("dao", "node", "PyTorch", version)
    os.makedirs(save_path, exist_ok=True)

    api_num = 0
    failed = []

    # 处理 apis（间接）
    def handle_api(api):
        nonlocal api_num
        url = root + api + '.html'
        r = safe_request(url)
        if not r:
            failed.append(url)
            return
        links = getRef(r.text, version)
        for link in links:
            r = safe_request(link)
            if not r:
                failed.append(link)
                continue
            print_hit(link)
            api_num += 1            
            apiName = link.split('#')[1]
            soup = BeautifulSoup(r.text, 'html.parser')
            dl = soup.find('dl')
            apiType = dl.attrs['class'][1] if dl and dl.has_attr('class') else 'unknown'
            print(api_num, apiName, apiType)
            args_list, params, returns, desc, methodFlag = getInformation(r.text, apiType)
            path = os.path.join(save_path, api)
            jsonDumps(apiName, apiType, args_list, params, returns, desc, path, version)
            if methodFlag:
                api_num = getDL(r.text, path, version, api_num)

    # 处理 directApis（直接）
    def handle_direct(api):
        nonlocal api_num
        url = root + api + '.html'
        print_hit(url)
        r = safe_request(url)
        if not r:
            failed.append(url)
            return
        api_num = getDl(r.text, os.path.join(save_path, api), version, api_num)

    # 多线程执行
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        tasks = [executor.submit(handle_api, api) for api in apis] + [executor.submit(handle_direct, api) for api in directApis]
        for _ in tqdm(as_completed(tasks), total=len(tasks), desc="Crawling"):
            pass

    print(f"[SUMMARY] Total: {api_num}, Failed: {len(failed)}")
    if failed:
        with open("failed_apis.txt", "w") as f:
            for item in failed:
                f.write(item + "\n")

def getRef(req, version):
    soup = BeautifulSoup(req, 'html.parser')
    ref = soup.find_all('tr', class_=['row-odd', 'row-even'])
    links = []
    for i in ref:
        a = i.find('a', class_='reference internal')
        if a and a['href']:
            full_url = f"https://pytorch.org/docs/{version}/{a['href']}"
            links.append(full_url)
    return links

def getInformation(req, apiType):
    soup = BeautifulSoup(req, 'html.parser')
    methodFlag = False
    if apiType == 'class':
        if soup.find_all('dl', {'class': 'method'}):
            methodFlag = True
        for dl in soup.find_all('dl', {'class': 'method'}):
            dl.extract()

    args_list, args_default = get_args(soup)

    desc = ""
    dd = soup.find('dl').find('dd') if soup.find('dl') else None
    if dd:
        p = dd.find('p')
        while p:
            desc += p.text + ' '
            p = p.findNext('p')
            if p and (p.parent.attrs.get('class') or p.parent.attrs.get('role')):
                break
        desc = desc.replace('\n', ' ').replace('\t', ' ').replace('"', '').replace(';', ',').strip().split('.')[0]

    params = []
    dts = soup.find_all('dt')
    for dt in dts:
        if dt.string in ['Keyword Arguments', 'Parameters']:
            dl = dt.parent
            flag = False
            for dl_son in dl:
                if dl_son == dt:
                    flag = True
                if flag and dl_son.name == 'dd':
                    ps = dl_son.find_all('p')
                    for p in ps:
                        if p.find_parent('ul'):
                            continue
                        strong = p.find('strong')
                        if not strong:
                            continue
                        name = strong.text
                        if name not in args_list:
                            continue
                        order = args_list.index(name)
                        description = p.text.strip().replace('\n', '').replace('\t', '')
                        if description.startswith(name):
                            description = description[len(name):]
                        type = ''
                        if '–' in description:
                            type = description.split('–')[0].strip('() ')
                            description = description.split('–')[1].strip()
                        default = args_default.get(name, '')
                        optional = 'optional' in type
                        if optional:
                            type = type.split(', optional')[0]
                        params.append((name, type, optional, default, description.split('.')[0], order))

    for order, arg in enumerate(args_list):
        if arg != '*' and arg not in [i[0] for i in params]:
            default = args_default.get(arg, '')
            params.append((arg, '', bool(default), default, '', order))

    returns = ["", ""]
    for dt in dts:
        if dt.string == 'Returns':
            for dd in dt.find_all_next('dd', limit=1):
                returns[0] = dd.text.strip()
        if dt.string == 'Return type':
            for dd in dt.find_all_next('dd', limit=1):
                returns[1] = dd.text.strip()

    return args_list, params, returns, desc, methodFlag

def getDl(req, path, version, api_num):
    soup = BeautifulSoup(req, 'html.parser')
    for cls in ['function', 'attribute', 'class']:
        for dl in soup.find_all('dl', class_=cls):
            if dl.parent.name == 'dd':
                continue
            api_num += 1
            dt = dl.find('dt')
            if not dt or not dt.has_attr('id'):
                continue
            apiName = dt['id']
            if apiName in specialName:
                apiName = specialName[apiName]
            print(api_num, apiName, cls)
            args_list, params, returns, desc, methodFlag = getInformation(str(dl), cls)
            jsonDumps(apiName, cls, args_list, params, returns, desc, path, version)
            if cls == 'class' and methodFlag:
                api_num = getDL(str(dl), path, version, api_num)
    return api_num

def getDL(req, path, version, api_num):
    soup = BeautifulSoup(req, 'html.parser')
    for dl in soup.find_all('dl', class_='method'):
        api_num += 1
        dt = dl.find('dt')
        if not dt or not dt.has_attr('id'):
            continue
        apiName = dt['id']
        if apiName in specialName:
            apiName = specialName[apiName]
        args_list, params, returns, desc, _ = getInformation(str(dl), 'method')
        print(api_num, apiName, 'method')
        jsonDumps(apiName, 'method', args_list, params, returns, desc, path, version)
    return api_num

def jsonDumps(api, apiType, args_list, params, returns, desc, path, version):
    jsDict = {
        'api': api,
        'type': apiType,
        'version': version,
        'description': desc,
        'args_list': args_list,
        'params': [],
        'returns': {'description': returns[0], 'type': returns[1]}
    }
    for i in params:
        jsDict['params'].append({
            'name': i[0],
            'type': i[1],
            'optional': i[2],
            'default': dealDefault(i[3]),
            'description': dealDefault(i[4]),
            'order': i[5]
        })
    fileName = safe_filename(api) + '.json'
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, fileName), 'w', encoding='utf-8') as f:
        json.dump(jsDict, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    solve(version='stable')

# python src/crawler/PyTorchCrawler.py