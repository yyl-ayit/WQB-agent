import requests
import json


def extract_text_from_response(raw_bytes: bytes) -> str:
    try:
        raw_str = raw_bytes.decode('utf-8').strip().lstrip('data: ')
        data = json.loads(raw_str)
        return data["content"]["parts"][0]["text"]
    except Exception as e:
        return f"解析失败: {e}"


def chat_angent(message):
    """
    :param message:
    :return:
    """

    headers = {
        'Accept': 'text/event-stream',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'http://127.0.0.1:50002',
        'Referer': 'http://127.0.0.1:50002/dev-ui/?app=agent&session=fdf280e7-6fe9-4e10-a60b-6a3ebd5fec09',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0',
        'sec-ch-ua': '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    json_data = {
        'appName': 'loop_submit',
        'userId': 'user',
        'sessionId': requests.get('http://127.0.0.1:8000/apps/loop_submit/users/user/sessions').json()[0]['id'],
        'newMessage': {
            'role': 'user',
            'parts': [
                {
                    'text': message,
                },
            ],
        },
        'streaming': False,
        'stateDelta': None,
    }
    print(json_data)
    response = requests.post('http://127.0.0.1:8000/run_sse', headers=headers, json=json_data, stream=True)
    print(response.content)
    return extract_text_from_response(response.content)


print(chat_angent('请生成一个可直接测评的并且高质量的 alpha 表达式，仅返回 JSON'))
# print('1')
# # 2. 把 response 包装成 SSEClient
# client = SSEClient(response)
#
# # 3. 逐行打印事件
# for event in client.events():
#     # event.data 是字符串，需要再 json.loads 一次
#     # print(event)
#     try:
#         chunk = json.loads(event.data)
#
#         if chunk.get('partial'):
#             print(chunk.get('content').get('parts')[0]['text'],end="",flush=True)
#         else:
#             print("++++++++++++++++++++++++++++++++++未显示操作+++++++++++++++++++++++++++++++++++++")
#             print(chunk.get('content').get('parts'))
#             print("-------------------------------------------------------------------------------")
#         # print(chunk.get("content").get('parts'), end="", flush=True)
#     except Exception:
#         # 非 JSON 或心跳事件，直接打印
#         print(event.data)
# #
# # data = {'content': {'parts': [{'functionCall': {'id': 'call_0_efcfcaf7-104c-40c2-bd65-f3c9282e064c',
# #                                                 'args': {'x': 1, 'y': 2}, 'name': 'example_calculation'}}],
# #                     'role': 'model'}, 'partial': False, 'invocationId': 'e-c2071db9-fca6-44d2-8f4c-c2ddc0b52763',
# #         'author': 'mcp_sse_agent', 'actions': {'stateDelta': {}, 'artifactDelta': {}, 'requestedAuthConfigs': {}},
# #         'longRunningToolIds': [], 'id': '968a4fe6-6894-4ad4-a892-45e9b63968d9', 'timestamp': 1755053419.658988}
# # data2 = {'content': {'parts': [{'functionResponse': {'id': 'call_0_efcfcaf7-104c-40c2-bd65-f3c9282e064c',
# #                                                      'name': 'example_calculation', 'response': {
# #         'result': {'content': [{'type': 'text', 'text': '{\n  "sum": 3.0,\n  "product": 2.0,\n  "ratio": 0.5\n}'}],
# #                    'isError': False}}}}], 'role': 'user'}, 'invocationId': 'e-c2071db9-fca6-44d2-8f4c-c2ddc0b52763',
# #          'author': 'mcp_sse_agent', 'actions': {'stateDelta': {}, 'artifactDelta': {}, 'requestedAuthConfigs': {}},
# #          'id': 'd963771a-90d3-4780-8c0a-47e80cdcdf30', 'timestamp': 1755053425.819139}
# # data3 = {'content': {'parts': [{'text': '调用'}], 'role': 'model'}, 'partial': True,
# #          'invocationId': 'e-c2071db9-fca6-44d2-8f4c-c2ddc0b52763', 'author': 'mcp_sse_agent',
# #          'actions': {'stateDelta': {}, 'artifactDelta': {}, 'requestedAuthConfigs': {}},
# #          'id': '5acf9bfb-a16c-45a4-a761-0850d5751612', 'timestamp': 1755053425.824838}

# Note: json_data will not be serialized by requests
# exactly as it was in the original request.
# data = '{"appName":"paper_search_demo","userId":"user","sessionId":"ee8b094a-1ebf-4bdb-8393-e3a6986d60b6","newMessage":{"role":"user","parts":[{"text":"帮我调用example_calculation这个工具，传入1 2"}]},"streaming":true,"stateDelta":null}'.encode()
# response = requests.post('http://127.0.0.1:8000/run_sse', headers=headers, data=data)
