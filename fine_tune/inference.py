import json
import torch
import os
from transformers import AutoModelForCausalLM, AutoTokenizer

def json_to_multiline_str(obj):
    """将json对象转换为多行字符串"""
    return json.dumps(obj, ensure_ascii=False, indent=2)

def load_finetuned_model(model_path):
    """加载微调后的模型"""
    try:
        model = AutoModelForCausalLM.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        return model, tokenizer
    except Exception as e:
        print(f"模型加载失败: {e}")
        return None, None

def inference_on_test_set(model, tokenizer, test_data):
    """对测试集进行推理"""
    results = []
    
    for i, item in enumerate(test_data):
        print(f"推理进度: {i+1}/{len(test_data)}")
        
        # 构造输入（与训练时相同的格式）
        input_text = json_to_multiline_str(item)
        
        # 编码输入
        inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=1024)
        
        # 生成输出
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=100,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # 解码输出
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # 提取生成的映射关系
        predicted_relation = generated_text.replace(input_text, "").strip()
        if predicted_relation.startswith("映射关系:"):
            predicted_relation = predicted_relation[5:].strip()
        
        results.append({
            "PyTorch": item.get('PyTorch', ''),
            "PaddlePaddle": item.get('PaddlePaddle', ''),
            "true_relation": item.get('opRelation', ''),
            "predicted_relation": predicted_relation,
            "full_output": generated_text
        })
    
    return results

def main():
    # 配置路径
    model_path = "./qwen_sft_ckpt"  # 修改为你的模型路径
    test_file = "../../dao/relation/PyTorch2PaddlePaddle/test.json"
    output_file = "test_inference_results.json"
    
    print("开始加载测试集...")
    # 加载测试集
    with open(test_file, 'r', encoding='utf-8') as f:
        test_data = json.load(f)['relationship']
    print(f"测试集大小: {len(test_data)}")
    
    print("开始加载微调模型...")
    # 加载微调模型
    model, tokenizer = load_finetuned_model(model_path)
    
    if model and tokenizer:
        print("模型加载成功，开始推理...")
        results = inference_on_test_set(model, tokenizer, test_data)
        
        # 保存推理结果
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # 计算准确率
        correct = 0
        for result in results:
            if result['true_relation'] == result['predicted_relation']:
                correct += 1
        
        accuracy = correct / len(results)
        print(f"\n推理完成！")
        print(f"准确率: {accuracy:.4f} ({correct}/{len(results)})")
        print(f"结果已保存到 {output_file}")
        
        # 显示一些示例结果
        print("\n示例结果:")
        for i, result in enumerate(results[:3]):
            print(f"样本 {i+1}:")
            print(f"  PyTorch: {result['PyTorch']}")
            print(f"  PaddlePaddle: {result['PaddlePaddle']}")
            print(f"  真实关系: {result['true_relation']}")
            print(f"  预测关系: {result['predicted_relation']}")
            print(f"  是否正确: {'✓' if result['true_relation'] == result['predicted_relation'] else '✗'}")
            print()
            
    else:
        print("模型加载失败，请检查模型路径和依赖")

if __name__ == "__main__":
    main() 