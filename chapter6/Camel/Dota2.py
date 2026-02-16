from colorama import Fore
from camel.societies import RolePlaying
from camel.utils import print_text_animated
from camel.models import ModelFactory
from camel.types import ModelPlatformType
from dotenv import load_dotenv
import os

load_dotenv()
LLM_API_KEY = os.getenv("MINIMAX_API_KEY")
LLM_BASE_URL = os.getenv("MINIMAX_BASE_URL")
LLM_MODEL = os.getenv("MINIMAX_MODEL_ID")

model_config_dict = {
    "max_tokens": 10000,  # 设置最大token数
    "temperature": 0.7,
}
# 创建模型
model = ModelFactory.create(
    model_platform=ModelPlatformType.QWEN,
    model_type=LLM_MODEL,
    url=LLM_BASE_URL,
    api_key=LLM_API_KEY,
    model_config_dict=model_config_dict
)

# 定义协作任务
task_prompt = """
创作一本关于"如何成为少女乐队爱好者"的短篇电子书，目标读者是对二次元的普通大众。
要求：
1. 内容科学严谨，基于实证研究
2. 语言通俗易懂，避免过多专业术语
3. 包含实用的改善建议和案例分析
4. 篇幅控制在8000-10000字
5. 结构清晰，包含引言、核心章节和总结
"""

print(Fore.YELLOW + f"协作任务:\n{task_prompt}\n")

# 初始化角色扮演会话
role_play_session = RolePlaying(
    assistant_role_name="日本宅男", 
    user_role_name="二次元研究员", 
    task_prompt=task_prompt,
    model=model
)

print(Fore.CYAN + f"具体任务描述:\n{role_play_session.task_prompt}\n")

# 用于存储所有对话内容的列表
book_content = []
book_content.append("=" * 50)
book_content.append("成为日本少女乐队爱好者")
book_content.append("=" * 50)
book_content.append(f"\n任务描述：\n{task_prompt}\n")
book_content.append("=" * 50)
book_content.append("\n")

# 开始协作对话
chat_turn_limit, n = 5, 0
input_msg = role_play_session.init_chat()

while n < chat_turn_limit:
    n += 1
    assistant_response, user_response = role_play_session.step(input_msg)
    
    # 获取当前轮次的内容
    writer_content = user_response.msg.content
    ame_content = assistant_response.msg.content
    
    # 控制台输出（保持原有动画效果）
    print_text_animated(Fore.BLUE + f"二次元研究员:\n\n{writer_content}\n")
    print_text_animated(Fore.GREEN + f"日本宅男:\n\n{ame_content}\n")
    
    # 保存到内容列表（去掉颜色代码，纯文本保存）
    book_content.append(f"\n{'='*50}")
    book_content.append(f"第 {n} 轮对话")
    book_content.append(f"{'='*50}\n")
    book_content.append(f"【二次元研究员】\n{writer_content}\n")
    book_content.append(f"【日本宅男】\n{ame_content}\n")
    
    # 检查任务完成标志
    if "CAMEL_TASK_DONE" in writer_content:
        print(Fore.MAGENTA + "✅ 电子书创作完成！")
        break
    
    input_msg = assistant_response.msg

print(Fore.YELLOW + f"总共进行了 {n} 轮协作对话")

# 保存到文件
filename = "成为日本少女乐队.txt"
try:
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(book_content))
    print(Fore.GREEN + f"✅ 文件已保存至: {os.path.abspath(filename)}")
except Exception as e:
    print(Fore.RED + f"❌ 保存文件时出错: {e}")