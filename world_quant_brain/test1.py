from my_fun import BrainTools

if __name__ == '__main__':
    Brain = BrainTools()
    # BrainTools.history_sumit_alphas()
    # 定义获取 Alphas 的 URL 和参数
    base_url = 'https://api.worldquantbrain.com/users/self/alphas'
    filter_params = {
        'limit': 100,
        'offset': 0,
        'status': 'ACTIVE',
        'order': '-os.sharpe',
        'hidden': 'false'
    }

    # 发送GET请求获取 Alphas 列表
    response = Brain.session.get(base_url, params=filter_params)
    print(response.json())
