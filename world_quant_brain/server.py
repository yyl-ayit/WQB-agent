#!/usr/bin/env python3
"""
Example MCP Server using the new simplified pattern.
This demonstrates how to create a new AI4S tool with tools defined at module level.
"""
import argparse
import json
import logging
import os
import sys
from datetime import datetime

from mcp.server.fastmcp import FastMCP
from my_fun import BrainTools
from memo_tools import MemoTools

MT = MemoTools()
BT = BrainTools(login=True)
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


def parse_args():
    """Parse command line arguments for MCP server."""
    parser = argparse.ArgumentParser(description="MCP Server")
    parser.add_argument('--port', type=int, default=50001, help='Server port (default: 50001)')
    parser.add_argument('--host', default='0.0.0.0', help='Server host (default: 0.0.0.0)')
    parser.add_argument('--log-level', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help='Logging level (default: INFO)')
    try:
        args = parser.parse_args()
    except SystemExit:
        class Args:
            port = 50001
            host = '0.0.0.0'
            log_level = 'INFO'

        args = Args()
    return args


args = parse_args()
mcp = FastMCP("world_quant_brain", host=args.host, port=args.port)


# Define tools at module level
@mcp.tool()
def history_sumit_alphas_self() -> dict:
    """
        一个用于调用历史提交成功的alphas,用于alpha生成的参考，不要对外展示，不能生成和历史重复的alpha，用于更好的生成alpha。

        Args:
        Returns:
            返回近期20条提交成功的alphas的json数据
    """
    logging.info("=====调用了history_sumit_alphas_self这个工具=====")
    return BT.history_sumit_alphas_self()


@mcp.tool()
def history_sumit_alphas_user(num: int) -> str:
    """
        只对用户展示，当用户想要查看历史提交成功的alphas时候，直接调用这个工具，并且将生成的Markdown直接展示给用户。

        Args:
            要查找提交成功的alphas的数据量{{num}}
        Returns:
            查找的Markdown格式数据
    """
    logging.info("=====调用了history_sumit_alphas_user这个工具=====")
    return BT.history_sumit_alphas_user(num)


@mcp.tool()
def get_n_os_alphas(total_alphas):
    """
        一个用于调用历史提交成功的alphas,用于alpha生成的参考，不要对外展示，不能生成和历史重复的alpha，用于更好的生成alpha。

        Args:
            需要的{{total_alphas}}总量
        Returns:
            返回近期20条提交成功的alphas的json数据
    """
    logging.info("=====调用了get_n_os_alphas这个工具=====")
    return BT.get_n_os_alphas(total_alphas)


@mcp.tool()
def plot_sharpe_vs_performance_user(mouth):
    """
         根据用户需要的的月份生成的alphas的sharpe_vs_performance的可视化图片，调用该函数可以生成sharpe和Turnover、Returns、Margin、Fitness的对比数据，
        直接将matplotlib生成的结果展示给用户。
        Args:
            需要查看的月份{{mouth}}
        Returns:
            查找的Markdown格式的图片数据
    """
    logging.info("=====调用了plot_sharpe_vs_performance_user这个工具=====")
    return BT.plot_sharpe_vs_performance_user(mouth)


@mcp.tool()
def plot_count_vs_month(x: int, y: int) -> str:
    """
       根据用户需要的的月份生成的alphas的数量对比的可视化图片,实现对两个月份各参数的数量对比分析，
       直接将matplotlib生成的结果展示给用户。

        Args:
            需要的{{x}}和{{y}}对应的月份
        Returns:
            生成的Markdown格式数据
    """
    logging.info("=====调用了plot_count_vs_month这个工具=====")
    return BT.plot_count_vs_month(x, y)


@mcp.tool()
def alpha_submit_self(alpha: dict) -> list:
    """
       内部调用，用于测评alpha的质量返回各个参数信息[alpha_id, sharpe, turnover, fitness, margin, exp, region, universe, neutralization, decay, delay,
          truncation]

        Args:
            需要的可以提交的{{alpha}}
        Returns:
            [alpha_id, sharpe, turnover, fitness, margin, exp, region, universe, neutralization, decay, delay,
          truncation]或者alpha的错误格式信息。
    """
    logging.info("=====调用了alpha_submit_self这个工具=====")
    logging.info("提交的alpha表达式 产出：%s", json.dumps(alpha, ensure_ascii=False))
    ss = BT.alpha_submit_self(alpha)
    logging.info(f"测评后的参数：{ss}")
    return ss


@mcp.tool()
def brain_mome_all(mes: str) -> str:
    """
    这个函数是一个有着大量alpha灵感和熟悉这个平台worldquantbrain的记忆智能体，当用户得到alpha灵感以及专业的量化问题时，可以直接调用该函数得到高质量的结果。

        Args:
            需要的可以提交的{{mes}}
        Returns:
            返回回答的结果。
    """
    MT.memorize(mes)
    logging.info("=====调用了brain_mome_all这个工具=====")
    ss = MT.ask(mes,logging)
    logging.info(f"回复的内容：{ss}")
    return ss


@mcp.tool()
def get_operators() -> dict:
    """
    获取所有操作符，以及对应的使用说明，生成alpha表达式之前很有必要调用和选择。

        Args:

        Returns:
            返回的json格式的数据
    """
    logging.info("=====调用了get_operators这个工具=====")
    return BT.get_operators()


@mcp.tool()
def get_fields() -> dict:
    """
    获取所有数据，以及对应的描述，生成alpha表达式之前很有必要调用和选择。

        Args:

        Returns:
            返回的json格式的数据
    """
    logging.info("=====调用了get_fields这个工具=====")
    return BT.get_fields()


if __name__ == "__main__":
    # Get transport type from environment variable, default to SSE
    transport_type = os.getenv('MCP_TRANSPORT', 'sse')
    mcp.run(transport=transport_type)
