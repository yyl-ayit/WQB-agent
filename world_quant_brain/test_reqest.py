

import requests, json, os
from pathlib import Path
from playwright.sync_api import sync_playwright

# -----------------------------------
# 第 1 步：requests 登录拿 cookie
# -----------------------------------
def get_cookie_jar():
    # cred_file = Path(__file__).with_name('wqb_cred.json')
    username, password = []

    session = requests.Session()
    # Save credentials into session
    session.auth = (username, password)

    # Send a POST request to the /authentication API
    response = session.post('https://api.worldquantbrain.com/authentication')
    print(response.content)
    # login_body = {"email": username, "password": password}
    # print(response.raise_for_status())
    print(session.cookies)
    # 转成 playwright 需要的格式
    cookies = [
        {"name": c.name, "value": c.value, "domain": ".worldquantbrain.com", "path": c.path}
        for c in session.cookies
    ]
    return cookies

# -----------------------------------
# 第 2 步：playwright 带 cookie 翻页
# -----------------------------------
# ------------- 2. 爬取 -------------
def run_spider():
    cookies = get_cookie_jar()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context()          # 1. 先建上下文
        ctx.add_cookies(cookies)             # 2. 再塞 cookie

        page = ctx.new_page()
        page.goto("https://support.worldquantbrain.com"
                  "/hc/zh-cn/search?query=Alpha%E7%81%B5%E6%84%9F&utf8=%E2%9C%93")

        all_links, page_num = [], 1
        while True:
            print(f"[+] 第 {page_num} 页")
            page.wait_for_selector(".search-results-list")
            links = page.locator(".search-result-title a").evaluate_all(
                "els => els.map(e => e.href)")
            all_links.extend(links)

            next_btn = page.locator("a.pagination-next-link")
            if next_btn.count() == 0 or next_btn.get_attribute("aria-disabled") == "true":
                break
            next_btn.click()
            page.wait_for_load_state("networkidle")
            page_num += 1

        browser.close()
        return all_links


if __name__ == "__main__":
    links = run_spider()
    print(f"\n共抓到 {len(links)} 条链接")
    for u in links:
        print(u)