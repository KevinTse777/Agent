import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# 1. 改为你的本地路径（根据实际下载位置修改）
model_path = "/Users/tse/.ollama/models/manifests/registry.ollama.ai/library/qwen2.5"
# model_path = "/Users/你的用户名/models/Qwen2.5-3B-Instruct"  # Mac 绝对路径示例

# 2. M5 Mac 专用设备检测（Metal Performance Shaders）
if torch.backends.mps.is_available():
    device = "mps"
    print("Using Apple Silicon GPU (MPS)")
elif torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"
print(f"Device: {device}")

# 3. 加载分词器（强制本地）
tokenizer = AutoTokenizer.from_pretrained(
    model_path, 
    local_files_only=True,  # 关键：禁止联网下载
    trust_remote_code=True  # Qwen 系列需要
)

# 4. 加载模型（针对 16GB Mac 优化）
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    local_files_only=True,      # 关键：禁止联网
    trust_remote_code=True,     # Qwen 系列需要
    torch_dtype=torch.float16,  # 半精度：内存减半，速度提升，M5 完美支持
    # device_map="auto",        # 自动分配层到设备（推荐）
    # 或者明确指定：
    low_cpu_mem_usage=True      # 减少 CPU 内存峰值（对大模型很重要）
).to(device)

print("模型加载完成！")

# 5. 使用部分（与你原代码基本一致，但注意输入也要 to device）
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "你好，请介绍你自己。"}
]

text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)

# 输入数据也要放到 M5 GPU 上
model_inputs = tokenizer([text], return_tensors="pt").to(device)

# 生成（M5 上生成速度约 10-20 tokens/秒 for 3B）
generated_ids = model.generate(
    model_inputs.input_ids,
    max_new_tokens=512,
    do_sample=True,          # 启用采样（更自然）
    temperature=0.7,
    top_p=0.9
)

# 解码输出（保持与你原代码一致）
generated_ids = [
    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
]
response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

print("\n模型的回答:")
print(response)