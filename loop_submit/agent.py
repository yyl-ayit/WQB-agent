import logging
import os
import sys
from datetime import datetime

from google.adk.agents import Agent, LoopAgent, SequentialAgent
from google.adk.runners import InMemoryRunner
from google.adk.agents.invocation_context import InvocationContext
from google.adk.tools.mcp_tool import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
from google.adk.models.lite_llm import LiteLlm

with open("Deepseek_key", 'r', encoding='utf-8') as f:
    key_api = f.read()
os.environ['DEEPSEEK_API_KEY'] = key_api
toolset = MCPToolset(
    connection_params=SseServerParams(
        url="http://127.0.0.1:50001/sse",
    ),
)

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

# ——————————
# STEP 1: 定义 ReAct Agent
react_agent = Agent(
    name="react_agent",
    model=LiteLlm(model="deepseek/deepseek-chat"),
    instruction="""
您是遵循 ReAct 框架的基于worldquantbrain这个平台的量化分析的AI助手：
1. REASON: 先思考你需要哪些信息，以及接下来怎么做；
2. ACT: 当思考完毕后调用工具（如搜索）获取信息；
3. OBSERVE: 阅读工具返回结果；
4. 给出完整回答。
""",
    tools=[toolset],
    description="Uses ReAct reasoning and acting cycles to answer complex queries"
)

alpha_agent = Agent(
    name="alpha_agent",
    model=LiteLlm(model="deepseek/deepseek-chat"),
    instruction="""
您是基于alpha表达式生成的AI助手：
alpha = {'type': 'REGULAR',
         'settings': {'instrumentType': 'EQUITY', 'region': 'USA', 'universe': 'TOP3000', 'delay': 1,
                      'decay': 0, 'neutralization': 'SECTOR', 'truncation': 0.08, 'pasteurization': 'ON',
                      'unitHandling': 'VERIFY', 'nanHandling': 'OFF', 'language': 'FASTEXPR', 'visualization': False},
         'regular': ''}
你可以调用任何能够使用的工具，建议询问熟悉这个平台worldquantbrain的记忆智能体相关的alpha模板等工具，来生成alpha表达式，alpha表达式可以一阶或者多阶，然后填入到'regular'对应的键值中，最后只返回json格式，即一个可以直接测评的alpha,例如
{'type': 'REGULAR',
         'settings': {'instrumentType': 'EQUITY', 'region': 'USA', 'universe': 'TOP3000', 'delay': 1,
                      'decay': 0, 'neutralization': 'SECTOR', 'truncation': 0.08, 'pasteurization': 'ON',
                      'unitHandling': 'VERIFY', 'nanHandling': 'OFF', 'language': 'FASTEXPR', 'visualization': False},
         'regular': 'group_rank(-ts_sum(winsorize(ts_backfill(vec_avg(anl4_guiqfv4_est), 120), std=4), 66),densify(market))'}
""",
    tools=[toolset],
    description="Uses ReAct reasoning and acting cycles to answer complex queries"
)
# ——————————
# STEP 2: 定义终止判断 Agent（仅阅读工具返回结果，不发起工具调用）
termination_checker = Agent(
    name="termination_checker",
    model=LiteLlm(model="deepseek/deepseek-chat"),
    instruction="""
你会收到之前工具的 observation 结果：
- 你需要调用alpha_submit_self工具，并且拿到返回的结果。
- 然后你也可以调用其他工具，如熟悉这个平台worldquantbrain的记忆智能体等工具，然后对结果进行分析和给出建议
返回结果。
""",
    include_contents='none',
    tools=[toolset],
    # output_key="termination_signal"
)

# ——————————
# STEP 3: 定义 Refinement Agent，如果是继续，就让 react_agent 再运行
# class RefinementAgent(Agent):
#     async def _run_async_impl(self, ctx: InvocationContext):
#         signal = ctx.session.state.get("termination_signal", "")
#         if signal.strip() == "DONE":
#             # 终止循环，不调用子 Agent
#             return
#         # 否则再次调用 react_agent
#         async for event in react_agent.run_async(ctx):
#             yield event


# refiner = RefinementAgent(
#     name="refiner",
#     model="gemini-2.0-pro",
#     include_contents='none',
# )

# ——————————
# STEP 4: 用 LoopAgent 包装反复运行



loop = LoopAgent(
    name="react_loop",
    sub_agents=[alpha_agent, termination_checker],
)

# ——————————
# STEP 5: 外部调用流程（Sequential）
root_agent = loop

# ——————————
# # 模拟 Runner 启动流程：
# async def main():
#     runner = InMemoryRunner(agent=root_agent, app_name="react_app", session_id="sess1", user_id="userA")
#     async for evt in runner.run_async(new_message=None):
#         pass  # 仅为了触发完整流程
#     final_state = runner.session.state
#     print("Final state:", final_state)
#
# if __name__ == "__main__":
#     asyncio.run(main())
