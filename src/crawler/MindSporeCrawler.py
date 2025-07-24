import requests
from bs4 import BeautifulSoup
from Tools import getInformation

def solve(root, save_path, version):
    # MindSpore API modules to crawl
    modules = ['mindspore', 'mindspore.ops', 'mindspore.nn', 'mindspore.mint', 
               'mindspore.amp', 'mindspore.train', 'mindspore.dataset.loading',
               'mindspore.dataset.transforms', 'mindspore.numpy', 
               'mindspore.scipy', 'mindspore.experimental',
               'mindspore.ops.primitive', 'mindspore.nn.probability',
               'mindspore.hal']
    modules = [
               'mindspore.ops.primitive', 'mindspore.nn.probability',
               'mindspore.hal']
    # modules = []
    # Direct API modules
    direct_api = ['mindspore', 'mindspore.common.initializer', 'mindspore.parallel', 
                  'mindspore.runtime', 'mindspore.device_context', 
                  'mindspore.communication', 'mindspore.mindrecord', 'mindspore.utils', 
                  'mindspore.boost', 'mindspore.rewrite']     
    # direct_api = ['mindspore.mindrecord']
    api_num = 0
    for i in modules:
        url = root + i + '.html'
        r = requests.get(url)
        links = getRef(root, r.text)
        for link in links:   
            path = save_path + i + '/'
            api_num = getInformation(link, api_num, version, path)
            
    for i in direct_api:
        link = root + i + '.html'
        path = save_path + i + '/'
        api_num = getInformation(link, api_num, version, path)
        

def getRef(root, req):
    soup = BeautifulSoup(req, 'html.parser')
    codes = soup.find_all(class_='xref py py-obj docutils literal notranslate')
    link = []
    for code in codes:
        a = code.parent
        # a 不一定有herf
        if not a.has_attr('href'):
            continue
        if root + a['href'] not in link:
            link.append(root + a['href'])
    return link


if __name__ == '__main__':
    version = 'master'
    root = "https://www.mindspore.cn/docs/en/" + version + "/api_python/"
    save_path = "dao/node/MindSpore/" + version + "/"
    solve(root, save_path, version) 

"""
python src/crawler/MindSporeCrawler.py
"""