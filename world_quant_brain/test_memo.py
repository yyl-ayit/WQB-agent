from openai import OpenAI
from mem0 import Memory
import os

base_url = "https://api.deepseek.com"
os.environ["DEEPSEEK_API_KEY"] = key_api
os.environ["OPENAI_API_KEY"] = openai_api_key
# os.environ["OPENAI_BASE_URL"] = base_url

# 定义 Mem0 的配置，包括 LLM 模型信息和向量数据库（使用 Chroma）
config = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": "deepseek-chat",
            "temperature": 0.2,
            "max_tokens": 4000,
            "api_key": key_api,
            "openai_base_url": "https://api.deepseek.com/v1"
        }
    },
    # "embeddings": {
    #     "provider": "ollama",            # ← 必须是 ollama
    #     "config": {
    #         "model": "bge-m3",           # ← 模型名
    #         "base_url": "http://localhost:11434"  # ← 正确字段名
    #         # 删掉 Authorization
    #     }
    # },
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "world_quant_brain",
            "path": "db"
        }
    }
}
# 初始化 OpenAI 客户端
openai_client = OpenAI(
    api_key=key_api,
    base_url=base_url
)

# 根据上述配置初始化记忆对象
memory = Memory.from_config(config)


# 核心函数：与 AI 对话，并利用记忆增强响应
def chat_with_memories(message: str, user_id: str = "default_user") -> str:
    # 第一步：从记忆中检索与当前用户输入最相关的记忆内容
    print(message, user_id)
    relevant_memories = memory.search(query=message, user_id=user_id, limit=3)

    # 将检索到的记忆整理成字符串，作为系统提示输入
    memories_str = "\\n".join(f"- {entry['memory']}" for entry in relevant_memories["results"])

    # 构建系统提示，告诉 AI 要参考哪些记忆内容
    system_prompt = (
        "你是一个基于https://platform.worldquantbrain.com/这个平台的量化分析师，主要是学习，并生成通过工具提交的alpha，然后根据返回的结果，再次优化和提交。根据查询和记忆回答问题。\\n"
        f"User Memories:\\n{memories_str}"
    )

    # 构造对话历史，系统提示 + 当前用户问题
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ]

    # 使用 OpenAI 接口生成对话回复
    response = openai_client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )
    assistant_response = response.choices[0].message.content  # 获取回复内容

    # 将这轮对话（用户和 AI 的发言）添加进记忆库
    messages.append({"role": "assistant", "content": assistant_response})
    memory.add(messages, user_id=user_id)

    return assistant_response  # 返回 AI 的回答


# 命令行对话主入口
def main():
    print("Chat with AI (type 'exit' to quit)")
    while True:
        user_input = input("You: ").strip()
        # print(user_input)
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        print(f"AI: {chat_with_memories(message=user_input, user_id='test_1')}")


# 程序主执行入口
if __name__ == "__main__":
    main()
