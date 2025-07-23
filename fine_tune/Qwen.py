# 调用 qwen 大模型，
# 观察用qwen大模型提取算子间关系的效果

import os
import json

def get_all_json_files(root):
    json_files = []
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            if fname.endswith('.json'):
                json_files.append(os.path.join(dirpath, fname))
    return json_files

def json_to_multiline_str(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2)

# 1. 处理映射关系
with open('../../dao/relation/PyTorch2PaddlePaddle/train.json', 'r', encoding='utf-8') as f:
    train_data = json.load(f)['relationship']

with open('qwen_sft.jsonl', 'w', encoding='utf-8') as f_out:
    for item in train_data:
        input_text = json_to_multiline_str(item)
        output_text = item.get('opRelation', '')
        f_out.write(json.dumps({"input": input_text, "output": output_text}, ensure_ascii=False) + '\n')

    # 2. 处理 PaddlePaddle 和 PyTorch 算子信息
    paddle_files = get_all_json_files('../../dao/node/PaddlePaddle/')
    pytorch_files = get_all_json_files('../../dao/node/PyTorch/')
    for file in paddle_files + pytorch_files:
        with open(file, 'r', encoding='utf-8') as jf:
            data = json.load(jf)
        input_text = json_to_multiline_str(data)
        output_text = ''
        f_out.write(json.dumps({"input": input_text, "output": output_text}, ensure_ascii=False) + '\n')

# python Qwen.py