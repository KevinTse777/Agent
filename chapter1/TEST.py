import os
api_key = os.getenv("DASHSCOPE_API_KEY", "")

print(f"密钥长度: {len(api_key)}")  # 应该是 51 或 56 位左右
print(f"前缀检查: {api_key[:7]}...")  # 应该以 sk- 开头
print(f"是否包含空格: {' ' in api_key}")  # 应该是 False