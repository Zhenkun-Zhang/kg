import json
import random

# 读取原始映射表
with open('dao/relation/PyTorch2PaddlePaddle/relationship_stable--3.0-beta.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

relationships = data['relationship']
random.shuffle(relationships)  # 打乱顺序

# 8:2 划分
split_idx = int(len(relationships) * 0.8)
train_set = relationships[:split_idx]
test_set = relationships[split_idx:]

# 保存训练集
with open('dao/relation/PyTorch2PaddlePaddle/train.json', 'w', encoding='utf-8') as f:
    json.dump({'relationship': train_set}, f, ensure_ascii=False, indent=2)

# 保存测试集
with open('dao/relation/PyTorch2PaddlePaddle/test.json', 'w', encoding='utf-8') as f:
    json.dump({'relationship': test_set}, f, ensure_ascii=False, indent=2)

print(f"训练集数量: {len(train_set)}, 测试集数量: {len(test_set)}")

# python src/fine_tune/pre.py