# wqb_login_then_spider.py
import random
import time

from playwright.sync_api import sync_playwright
# save_all_pages.py
from pathlib import Path
import json

path_ = Path(r"E:\PycharmProject\agent_try\build-your-agent\agents\world_quant_brain\data_community")
path_.parent.mkdir(parents=True, exist_ok=True)

# 2️⃣ 从文件读回来
with open("urls.json", "r", encoding="utf-8") as f:
    loaded_urls = json.load(f)

print("读取完成，共", len(loaded_urls), "条")
page_num = 1
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # 一步到位：浏览器里登录后再爬
    page.goto("https://platform.worldquantbrain.com/")

    a = input("手动")
    for url in loaded_urls:
        try:
            # page.goto("https://support.worldquantbrain.com/hc/zh-cn/search?query=Alpha灵感")
            page.goto(url)
            # 等待页面加载完成
            page.wait_for_selector("main", timeout=0)

            # 保存整页源码
            html_path = path_ / f"data_{page_num:03d}.txt"
            # html_path.parent.mkdir(parents=True, exist_ok=True)
            html_path.write_text(page.content(), encoding="utf-8")
            print(f"[+] 已保存 {html_path}")

            page_num += 1
            time.sleep(random.randint(3, 7))
        except Exception as e:
            print(str(e))
            pass

    browser.close()
