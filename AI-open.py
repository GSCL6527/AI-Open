"""
©2025 GS Group All Rights Reserved.
www.gscl.com.mp
www.652789.xyz

v0.1版本更新日志：第一个版本，实现了基本的命令生成和执行功能。
v0.2版本更新日志：优化了代码，修复了命令无法执行的问题。
v0.3版本更新日志：修复了AI大模型输出的不是可执行文件名称导致被拦截从而无法正确执行的问题。
v0.4版本更新日志：修复了AI大模型输出的可执行文件名称带有.exe导致被误拦截从而无法正确执行的问题。
"""
import requests
import subprocess
import re
import time
import logging

# 增强配置项
class SecurityConfig:
    OLLAMA_URL = "http://127.0.0.1:11434"
    MODEL_NAME = "deepseek-r1:14b"
    ALLOWED_COMMANDS = {'mspaint', 'notepad', 'calc', 'explorer'}  # 命令白名单
    COMMAND_PATTERN = re.compile(r"^[a-zA-Z0-9_\-.\\/: ]+$")  # 安全命令正则
    THINKING_KEYWORDS = re.compile(r'(思考|可能|因为|所以|建议|方案|步骤)', re.IGNORECASE)

# 初始化日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('command_executor.log'),
        logging.StreamHandler()
    ]
)

def generate_command(prompt: str) -> str:
    """优化后的命令生成函数"""
    enhanced_prompt = (
        "请严格按以下要求响应：\n"
        "1. 直接输出唯一的Windows系统命令\n"
        "2. 不要包含任何思考过程\n"
        "3. 不要解释命令作用\n"
        "4. 输出唯一的Windows可执行程序名\n"
        "5. 使用标准系统命令（如画图=mspaint）\n"
        "6. 禁用缩写和别名（如不要用paint代替mspaint）\n"
        "7. 示例格式：mspaint\n\n"
        f"用户指令：{prompt}"
    )

    try:
        response = requests.post(
            f"{SecurityConfig.OLLAMA_URL}/api/generate",
            json={
                "model": SecurityConfig.MODEL_NAME,
                "prompt": enhanced_prompt,
                "stream": False
            },
            timeout=30
        )
        response.raise_for_status()
        return sanitize_output(response.json()["response"])
    except Exception as e:
        logging.error(f"API请求失败: {str(e)}")
        return ""


def sanitize_output(raw_output: str) -> str:
    """增强型输出净化"""
    valid_commands = []
    for line in raw_output.split('\n'):
        line = line.strip()

        # 新增处理：统一去除.exe后缀
        if line.lower().endswith('.exe'):
            line = line[:-4]

        # 过滤空行和注释
        if not line or line.startswith(('#', '//')):
            continue

        # 排除包含思考关键词的行
        if SecurityConfig.THINKING_KEYWORDS.search(line):
            continue

        # 基础格式验证
        if SecurityConfig.COMMAND_PATTERN.match(line):
            valid_commands.append(line)

    # 优先选择最后一行有效命令（通常为最终结论）
    return valid_commands[-1] if valid_commands else ""


def validate_command(cmd: str) -> bool:
    """双重安全验证（增加后缀兼容）"""
    # 统一转换为小写比较
    normalized_cmd = cmd.lower().replace('.exe', '')
    return (
            normalized_cmd in {c.lower() for c in SecurityConfig.ALLOWED_COMMANDS} and
            SecurityConfig.COMMAND_PATTERN.match(cmd) is not None
    )

def execute_command(cmd: str):
    """带日志记录的执行函数"""
    try:
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        logging.info(f"执行成功: {cmd} (PID: {process.pid})")
        print(f"已执行命令: {cmd}")
    except Exception as e:
        logging.error(f"执行失败: {cmd} - {str(e)}")
        print(f"命令执行失败: {str(e)}")

def main():
    print("内部版本，仅供测试使用，请勿用于非法用途！")
    print("作者：GS\n\n调试\nDebugging\n")
    print("支持的命令示例：画图/记事本/计算器/文件管理器")
    print("指令转换程序已启动（输入'退出'结束）")

    while True:
        user_input = input("\n请输入指令：").strip()
        if user_input.lower() in ["退出", "exit"]:
            print("程序已退出")
            break
        if not user_input:
            continue

        logging.info(f"收到指令: {user_input}")
        print("正在生成命令...")
        start_time = time.time()

        raw_command = generate_command(user_input)
        process_time = time.time() - start_time

        print(f"生成耗时: {process_time:.2f}秒")

        if not raw_command:
            print("未获取到有效命令")
            continue

        if validate_command(raw_command):
            execute_command(raw_command)
        else:
            print(f"安全拦截: 可疑指令 '{raw_command}'")
            logging.warning(f"拦截可疑命令: {raw_command}")

if __name__ == "__main__":
    main()