import os, tiktoken, chromadb, openai, uuid
from tqdm import tqdm
with open("Deepseek_key", 'r', encoding='utf-8') as f:
    key_api = f.read()
base_url = "https://api.deepseek.com"
os.environ["DS_KEY"] = key_api
# 1. 初始化 DeepSeek 客户端
client = openai.OpenAI(api_key=os.getenv("DS_KEY"),
                       base_url="https://api.deepseek.com")
# 2. 初始化 Chroma（本地目录 db，自动建表）
chroma = chromadb.PersistentClient(path="db")
collection = chroma.get_or_create_collection(name="mem")

# 3. 工具：切分文本（按 token 数）
enc = tiktoken.get_encoding("cl100k_base")
# 1. 本地 Ollama embedding
client_emb = openai.OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # 随意写
)


def chunks(text, max_tokens=400):
    tokens = enc.encode(text)
    for i in tqdm(range(0, len(tokens), max_tokens)):
        yield enc.decode(tokens[i:i + max_tokens])


def embed(text):
    return client_emb.embeddings.create(
        input=text,
        model="bge-m3"
    ).data[0].embedding


# 5. 把长文本灌进「记忆库」
def memorize(long_text):
    for idx, chunk in enumerate(chunks(long_text)):
        vec = embed(chunk)
        collection.add(documents=[chunk],
                       embeddings=[vec],
                       ids=[str(uuid.uuid4())])


# 6. 带记忆的问答
def ask(question, top_k=3):
    q_vec = embed(question)
    docs = collection.query(query_embeddings=[q_vec],
                            n_results=top_k)["documents"][0]
    context = "\n".join(docs)
    prompt = f"根据以下已知信息回答：\n{context}\n\n问题：{question}"
    resp = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "user", "content": prompt}],
                                          stream=False)
    return resp.choices[0].message.content


# ------------------- 一次跑通示例 -------------------
if __name__ == "__main__":
    # 假设你有大量文本
    my_docs = open("big_text.txt", encoding="utf-8").read()
    memorize(my_docs)  # 只需执行一次，后续可增量


    # print(ask("请用三句话总结这份资料的核心观点"))
