import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from deal_tools import DearBrainJson
import json
from my_fun import BrainTools
BT = BrainTools()
mouth = "07"
with open('alpha_list_submitted.json', 'r') as f:
    alpha_list_submitted = json.load(f)
# print(alpha_list_submitted)
#
df_alpha_list_submitted = pd.DataFrame(alpha_list_submitted)
#
# # months = [ '01', '02', '03', '04', '05', '06', '07','08', '09', '10', '11', '12']
# # 获取不同的month，画出不同的month的performance
#
# df_month = DearBrainJson.get_month(df_alpha_list_submitted, mouth)
# df_is_performance = DearBrainJson.get_performance(df_month, 'is')
# df_os_performance = DearBrainJson.get_performance(df_month, 'os')
# sharpe_os, turnover_os, returns_os, margin_os, fitness_os, _, _ = DearBrainJson.get_performance_metrics(
#     df_os_performance)
# sharpe_is, turnover_is, returns_is, margin_is, fitness_is, _, _ = DearBrainJson.get_performance_metrics(
#     df_is_performance)
# # 调用绘图函数
# DearBrainJson.plot_sharpe_vs_performance(sharpe_os, turnover_os, returns_os, margin_os, fitness_os,
#                                          sharpe_is, turnover_is, returns_is, margin_is, fitness_is,
#                                          mouth)
# month_pairs = [
#     ('01', '04'), ('02', '05'), ('03', '06'),
#     ('04', '07'), ('05', '08'), ('06', '09'),
#     ('07', '10'), ('08', '11'), ('09', '12')
# ]
alpha_list_submitted = BT.get_n_os_alphas(3000)
print(alpha_list_submitted.head())
print(BT.plot_count_vs_month(8, 7, alpha_list_submitted))

exit()
month_pairs = [
    ('07', '08')
]

# 对每一对月份进行对比分析
for month1, month2 in month_pairs:
    # 获取两个月份的数据
    df_month1 = DearBrainJson.get_month(df_alpha_list_submitted, month1)
    df_month2 = DearBrainJson.get_month(df_alpha_list_submitted, month2)

    # 获取两个月份的IS和OS绩效数据
    df_is_performance1 = DearBrainJson.get_performance(df_month1, 'is')
    df_os_performance1 = DearBrainJson.get_performance(df_month1, 'os')
    sharpe_os1, turnover_os1, returns_os1, margin_os1, fitness_os1, selfcorrelation_os1, prodcorrelation_os1 = DearBrainJson.get_performance_metrics(
        df_os_performance1)
    sharpe_is1, turnover_is1, returns_is1, margin_is1, fitness_is1, selfcorrelation_is1, prodcorrelation_is1 = DearBrainJson.get_performance_metrics(
        df_is_performance1)

    df_is_performance2 = DearBrainJson.get_performance(df_month2, 'is')
    df_os_performance2 = DearBrainJson.get_performance(df_month2, 'os')
    sharpe_os2, turnover_os2, returns_os2, margin_os2, fitness_os2, selfcorrelation_os2, prodcorrelation_os2 = DearBrainJson.get_performance_metrics(
        df_os_performance2)
    sharpe_is2, turnover_is2, returns_is2, margin_is2, fitness_is2, selfcorrelation_is2, prodcorrelation_is2 = DearBrainJson.get_performance_metrics(
        df_is_performance2)

    # 绘制两个月份IS性能的对比图
    fig, axes = plt.subplots(4, 2, figsize=(15, 15))
    fig.suptitle(f'IS Performance Comparison: Month {month1} vs Month {month2}', fontsize=16)

    # Sharpe Ratio 对比
    sns.histplot(sharpe_is1, bins=20, kde=True, ax=axes[0, 0], color='blue', label=f'Month {month1}',
                 element='step')
    sns.histplot(sharpe_is2, bins=20, kde=True, ax=axes[0, 0], color='red', label=f'Month {month2}',
                 element='step')
    axes[0, 0].set_title('Sharpe Ratio Distribution')
    axes[0, 0].legend()

    # Turnover 对比
    sns.histplot(turnover_is1, bins=20, kde=True, ax=axes[0, 1], color='blue', label=f'Month {month1}',
                 element='step')
    sns.histplot(turnover_is2, bins=20, kde=True, ax=axes[0, 1], color='red', label=f'Month {month2}',
                 element='step')
    axes[0, 1].set_title('Turnover Distribution')
    axes[0, 1].legend()

    # Returns 对比
    sns.histplot(returns_is1, bins=20, kde=True, ax=axes[1, 0], color='blue', label=f'Month {month1}',
                 element='step')
    sns.histplot(returns_is2, bins=20, kde=True, ax=axes[1, 0], color='red', label=f'Month {month2}',
                 element='step')
    axes[1, 0].set_title('Returns Distribution')
    axes[1, 0].legend()

    # Margin 对比
    sns.histplot(margin_is1, bins=20, kde=True, ax=axes[1, 1], color='blue', label=f'Month {month1}',
                 element='step')
    sns.histplot(margin_is2, bins=20, kde=True, ax=axes[1, 1], color='red', label=f'Month {month2}',
                 element='step')
    axes[1, 1].set_title('Margin Distribution')
    axes[1, 1].legend()

    # Fitness 对比
    sns.histplot(fitness_is1, bins=20, kde=True, ax=axes[2, 0], color='blue', label=f'Month {month1}',
                 element='step')
    sns.histplot(fitness_is2, bins=20, kde=True, ax=axes[2, 0], color='red', label=f'Month {month2}',
                 element='step')
    axes[2, 0].set_title('Fitness Distribution')
    axes[2, 0].legend()
    # Self-Correlation 对比
    sns.histplot(selfcorrelation_is1, bins=20, kde=True, ax=axes[2, 1], color='blue', label=f'Month {month1}',
                 element='step')
    sns.histplot(selfcorrelation_is2, bins=20, kde=True, ax=axes[2, 1], color='red', label=f'Month {month2}',
                 element='step')
    axes[2, 1].set_title('Self-Correlation Distribution')
    axes[2, 1].legend()
    # Prod-Correlation 对比
    sns.histplot(prodcorrelation_is1, bins=20, kde=True, ax=axes[3, 0], color='blue', label=f'Month {month1}',
                 element='step')
    sns.histplot(prodcorrelation_is2, bins=20, kde=True, ax=axes[3, 0], color='red', label=f'Month {month2}',
                 element='step')
    axes[3, 0].set_title('Prod-Correlation Distribution')
    axes[3, 0].legend()

    # 计算并显示关键指标的平均值对比
    comparison_data = {
        'Metric': ['Sharpe', 'Turnover', 'Returns', 'Margin', 'Fitness', 'Self-Correlation', 'Prod-Correlation'],
        f'Month {month1}': [
            sharpe_is1.mean(),
            turnover_is1.mean(),
            returns_is1.mean(),
            margin_is1.mean(),
            fitness_is1.mean(),
            selfcorrelation_is1.mean(),
            prodcorrelation_is1.mean()
        ],
        f'Month {month2}': [
            sharpe_is2.mean(),
            turnover_is2.mean(),
            returns_is2.mean(),
            margin_is2.mean(),
            fitness_is2.mean(),
            selfcorrelation_is2.mean(),
            prodcorrelation_is2.mean()
        ]
    }
    df_comparison = pd.DataFrame(comparison_data)
    axes[3, 1].axis('off')
    table = axes[3, 1].table(
        cellText=df_comparison.round(3).values,
        colLabels=df_comparison.columns,
        cellLoc='center',
        loc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
    axes[3, 1].set_title('Performance Metrics Comparison')

    plt.tight_layout()
    plt.subplots_adjust(top=0.95)
    plt.show()
