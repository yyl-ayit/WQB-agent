import requests
from os.path import expanduser
import pandas as pd
from deal_tools import DearBrainJson
import json



class BrainTools:
    """
    platform.worldquantbrain平台相关的功能代码
    """

    def __init__(self, login=False):
        if not login:
            self.session = {}
        else:
            with open(expanduser('brain_credentials_copy')) as f:
                credentials = eval(f.read())

            username, password = credentials

            sess = requests.Session()
            # Save credentials into session
            sess.auth = (username, password)

            # Send a POST request to the /authentication API
            response = sess.post('https://api.worldquantbrain.com/authentication')
            print(response.content)
            self.session = sess

    def history_sumit_alphas_self(self) -> json:
        """
            一个用于调用历史提交成功的alphas,用于alpha生成的参考，不要对外展示，不能生成和历史重复的alpha，用于更好的生成alpha。

            Args:
            Returns:
                返回近期20条提交成功的alphas的json数据
        """
        base_url = 'https://api.worldquantbrain.com/users/self/alphas'
        filter_params = {
            'limit': 20,
            'offset': 0,
            'status': 'ACTIVE',
            'order': '-os.sharpe',
            'hidden': 'false'
        }

        # 发送GET请求获取 Alphas 列表
        response = self.session.get(base_url, params=filter_params)

        return response.json()

    def history_sumit_alphas_user(self, num: int) -> str:
        """
            只对用户展示，当用户想要查看历史提交成功的alphas时候，直接调用这个工具，并且将生成的Markdown直接展示给用户。

            Args:
                要查找提交成功的alphas的数据量{{num}}
            Returns:
                查找的Markdown格式数据
        """
        # 定义获取 Alphas 的 URL 和参数
        print("*---" * 100)
        print(num)
        base_url = 'https://api.worldquantbrain.com/users/self/alphas'
        filter_params = {
            'limit': num,
            'offset': 0,
            'status': 'ACTIVE',
            'order': '-os.sharpe',
            'hidden': 'false'
        }

        # 发送GET请求获取 Alphas 列表
        response = self.session.get(base_url, params=filter_params)
        print(response.text)
        print(response.status_code)
        print("---" * 100)
        alphas_data = response.json()
        markdown_content = f"# Alphas 信息\n\n总共找到 {alphas_data['count']} 个符合条件的 Alphas\n"
        ls = []
        for index, alpha in enumerate(alphas_data['results'], start=1):
            ls.append(alpha['regular']['code'])
            markdown_content += "\n---\n"
            markdown_content += f"## Alpha ID {index}: {alpha['id']}\n"
            # 添加表达式
            if 'regular' in alpha and 'code' in alpha['regular']:
                markdown_content += "### **Fast Expression表达式**:\n"
                markdown_content += f"```Fast Expression\n{alpha['regular']['code']}\n```\n"
            else:
                markdown_content += "### **Fast Expression表达式**: 未找到\n"
            # 添加设置参数
            if 'settings' in alpha:
                settings_json = json.dumps(alpha['settings'], indent=2, ensure_ascii=False)
                markdown_content += "### **Simulation Settings设置参数**:\n"
                markdown_content += f"```js\n{settings_json}\n```\n"
            else:
                markdown_content += "### **Simulation Settings设置参数**: 未找到\n"
        return markdown_content

    def get_n_os_alphas(self, total_alphas, limit=100):
        """
            一个用于调用历史提交成功的alphas,用于alpha生成的参考，不要对外展示，不能生成和历史重复的alpha，用于更好的生成alpha。

            Args:
                需要的{{total_alphas}}总量
            Returns:
                返回近期20条提交成功的alphas的json数据
        """

        with open('alpha_list_submitted.json', 'r') as f:

            alpha_list_submitted = json.load(f)
        # print("alpha_list_submitted", alpha_list_submitted)
        if alpha_list_submitted:
            return alpha_list_submitted
        fetched_alphas = []

        offset = 0

        # Keep fetching alphas until the required number of alphas is reached or no more alphas are available.

        while len(fetched_alphas) < total_alphas:

            response = self.session.get(

                f"https://api.worldquantbrain.com/users/self/alphas?stage=OS&limit={limit}&offset={offset}"

            )

            alphas = response.json()["results"]

            fetched_alphas.extend(alphas)

            if len(alphas) < limit:
                break

            offset += limit

        return fetched_alphas[:total_alphas]

    def plot_sharpe_vs_performance_user(self, mouth="07"):
        """
            根据用户需要的的月份生成的alphas的sharpe_vs_performance的可视化图片，调用该函数可以生成sharpe和Turnover、Returns、Margin、Fitness的对比数据，
            直接将matplotlib生成的结果展示给用户。
            Args:
                需要的{{mouth}}对应的月份
            Returns:
                生成的Markdown格式数据
        """
        if len(str(mouth)) == 1:
            mouth = "0" + str(mouth)
        alpha_list_submitted = self.get_n_os_alphas(3000)

        df_alpha_list_submitted = pd.DataFrame(alpha_list_submitted)

        # months = [ '01', '02', '03', '04', '05', '06', '07','08', '09', '10', '11', '12']
        # 获取不同的month，画出不同的month的performance

        df_month = DearBrainJson.get_month(df_alpha_list_submitted, mouth)
        df_is_performance = DearBrainJson.get_performance(df_month, 'is')
        df_os_performance = DearBrainJson.get_performance(df_month, 'os')
        sharpe_os, turnover_os, returns_os, margin_os, fitness_os, _, _ = DearBrainJson.get_performance_metrics(
            df_os_performance)
        sharpe_is, turnover_is, returns_is, margin_is, fitness_is, _, _ = DearBrainJson.get_performance_metrics(
            df_is_performance)
        # 调用绘图函数
        return DearBrainJson.plot_sharpe_vs_performance(sharpe_os, turnover_os, returns_os, margin_os, fitness_os,
                                                        sharpe_is, turnover_is, returns_is, margin_is, fitness_is,
                                                        mouth)

    def plot_count_vs_month(self, x: int, y: int) -> str:
        """
           根据用户需要的的月份生成的alphas的每个月的数量占比的可视化图片,将2个月份做对比,，调用该函数可以生成Turnover、Returns、Margin、Fitness的数量占比数据，
           直接将matplotlib生成的结果展示给用户。

            Args:
                需要的{{x}}和{{y}}对应的月份
            Returns:
                生成的Markdown格式数据
        """
        alpha_list_submitted = self.get_n_os_alphas(3000)
        df_alpha_list_submitted = pd.DataFrame(alpha_list_submitted)
        return DearBrainJson.plot_count_vs_month(x, y, df_alpha_list_submitted)

    def alpha_submit_self(self, alpha: dict) -> list:
        """
           内部调用，用于测评alpha的质量返回各个参数信息[alpha_id, sharpe, turnover, fitness, margin, exp, region, universe, neutralization, decay, delay,
              truncation]

            Args:
                需要的可以提交的{{alpha}}
            Returns:
                [alpha_id, sharpe, turnover, fitness, margin, exp, region, universe, neutralization, decay, delay,
              truncation]或者alpha的错误格式信息。
        """

        return DearBrainJson.alpha_submit_self(alpha)

    def get_operators(self) -> dict:
        """
        获取所有操作符，以及对应的使用说明，生成alpha表达式之前很有必要调用和选择。

            Args:

            Returns:
                返回的json格式的数据
        """
        with open('operators.json', 'r', encoding='utf-8') as f:
            operators = json.load(f)
        return operators

    def get_fields(self) -> dict:
        """
        获取所有数据，以及对应的描述，生成alpha表达式之前很有必要调用和选择。

            Args:

            Returns:
                返回的json格式的数据
        """

        with open('fields.json', 'r', encoding='utf-8') as f:
            fields_data = json.load(f)
        # 预处理fields为字典 {id: description} 和列表 [id1, id2, ...]
        fields_dict = {field.get('id'): field.get('description') for field in fields_data[:100]}
        # fields_ids = list(fields_dict.keys())
        return fields_dict
