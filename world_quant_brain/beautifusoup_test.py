#!/usr/bin/env python3
# extract_href.py

from bs4 import BeautifulSoup
import os
import json
file_names = [i for i in os.listdir("data_community")]
ls_url = []
S= ""
for file_name in file_names:
    path = os.path.join("data_community", file_name)
    with open(path, 'r', encoding='utf-8') as f:
        data_html = f.read()

    # 解析 HTML
    soup = BeautifulSoup(data_html, 'html.parser')
    # print("".join(soup.text.split()).strip())
    S += "".join(soup.text.split()).strip() + "\n"
with open("big_text.txt", 'w', encoding='utf-8') as f:
    f.write(S)


#     # 提取 href
#     li_tag_ls = soup.find_all('li', class_='search-result-list-item')
#     for li_tag in li_tag_ls:
#         # print(a_tag)
#         h2_tag = li_tag.find('h2')
#         a_tag = h2_tag.find('a').get('href')
#         ls_url.append("https://support.worldquantbrain.com" + a_tag)
#
# print("帖子数量", len(ls_url))
#
#
#
# # 1️⃣ 保存到文件
# with open("urls.json", "w", encoding="utf-8") as f:
#     json.dump(ls_url, f, ensure_ascii=False, indent=2)
#
# print(f"已保存 {len(ls_url)} 条 URL 到 urls.json")
#
# # 2️⃣ 从文件读回来
# with open("urls.json", "r", encoding="utf-8") as f:
#     loaded_urls = json.load(f)
#
# print("读取完成，共", len(loaded_urls), "条")


