import ast
import inspect
import os
import re
from string import Template
from typing import List, Callable, Tuple

import click
import platform
from dotenv import load_dotenv
from openai import OpenAI

from react_system_prompt_template import system_prompt_template


class ReActAgent:
    def __init__(self, base_url: str, model: str, tools: List[Callable], project_directory: str):
        self.model = model
        self.tools = {func.__name__: func for func in tools}
        self.project_directory = project_directory
        self.client = OpenAI(
            base_url=base_url,
            api_key=ReActAgent.get_api_key(),
        )

    def run(self, user_input: str):
        messages = [
            {"role": "system", "content": self.render_system_prompt(system_prompt_template)},
            {"role": "user", "content": f"<question>{user_input}</question>"}
        ]

        # ReAct范式核心逻辑！！！
        while True:
            # 请求模型；
            content = self.call_model(messages)

            # 检测 Thought；
            thought_match = re.search(r"<thought>(.*?)</thought>", content, re.DOTALL)
            if thought_match:
                thought = thought_match.group(1)
                print(f"\n\n💡 Thought: {thought}")

            # 检测模型是否输出 Final Answer，如果是的话，直接返回；
            if "<final_answer>" in content:
                final_answer = re.search(r"<final_answer>(.*?)</final_answer>", content, re.DOTALL)
                return final_answer.group(1)

            # 检测 Action；
            action_match = re.search(r"<action>(.*?)</action>", content, re.DOTALL)
            if not action_match:
                raise RuntimeError("未检测到Final Answer，同时未检测到Action...")
            action = action_match.group(1)
            tool_name, args = self.parse_action(action)

            print(f"\n\n⚙️ Action: {tool_name}({', '.join(args)})")
            # 只有终端命令才需要询问用户，其他的工具直接执行；
            should_continue = input(f"\n\n是否继续？（y/n）") if tool_name == "run_terminal_command" else "y"
            if should_continue.lower() != 'y':
                return "操作被用户取消"

            try:
                observation = self.tools[tool_name](*args)
            except Exception as e:
                observation = f"工具执行错误：{str(e)}"
            print(f"\n\n🌏 Observation：{observation}")
            obs_msg = f"<observation>{observation}</observation>"
            messages.append({"role": "user", "content": obs_msg})

    def call_model(self, messages):
        print("\n\n🚀 正在请求模型，请稍等...")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        content = response.choices[0].message.content
        messages.append({"role": "assistant", "content": content})
        return content

    def get_tool_list(self) -> str:
        """生成工具列表字符串，包含函数签名和简要说明"""
        tool_descriptions = []
        for func in self.tools.values():
            name = func.__name__
            signature = str(inspect.signature(func))
            doc = inspect.getdoc(func)
            tool_descriptions.append(f"- {name}{signature}: {doc}")
        return "\n".join(tool_descriptions)

    def render_system_prompt(self, template: str) -> str:
        """渲染系统提示模板，替换变量"""
        tool_list = self.get_tool_list()

        file_list = ", ".join(
            os.path.abspath(os.path.join(self.project_directory, f))
            for f in os.listdir(self.project_directory)
        )
        if "" == file_list.strip():
            file_list = "空"

        return Template(template).substitute(
            tool_list=tool_list,
            operating_system=self.get_operating_system_name(),
            project_directory=self.project_directory,
            file_list=file_list
        )

    @staticmethod
    def get_api_key() -> str:
        """Load the API key from an environment variable."""
        load_dotenv()
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("未找到 OPENROUTER_API_KEY 环境变量，请在 .env 文件中设置。")
        return api_key

    @staticmethod
    def fix_multiline_string(code_str: str) -> str:
        if '"""' in code_str or "'''" in code_str:
            return code_str

        # 粗暴策略：检测是否有多行但只用单引号
        lines = code_str.split("\n")
        if len(lines) > 1:
            first_quote = code_str.find('"')
            if first_quote != -1:
                return code_str.replace('"', '"""', 1).rstrip() + '"""'

        return code_str

    def parse_action(self, code_str: str) -> Tuple[str, List[str]]:
        match = re.match(r'(\w+)\((.*)\)', code_str, re.DOTALL)
        if not match:
            raise ValueError("Invalid function call syntax.")

        func_name = match.group(1)
        args_str = match.group(2).strip()

        # 手动解析参数，特别处理包含多行内容的字符串;
        args = []
        current_arg = ""
        in_string = False
        string_char = None
        i = 0
        paren_depth = 0

        while i < len(args_str):
            char = args_str[i]

            if not in_string:
                if char in ['"', "'"]:
                    in_string = True
                    string_char = char
                    current_arg += char
                elif char == '(':
                    paren_depth += 1
                    current_arg += char
                elif char == ')':
                    paren_depth -= 1
                    current_arg += char
                elif char == ',' and paren_depth == 0:
                    # 遇到顶层逗号，结束当前参数;
                    args.append(self._parse_single_arg(current_arg.strip()))
                    current_arg = ""
                else:
                    current_arg += char
            else:
                current_arg += char
                if char == string_char and (i == 0 or args_str[i - 1] != '\\'):
                    in_string = False
                    string_char = None

            i += 1

        # 添加最后一个参数;
        if current_arg.strip():
            args.append(self._parse_single_arg(current_arg.strip()))

        return func_name, args

    @staticmethod
    def _parse_single_arg(arg_str: str):
        """解析单个参数"""
        arg_str = arg_str.strip()

        # 如果是字符串字面量;
        if (arg_str.startswith('"') and arg_str.endswith('"')) or \
                (arg_str.startswith("'") and arg_str.endswith("'")):
            # 移除外层引号并处理转义字符;
            inner_str = arg_str[1:-1]
            # 处理常见的转义字符;
            inner_str = inner_str.replace('\\"', '"').replace("\\'", "'")
            inner_str = inner_str.replace('\\n', '\n').replace('\\t', '\t')
            inner_str = inner_str.replace('\\r', '\r').replace('\\\\', '\\')
            return inner_str

        # 尝试使用 ast.literal_eval 解析其他类型;
        try:
            return ast.literal_eval(arg_str)
        except (SyntaxError, ValueError):
            # 如果解析失败，返回原始字符串;
            return arg_str

    @staticmethod
    def get_operating_system_name():
        os_map = {
            "Darwin": "macOS",
            "Windows": "Windows",
            "Linux": "Linux"
        }
        return os_map.get(platform.system(), "Unknown")


def read_file(file_path):
    """用于读取文件内容"""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def write_to_file(file_path, content):
    """将指定内容写入指定文件"""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content.replace("\\n", "\n"))
    return "写入成功"


def run_terminal_command(command) -> dict:
    """用于执行终端命令"""
    import subprocess
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=10)

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        # 输出截断（防止 context 爆炸）
        MAX_LEN = 2000
        if len(stdout) > MAX_LEN:
            stdout = stdout[:MAX_LEN] + "...(truncated)"
        if len(stderr) > MAX_LEN:
            stderr = stderr[:MAX_LEN] + "...(truncated)"

        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": stdout,
            "stderr": stderr,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Command run timeout."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@click.command()
@click.argument('project_directory',
                type=click.Path(exists=True, file_okay=False, dir_okay=True))
def main(project_directory):
    project_dir = os.path.abspath(project_directory)

    base_url = "https://openrouter.ai/api/v1"
    model = "deepseek/deepseek-v3.2"
    tools = [read_file, write_to_file, run_terminal_command]
    agent = ReActAgent(base_url=base_url, model=model, tools=tools, project_directory=project_dir)

    task = input("请输入任务：")
    final_answer = agent.run(task)

    print(f"\n\n✅ Final Answer：{final_answer}")


if __name__ == "__main__":
    main()