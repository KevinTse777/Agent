from pathlib import Path
import os

from dotenv import load_dotenv

# 先加载项目根目录 .env，避免 hello_agents 在 site-packages 中读取不到配置
load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

from hello_agents import SimpleAgent, HelloAgentsLLM, ToolRegistry
from hello_agents.tools import MemoryTool, RAGTool

# 创建LLM实例（使用已验证可用的 DashScope OpenAI 兼容配置）
llm = HelloAgentsLLM(
    model="qwen-plus",
    api_key=os.getenv("EMBED_API_KEY"),
    base_url=os.getenv("EMBED_BASE_URL"),
)

# 创建Agent
agent = SimpleAgent(
    name="智能助手",
    llm=llm,
    system_prompt="你是一个有记忆和知识检索能力的AI助手"
)

# 创建工具注册表
tool_registry = ToolRegistry()

# 添加记忆工具
memory_tool = MemoryTool(user_id="user123")
tool_registry.register_tool(memory_tool)

# 添加RAG工具
rag_tool = RAGTool(knowledge_base_path="./knowledge_base")
tool_registry.register_tool(rag_tool)

# 为Agent配置工具
agent.tool_registry = tool_registry

# 开始对话
response = agent.run("你好！请记住我叫张三，我是一名Python开发者")
print(response)
