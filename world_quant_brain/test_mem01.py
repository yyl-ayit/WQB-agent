import os

from mem0 import Memory


os.environ["DEEPSEEK_API_KEY"] = key_api
os.environ["OPENAI_API_KEY"] = openai_api_key

config = {
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "deepseek-coder",
            "ollama_base_url": "http://localhost:11434",
            "api_key": "ollama",       # 假 key，绕过 openai 客户端检查
            # "timeout": 60              # 秒
        }
    },
    "embeddings": {
        "provider": "ollama",
        "config": {
            "model": "bge-m3",
            "ollama_base_url": "http://localhost:11434",
            "api_key": "ollama",
            # "timeout": 60
        }
    },
    "vector_store": {
        "provider": "chroma",
        "config": {"collection_name": "wqb", "path": "db"}
    }
}

memory = Memory.from_config(config)
memory.add("hello world", user_id="u1")
print(memory.search("hello", user_id="u1"))