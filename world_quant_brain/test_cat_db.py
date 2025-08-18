#!/usr/bin/env python3
# view_memory.py
import os
import chromadb
from chromadb.config import Settings

# 1. 连接到本地持久化目录（必须和 memorize 时用的 path 一致）
DB_PATH = "db"
if not os.path.isdir(DB_PATH):
    raise RuntimeError(f"目录 {DB_PATH} 不存在，记忆库尚未创建！")

client = chromadb.PersistentClient(path=DB_PATH)

# 2. 拿到同一个 collection
collection = client.get_collection(name="mem")

# 3. 取出全部数据
all_data = collection.get()

if not all_data["documents"]:
    print("记忆库当前为空。")
else:
    print(f"共找到 {len(all_data['documents'])} 条文档：\n")
    num = 0
    for doc, id_ in zip(all_data["documents"], all_data["ids"]):
        # 打印前 200 字符，避免刷屏
        preview = doc.replace("\n", " ")[:200]
        print(f"[ID: {id_}] {preview}...")
        num += 1
        if num % 100 == 0:
            break