import json
with open('fields.json', 'r', encoding='utf-8') as f:
    fields_data = json.load(f)
# 预处理fields为字典 {id: description} 和列表 [id1, id2, ...]
fields_dict = {field.get('id'): field.get('description') for field in fields_data}
# fields_ids = list(fields_dict.keys())
print(len(fields_dict))
print(fields_dict)
exit()


from memo_tools import MemoTools

MT = MemoTools()
def brain_mome_all(mes: str) -> str:
    """
    这个函数是一个有着大量alpha灵感和熟悉这个平台worldquantbrain的智能体，当用户得到alpha灵感以及专业的量化问题时，可以直接调用该函数得到高质量的结果。

        Args:
            需要的可以提交的{{mes}}
        Returns:
            返回回答的结果。
    """
    MT.memorize(mes)
    return MT.ask(mes)





print(brain_mome_all("你好"))
exit()



id_alpha = str(data['alpha'])
print(id_alpha)


exit()


user_input = ""
while True:
    if "@@" in user_input:
        break
    user_input += input("You: ").strip()
print(user_input)

import requests
import json


def main():
    url = "https://qianfan.baidubce.com/v2/chat/completions"

    payload = json.dumps({
        "model": "ernie-3.5-8k",
        "messages": [
            {
                "role": "user",
                "content": "您好"
            },
            {
                "role": "assistant",
                "content": "您好！很高兴与您交流。请问有什么我可以帮助您的吗？无论是知识问答、文本创作还是其他方面的需求，我都会尽力提供帮助。"
            }
        ],
        "web_search": {
            "enable": False,
            "enable_citation": False,
            "enable_trace": False
        },
        "plugin_options": {}
    }, ensure_ascii=False)
    headers = {
        'Authorization': "",
        'appid': ''
    }

    response = requests.request("POST", url, headers=headers, data=payload.encode("utf-8"))

    print(response.text)


if __name__ == '__main__':
    main()
