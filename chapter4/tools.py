from dotenv import load_dotenv
# 加载 .env 文件中的环境变量
load_dotenv()

import os
import ast
import operator
from typing import Dict, Any

def search(query: str) -> str:
    """
    一个基于SerpApi的实战网页搜索引擎工具。
    它会智能地解析搜索结果，优先返回直接答案或知识图谱信息。
    """
    print(f"🔍 正在执行 [SerpApi] 网页搜索: {query}")
    try:
        try:
            from serpapi import SerpApiClient
        except ModuleNotFoundError:
            return "错误：未安装 serpapi 依赖，无法使用 Search 工具。"

        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            return "错误：SERPAPI_API_KEY 未在 .env 文件中配置。"

        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "gl": "cn",  # 国家代码
            "hl": "zh-cn", # 语言代码
        }
        
        client = SerpApiClient(params)
        results = client.get_dict()
        
        # 智能解析：优先寻找最直接的答案
        if "answer_box_list" in results:
            return "\n".join(results["answer_box_list"])
        if "answer_box" in results and "answer" in results["answer_box"]:
            return results["answer_box"]["answer"]
        if "knowledge_graph" in results and "description" in results["knowledge_graph"]:
            return results["knowledge_graph"]["description"]
        if "organic_results" in results and results["organic_results"]:
            # 如果没有直接答案，则返回前三个有机结果的摘要
            snippets = [
                f"[{i+1}] {res.get('title', '')}\n{res.get('snippet', '')}"
                for i, res in enumerate(results["organic_results"][:3])
            ]
            return "\n\n".join(snippets)
        
        return f"对不起，没有找到关于 '{query}' 的信息。"

    except Exception as e:
        return f"搜索时发生错误: {e}"


def calculator(expression: str) -> str:
    """
    一个安全的数学计算工具，支持 +, -, *, /, //, %, ** 和括号。
    输入示例: (123 + 456) * 789 / 12
    """
    print(f"🧮 正在执行 [Calculator] 计算: {expression}")

    if not expression or not expression.strip():
        return "错误：计算器输入为空，请提供一个数学表达式。"

    expr = expression.strip().replace("×", "*").replace("÷", "/")
    if len(expr) > 200:
        return "错误：表达式过长，请简化后再试。"

    allowed_bin_ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }
    allowed_unary_ops = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Num):  # 兼容旧版本 Python AST
            return node.n
        if isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            op_type = type(node.op)
            if op_type not in allowed_bin_ops:
                raise ValueError("包含不支持的二元运算符。")
            if op_type is ast.Pow and abs(right) > 12:
                raise ValueError("幂运算指数过大，已拒绝执行。")
            return allowed_bin_ops[op_type](left, right)
        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in allowed_unary_ops:
                raise ValueError("包含不支持的一元运算符。")
            return allowed_unary_ops[op_type](_eval(node.operand))
        raise ValueError("表达式包含不支持的语法。")

    try:
        tree = ast.parse(expr, mode="eval")
        value = _eval(tree)
        return f"结果：{value}"
    except ZeroDivisionError:
        return "错误：除数不能为 0。"
    except SyntaxError:
        return "错误：表达式语法错误，请检查括号和运算符。"
    except Exception as e:
        return f"错误：无法计算该表达式（{e}）。"
    
class ToolExecutor:
    """
    一个工具执行器，负责管理和执行工具。
    """
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def registerTool(self, name: str, description: str, func: callable):
        """
        向工具箱中注册一个新工具。
        """
        if name in self.tools:
            print(f"警告：工具 '{name}' 已存在，将被覆盖。")
        
        self.tools[name] = {"description": description, "func": func}
        print(f"工具 '{name}' 已注册。")

    def getTool(self, name: str) -> callable:
        """
        根据名称获取一个工具的执行函数。
        """
        return self.tools.get(name, {}).get("func")

    def getAvailableTools(self) -> str:
        """
        获取所有可用工具的格式化描述字符串。
        """
        return "\n".join([
            f"- {name}: {info['description']}" 
            for name, info in self.tools.items()
        ])

    def listToolNames(self) -> list[str]:
        """
        返回当前已注册的工具名称列表。
        """
        return list(self.tools.keys())
