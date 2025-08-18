import os, tiktoken, chromadb, openai, uuid


class MemoTools:
    """
    长期记忆
    """

    def __init__(self):
        with open("Deepseek_key", 'r', encoding='utf-8') as f:
            key_api = f.read()
        os.environ["DS_KEY"] = key_api
        # 1. 初始化 DeepSeek 客户端
        self.client = openai.OpenAI(api_key=os.getenv("DS_KEY"),
                                    base_url="https://api.deepseek.com")
        # 2. 初始化 Chroma（本地目录 db，自动建表）
        self.chroma = chromadb.PersistentClient(path="db")
        self.collection = self.chroma.get_or_create_collection(name="mem")

        # 3. 工具：切分文本（按 token 数）
        self.enc = tiktoken.get_encoding("cl100k_base")
        # 1. 本地 Ollama embedding
        self.client_emb = openai.OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama"  # 随意写
        )

    def chunks(self, text, max_tokens=400):
        tokens = self.enc.encode(text)
        for i in range(0, len(tokens), max_tokens):
            yield self.enc.decode(tokens[i:i + max_tokens])

    def embed(self, text):
        return self.client_emb.embeddings.create(
            input=text,
            model="bge-m3"
        ).data[0].embedding

    # 5. 把长文本灌进「记忆库」
    def memorize(self, long_text):
        for idx, chunk in enumerate(self.chunks(long_text)):
            vec = self.embed(chunk)
            self.collection.add(documents=[chunk],
                                embeddings=[vec],
                                ids=[str(uuid.uuid4())])

    # 6. 带记忆的问答
    def ask(self, question, logging):
        q_vec = self.embed(question)
        docs = self.collection.query(query_embeddings=[q_vec],
                                     n_results=3)["documents"][0]
        context = "\n".join(docs)
        prompt = f"根据以下已知信息回答：\n{context}\n\n问题：{question}"
        if logging:
            logging.info(f"————————记忆内容{prompt}————————")
        resp = self.client.chat.completions.create(model="deepseek-chat",
                                                   messages=[{"role": "user", "content": prompt}],
                                                   stream=False)

        if logging:
            logging.info(f"————————给出的回答{resp.choices[0].message.content}————————")
        return resp.choices[0].message.content
