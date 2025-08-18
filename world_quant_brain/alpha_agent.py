import os
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
- 如果结果不正确，需要返回重新生成的提示
- 你需要调用alpha_submit_self工具，并且拿到返回的结果。
- 然后你也可以调用其他工具，如熟悉这个平台worldquantbrain的记忆智能体等工具，然后对结果进行分析和给出建议
返回结果。
""",
    include_contents='none',
    tools=[toolset],
    # output_key="termination_signal"
)


loop = LoopAgent(
    name="react_loop",
    sub_agents=[alpha_agent, termination_checker],
    max_iterations=3  # 防止死循环
)

# ——————————
# STEP 5: 外部调用流程（Sequential）
root_agent = loop
