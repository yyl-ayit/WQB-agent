#!/usr/bin/env python3
"""
同步无限循环：
alpha_agent 产出的 alpha 交给 termination_checker，
termination_checker 的结果再作为下一轮 alpha_agent 的输入，
周而复始，直到 Ctrl+C。
"""

import json
import logging
import os
import signal
import sys
from datetime import datetime
from API_agent import chat_angent
from google.adk.runners import InMemoryRunner

# -------------------------------------------------
# 假设两个 Agent 写在 agents.py
# -------------------------------------------------
from agent import alpha_agent, termination_checker


def ask(question: str):
    """同步调用一次 react_agent 并返回结果"""
    runner = InMemoryRunner(agent=alpha_agent)
    resp = runner.run(question)  # 同步方法
    return resp
# -------------------------------------------------
# 日志
# -------------------------------------------------
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(
            f"{LOG_DIR}/sync_loop_{datetime.now():%Y%m%d_%H%M%S}.log",
            encoding="utf-8"
        ),
        logging.StreamHandler(sys.stdout)
    ]
)

# -------------------------------------------------
# 优雅退出
# -------------------------------------------------
STOP = False
def _sig_handler(signum, frame):
    global STOP
    logging.warning("收到终止信号，准备退出……")
    STOP = True
signal.signal(signal.SIGINT, _sig_handler)

# -------------------------------------------------
# 下一轮提示模板
# -------------------------------------------------
NEXT_PROMPT_TEMPLATE = """
上一轮终止检查器给出的分析结果如下：
{checker_result}

请在此基础上改进或生成全新的 alpha 表达式，并**仅返回**可直接测评的 JSON。
"""

# -------------------------------------------------
# 主循环
# -------------------------------------------------
def main():
    logging.info("同步无限循环启动，按 Ctrl+C 结束")
    round_id = 0
    # 第一轮让 alpha_agent 自由发挥
    next_prompt = "请生成一个可直接测评的并且高质量的 alpha 表达式，仅返回 JSON"

    while not STOP:
        round_id += 1
        logging.info("===== 第 %d 轮开始 =====", round_id)

        result = chat_angent(next_prompt)

        print(result)
        # ==============================
        alpha_json_str = result
        try:
            alpha_json = json.loads(alpha_json_str)
        except Exception as e:
            logging.error("alpha_agent 返回的不是合法 JSON：%s", result[:300])
            continue
        logging.info("alpha_agent 产出：%s", json.dumps(alpha_json, ensure_ascii=False))

        # 2) termination_checker 处理
        checker_resp = termination_checker.run(user_input=json.dumps(alpha_json, ensure_ascii=False))
        logging.info("termination_checker 返回：%s", checker_resp)

        # 3) 构造下一轮提示
        next_prompt = NEXT_PROMPT_TEMPLATE.format(checker_result=json.dumps(checker_resp, ensure_ascii=False))

    logging.info("同步无限循环正常结束")

# -------------------------------------------------
# 入口
# -------------------------------------------------
if __name__ == "__main__":
    main()