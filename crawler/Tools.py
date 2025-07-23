from bs4 import BeautifulSoup
import requests
import os
import json

def dealDefault(default):
    default = default.replace("mstype", "mindspore")
    i = default.strip()
    if len(i) == 0:
        i = ""
    else:
        i = i.replace("\"", "")
        i = i.replace("\'", "")
        i = i.replace("'", "")
        i = i.replace("'", "")
        i = i.replace("'", "")
        i = i.replace("'", "")
    return i

def print_hit(hit):
    print('------\n' + hit)

def isWord(string):
    if string.find(' ') == -1 and string.find('-') == -1:
        return True
    else:
        return False
    
def get_args(dt):
    # get args_list and default value
    args_list = []
    args_default = {}
    args = ""
    em_elements = dt.find_all('em', {'class': 'sig-param'})
    for em in em_elements:
        spans = em.find_all('span', {'class': 'pre'})
        for span in spans:
            args += span.text
        args += ","
    args_list = args.split(',')
    args_list = args_list[:-1]
    for i in range(len(args_list)):
        if '=' in args_list[i]:
            key = args_list[i].split('=')[0]
            value = args_list[i].split('=')[1]
            args_default[key] = value
            args_list[i] = key 
    return args_list, args_default

def solve_raise(Raises, dd):
    ul = dd.find('ul', {'class': 'simple'})
    if not ul:
        Raises.append((get_raise(dd)))
        return Raises
    else:
        lis = ul.find_all('li')
        raiseDesc = ''
        if lis[0].find('p').find('strong'):
            for li in lis:
                ul_without_simple = li.find('ul')
                if not ul_without_simple:
                    Raises.append((get_raise(dd)))
                else:
                    lis_under_ul = ul_without_simple.find_all('li')
                    raiseType = li.find('p').find('strong').text
                    for li_under_ul in lis_under_ul:
                        raiseDesc += li_under_ul.find('p').text.replace('\n', ' ').replace('\t', ' ').replace('\\', '').strip() + ' '
                    Raises.append((raiseType, raiseDesc))  
            return Raises
        else:
            raiseType = dd.find('p').find('strong').text
            for li in lis:
                raiseDesc += li.find('p').text.replace('\n', ' ').replace('\t', ' ').replace('\\', '').strip() + ' '
            Raises.append((raiseType, raiseDesc))
            return Raises    

def get_raise(dd):
    raiseType = dd.find('p').find('strong').text
    raiseDesc = dd.find('p').text
    if '–' in raiseDesc:
        raiseDesc = raiseDesc.split('–')[1]          
    raiseDesc = raiseDesc.replace('\n', ' ').replace('\t', ' ').replace('\\', '').strip()
    return raiseType, raiseDesc
def solve_platform(Supported_Platforms, dd):
    spans = dd.find_all('span')
    for span in spans:
        Supported_Platforms.append(span.text.strip())
    return Supported_Platforms

def getInformation(link, apinum, version, path):
    print_hit(link)
    r = requests.get(link)
    soup = BeautifulSoup(r.text, 'html.parser')
    dls = soup.find_all('dl')
    for dl_operator in dls:
        if 'py' not in dl_operator['class']:
            continue
        apinum += 1
        apitype = dl_operator['class'][1]
        dt_operator = dl_operator.find('dt')
        if 'id' not in dt_operator.attrs:
            continue
        apiName = dt_operator['id']
        if 'mindspore.communication.mindspore' in apiName:
            apiName = apiName.replace('mindspore.communication.mindspore', 'mindspore')
        print(apinum, apiName, apitype)
        args_list, args_default = get_args(dt_operator)
        desc = ''
        dd_operator = dl_operator.find('dd')
        if dd_operator.find('p'):
            desc = dd_operator.find('p').text.split('.')[0].replace('\t', ' ').replace("\n", " ").replace(";", ",").replace('"', "").replace("\\", " ").strip() + '.'
        Parameters = []
        Returns = []
        Raises = []
        Supported_Platforms = []
        dl_fields = dd_operator.find_all('dl') 
        index = 0
        flag = False
        for i in range(len(dl_fields)):
            if 'py' in dl_fields[i]['class']:
                index = i
                flag = True
                break
        if flag:
            dl_fields = dl_fields[:index]
        for dl_field in dl_fields:    
            dts = dl_field.find_all('dt')                
            for dt in dts:              
                dd = dt.find_next_sibling('dd')
                ps = dd.find_all('p')
                if dt.string == 'Parameters':
                    Parameters = solve_params(Parameters, ps, args_list, args_default)
                if dt.string == 'Returns':
                    Returns = solve_return(Returns, dd)
                if dt.string and 'Example' in dt.string:
                    continue
                if dt.string == 'Raises':
                    Raises = solve_raise(Raises, dd)
                if dt.string == 'Supported Platforms:':
                    Supported_Platforms = solve_platform(Supported_Platforms, dd)
        jsonDumps(apiName, apitype, desc, version, path, Parameters, Returns, Supported_Platforms, Raises, args_list)
    return apinum
    
def solve_params(Parameters, ps, args_list, args_default):
    for p in ps:
        strong = p.find('strong')
        if strong:
            name = strong.text
            if name in args_list:
                order = args_list.index(name)
            else:
                order = ps.index(p)
        if not strong:
            continue
        # get description, optional and type of the parameter
        description = p.text.replace('\n', ' ').replace('\t', ' ').replace('"', '').split('. ')[0].replace(';', '.').replace('\\(', '').replace('\\)', '').replace('\\', '').strip()
        type = ''
        if description.startswith(name):
            description = description[len(name):]
            if '–' in description:
                type = description.split('–')[0].replace(')', '').replace('(', '').strip()
                description = description.split('–')[1].strip()
        optional = False
        if 'optional' in type or 'Optional' in type:
            optional = True
            type = type.replace(', optional', '').replace(', Optional', '').strip()         
        # get the default 
        default = ''        
        if name in list(args_default.keys()):
            default = args_default[name]
        Parameters.append((name, type, optional, default, description, order))
    return Parameters

def solve_return(Returns, dd):    
    Returns = dd.text.replace('\n', ' ').replace('\t', ' ').replace('"', '').split('. ')[0].replace(';', '.').replace('\\(', '').replace('\\)', '').strip() + '.'
    return Returns

def jsonDumps(apiName, apitype, desc, version, path, Parameters, Returns, Supported_Platforms, Raises, args_list):
    jsDict = {}
    jsDict['api'] = apiName
    jsDict['type'] = apitype
    jsDict['version'] = version
    jsDict['description'] = desc
    jsDict['args_list'] = args_list
    myParams = []
    for i in Parameters:
        temp = {}
        temp['name'] = i[0]
        temp['type'] = i[1]
        temp['optional'] = i[2]
        temp['default'] = dealDefault(i[3])
        temp['description'] = dealDefault(i[4])
        temp['order'] = i[5]
        myParams.append(temp)  
    jsDict['Parameters'] = myParams
    jsDict['Returns'] = Returns
    jsDict['Supported_Platforms'] = Supported_Platforms
    apiRaises = []
    for i in Raises:
        temp = {}
        temp['type'] = i[0]
        temp['description'] = dealDefault(i[1])
        apiRaises.append(temp)
    jsDict['Raises'] = apiRaises
    fileName = apiName + '.json'
    filePath = path + fileName
    if os.path.exists(filePath):
        filePath = filePath.replace(".json", "_2.json")
    if not os.path.exists(path):
        os.makedirs(path)
    with open(filePath, 'w', encoding='utf-8') as f:
        json.dump(jsDict, f, ensure_ascii=False, indent=4, default=str)
        f.close()

def Empty(path, apiName):
    file_dir = os.path.dirname(path)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)  # 创建目录
    with open(path, 'a') as f:
        f.write(apiName + '\n')
