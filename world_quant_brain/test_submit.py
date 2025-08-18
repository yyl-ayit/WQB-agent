import json
from os.path import expanduser

import requests

from time import sleep
from my_fun import BrainTools

# BT = BrainTools()
failure_count = 0
keep_trying = True  # 控制while循环迭代的标志
sim_progress_url = None
alpha = {'type': 'REGULAR',
         'settings': {'instrumentType': 'EQUITY', 'region': 'USA', 'universe': 'TOP3000', 'delay': 1,
                      'decay': 0, 'neutralization': 'SECTOR', 'truncation': 0.08, 'pasteurization': 'ON',
                      'unitHandling': 'VERIFY', 'nanHandling': 'OFF', 'language': 'FASTEXPR', 'visualization': False},
         'regular': 'group_rank(-ts_sum(winsorize(ts_backfill(vec_avg(anl4_guiqfv4_est), 120), std=4), 66),densify(market))'}


def login():
    with open(expanduser('brain_credentials_copy')) as f:
        credentials = eval(f.read())

    username, password = credentials

    sess = requests.Session()
    # Save credentials into session
    sess.auth = (username, password)

    # Send a POST request to the /authentication API
    response = sess.post('https://api.worldquantbrain.com/authentication')
    print(response.content)
    return sess


def locate_alpha(s, alpha_id):
    """
    Retrieve and parse alpha data from an API.

    This function sends an HTTP GET request to retrieve alpha data from a specified
    API using the given alpha identifier. Upon receiving a response, it checks for
    rate-limiting headers and waits if necessary. The function then decodes the
    response content, extracts relevant performance metrics and alpha settings,
    and returns them in a list.

    Parameters:
        s (Session): A requests.Session object used for making the HTTP GET request.
        alpha_id (str): The unique identifier for the alpha to be retrieved.

    Returns:
        list: A list containing extracted alpha data, including
            - alpha_id (str)
            - sharpe (float)
            - turnover (float)
            - fitness (float)
            - margin (float)
            - expr (str): Alpha's code expression.
            - region (str): Associated region of the alpha.
            - universe (str): Universe setting for the alpha.
            - neutralization (str): Neutralization setting.
            - decay (float)
            - truncation (float)
    """
    while True:
        alpha = s.get("https://api.worldquantbrain.com/alphas/" + alpha_id)
        if "retry-after" in alpha.headers:
            sleep(float(alpha.headers["Retry-After"]))
        else:
            break
    string = alpha.content.decode('utf-8')
    metrics = json.loads(string)

    sharpe = metrics["is"]["sharpe"]
    fitness = metrics["is"]["fitness"]
    turnover = metrics["is"]["turnover"]
    margin = metrics["is"]["margin"]
    decay = metrics["settings"]["decay"]
    delay = metrics["settings"]["delay"]
    exp = metrics['regular']['code']
    universe = metrics["settings"]["universe"]
    truncation = metrics["settings"]["truncation"]
    neutralization = metrics["settings"]["neutralization"]
    region = metrics["settings"]["region"]

    triple = [alpha_id, sharpe, turnover, fitness, margin, exp, region, universe, neutralization, decay, delay,
              truncation]
    return triple


session = login()
while keep_trying:
    try:
        # 尝试发送模拟请求
        sim_resp = session.post(
            'https://api.worldquantbrain.com/simulations',
            json=alpha
        )
        print(sim_resp.text)
        # print(sim_resp.text)
        sim_progress_url = sim_resp.headers['Location']  # 从响应头中获取位置
        print(sim_progress_url)
        keep_trying = False  # 成功获取位置，退出while循环

    except Exception as e:
        # 处理异常：记录错误，休眠并增加失败次数计数
        print(f"提交时出现错误。等待15秒·······")
        sleep(15)
        failure_count += 1  # 增加失败次数计数器

    # 检查失败次数是否达到容忍限度
    if failure_count >= 7:
        session = login()  # 重新登录会话
        failure_count = 0  # 重置失败次数计数器

        # 记录并且打印消息，然后移动到下一个alpha
        print(f"No location for too many times, move to next alpha {alpha['regular']}")

        break  # 退出while循环，移动到for循环中的下一个alpha
id_alpha = ""
if not keep_trying:
    sleep(40)
    keep_trying = True
    while keep_trying:
        sleep(10)
        try:
            data = session.get(sim_progress_url).json()
            print("进程",data)
            id_alpha = str(data['alpha'])
            break
        except Exception as e:
            # print(str(e))
            pass
print(id_alpha)

# 赋值目标 alpha_id
alpha_id_ori = id_alpha
# 初始化对照组 alpha_json 列表
alpha_line = []

# 获取目标 alpha 信息
tem = locate_alpha(session, alpha_id_ori)
# 将 alpha 信息列表解包并赋值给对应的变量
[alpha_id, sharpe, turnover, fitness, margin, exp, region, universe, neutralization, decay, delay, truncation] = tem
print(alpha_id, sharpe, turnover, fitness, margin, exp, region, universe, neutralization, decay, delay, truncation)
