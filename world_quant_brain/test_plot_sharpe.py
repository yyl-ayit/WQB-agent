from my_fun import BrainTools
import pandas as pd
import matplotlib.pyplot as plt

import seaborn as sns

import numpy as np
import matplotlib.gridspec as gridspec


class DearBrainJson(object):
    """
    一个处理Brain的工具
    """

    @staticmethod
    def get_region(alpha_list_submitted, region):
        """

        :param alpha_list_submitted:
        :param region:
        :return:
        """
        # filter the alpha_list_submitted dataframe by region

        df_region = alpha_list_submitted[alpha_list_submitted['settings'].apply(lambda x: x['region'] == region)]

        return df_region

    @staticmethod
    def get_month(alpha_list_submitted, month):
        """
        根据传入的开始日期和结束日期过滤数据框

        参数:
            alpha_list_submitted (pd.DataFrame): 包含日期数据的数据框
            startday (str): 开始日期字符串，格式为"YYYY-MM-DD"
            endday (str): 结束日期字符串，格式为"YYYY-MM-DD"

        返回:
            pd.DataFrame: 过滤后的数据框，包含指定日期范围内的数据
        """
        # 提取开始日期和结束日期的年月部分
        start = f'2025-{month}'
        end = f'2025-{month}'

        # 从数据框的日期列提取年月部分（前7个字符）
        df_range = alpha_list_submitted.copy()
        df_range['year_month'] = df_range['dateSubmitted'].str[:7]

        # 筛选在指定日期范围内的数据
        filtered_df = df_range[(df_range['year_month'] >= start) & (df_range['year_month'] <= end)]

        # 返回筛选后的数据（可选：移除临时列）
        return filtered_df.drop(columns=['year_month'])

    # 示例调用
    # get_month(df_alpha_list_submitted, '01')
    @staticmethod
    def get_performance(df_region, performance_type):
        # filter the performance type from the dataframe

        df_performance = df_region[performance_type]

        return df_performance

    @staticmethod
    def get_performance_metrics(df_performance):
        # extract the performance metrics from the dataframe

        sharpe = df_performance.apply(lambda x: x.get('sharpe', np.nan))

        turnover = df_performance.apply(lambda x: x.get('turnover', np.nan))

        returns = df_performance.apply(lambda x: x.get('returns', np.nan))

        margin = df_performance.apply(lambda x: x.get('margin', np.nan))

        fitness = df_performance.apply(lambda x: x.get('fitness', np.nan))
        selfcor = df_performance.apply(lambda x: x.get('selfCorrelation', np.nan))
        prodcor = df_performance.apply(lambda x: x.get('prodCorrelation', np.nan))
        valid_mask = (prodcor != 0)  # 仅保留prodcor非0的因子

        # 应用过滤
        sharpe = sharpe[valid_mask]
        turnover = turnover[valid_mask]
        returns = returns[valid_mask]
        margin = margin[valid_mask]
        fitness = fitness[valid_mask]
        selfcor = selfcor[valid_mask]
        prodcor = prodcor[valid_mask]
        return sharpe, turnover, returns, margin * 100, fitness, selfcor, prodcor

    @staticmethod
    def plot_performance_metrics(sharpe, turnover, returns, margin, fitness, region):
        # set up the figure and axes for the subplots

        fig = plt.figure(figsize=(15, 10))

        gs = gridspec.GridSpec(3, 2, height_ratios=[1, 1, 1], width_ratios=[1, 1])

        ax0 = fig.add_subplot(gs[0, 0])

        ax1 = fig.add_subplot(gs[0, 1])

        ax2 = fig.add_subplot(gs[1, 0])

        ax3 = fig.add_subplot(gs[1, 1])

        ax4 = fig.add_subplot(gs[2, :])

        # plot the histograms for each metric

        sns.histplot(sharpe, bins=20, kde=True, ax=ax0)

        sns.histplot(turnover, bins=20, kde=True, ax=ax1)

        sns.histplot(returns, bins=20, kde=True, ax=ax2)

        sns.histplot(margin, bins=20, kde=True, ax=ax3)

        sns.histplot(fitness, bins=20, kde=True, ax=ax4)

        # set titles and labels for each subplot

        ax0.set_title(f'Sharpe Ratio Distribution in {region}')

        ax1.set_title(f'Turnover Distribution in {region}')

        ax2.set_title(f'Returns Distribution in {region}')

        ax3.set_title(f'Margin Distribution in {region}')

        ax4.set_title(f'Fitness Distribution in {region}')

        plt.tight_layout()

        plt.show()

    @staticmethod
    def plot_is_os_performance_matrix(df_is_performance, df_os_performance, region):
        # extract the performance metrics for IS and OS

        sharpe_is, turnover_is, returns_is, margin_is, fitness_is, selfcor_is, prodcor_is = DearBrainJson.get_performance_metrics(
            df_is_performance)

        sharpe_os, turnover_os, returns_os, margin_os, fitness_os, selfcor_os, prodcor_os = DearBrainJson.get_performance_metrics(
            df_os_performance)

        # for the same histpolot, we will put the IS and OS performance in the same histogram, we can use different color for the IS and OS performance

        # set up the figure and axes for the subplots

        fig = plt.figure(figsize=(15, 10))

        gs = gridspec.GridSpec(3, 2, height_ratios=[1, 1, 1], width_ratios=[1, 1])

        ax0 = fig.add_subplot(gs[0, 0])

        ax1 = fig.add_subplot(gs[0, 1])

        ax2 = fig.add_subplot(gs[1, 0])

        ax3 = fig.add_subplot(gs[1, 1])

        ax4 = fig.add_subplot(gs[2, :])

        # plot the histograms for each metric

        sns.histplot(sharpe_is, bins=20, kde=True, ax=ax0, color='blue', label='IS')

        sns.histplot(sharpe_os, bins=20, kde=True, ax=ax0, color='orange', label='OS')

        # set the x-label to be the same for both IS and OS

        ax0.set_xlabel('Sharpe Ratio')

        ax0.legend()

        sns.histplot(turnover_is, bins=20, kde=True, ax=ax1, color='blue', label='IS')

        sns.histplot(turnover_os, bins=20, kde=True, ax=ax1, color='orange', label='OS')

        ax1.set_xlabel('Turnover')

        ax1.legend()

        sns.histplot(returns_is, bins=20, kde=True, ax=ax2, color='blue', label='IS')

        sns.histplot(returns_os, bins=20, kde=True, ax=ax2, color='orange', label='OS')

        ax2.set_xlabel('Returns')

        ax2.legend()

        sns.histplot(margin_is, bins=20, kde=True, ax=ax3, color='blue', label='IS')

        sns.histplot(margin_os, bins=20, kde=True, ax=ax3, color='orange', label='OS')

        ax3.set_xlabel('Margin')

        ax3.legend()

        sns.histplot(fitness_is, bins=20, kde=True, ax=ax4, color='blue', label='IS')

        sns.histplot(fitness_os, bins=20, kde=True, ax=ax4, color='orange', label='OS')

        ax4.set_xlabel('Fitness')

        ax4.legend()

        # set titles and labels for each subplot

        ax0.set_title(f'Sharpe Ratio Distribution in {region}')

        ax1.set_title(f'Turnover Distribution in {region}')

        ax2.set_title(f'Returns Distribution in {region}')

        ax3.set_title(f'Margin Distribution in {region}')

        ax4.set_title(f'Fitness Distribution in {region}')

        plt.tight_layout()

        plt.show()

    @staticmethod
    def get_month(alpha_list_submitted, month):
        """
        根据传入的开始日期和结束日期过滤数据框

        参数:
            alpha_list_submitted (pd.DataFrame): 包含日期数据的数据框
            startday (str): 开始日期字符串，格式为"YYYY-MM-DD"
            endday (str): 结束日期字符串，格式为"YYYY-MM-DD"

        返回:
            pd.DataFrame: 过滤后的数据框，包含指定日期范围内的数据
        """
        # 提取开始日期和结束日期的年月部分
        start = f'2025-{month}'
        end = f'2025-{month}'

        # 从数据框的日期列提取年月部分（前7个字符）
        df_range = alpha_list_submitted.copy()
        df_range['year_month'] = df_range['dateSubmitted'].str[:7]

        # 筛选在指定日期范围内的数据
        filtered_df = df_range[(df_range['year_month'] >= start) & (df_range['year_month'] <= end)]

        # 返回筛选后的数据（可选：移除临时列）
        return filtered_df.drop(columns=['year_month'])

    @staticmethod
    def plot_sharpe_vs_performance(sharpe_os, turnover_os, returns_os, margin_os, fitness_os, sharpe_is, turnover_is,
                                   returns_is, margin_is, fitness_is, region):
        # set up the figure and axes for the subplots

        fig = plt.figure(figsize=(15, 10))

        gs = gridspec.GridSpec(3, 2, height_ratios=[1, 1, 1], width_ratios=[1, 1])

        ax0 = fig.add_subplot(gs[0, 0])

        ax1 = fig.add_subplot(gs[0, 1])

        ax2 = fig.add_subplot(gs[1, 0])

        ax3 = fig.add_subplot(gs[1, 1])

        ax4 = fig.add_subplot(gs[2, :])

        # plot the scatter plots for each metric

        sns.scatterplot(x=sharpe_os, y=turnover_os, ax=ax0, color='orange', label='OS')

        sns.scatterplot(x=sharpe_is, y=turnover_is, ax=ax0, color='blue', label='IS')

        sns.regplot(x=sharpe_os, y=turnover_os, ax=ax0, scatter=False, color='orange')

        sns.regplot(x=sharpe_is, y=turnover_is, ax=ax0, scatter=False, color='blue')

        ax0.set_xlabel('Sharpe Ratio')

        ax0.set_ylabel('Turnover')

        ax0.legend()

        ax0.set_title(f'Sharpe Ratio vs Turnover in {region}')

        sns.scatterplot(x=sharpe_os, y=returns_os, ax=ax1, color='orange', label='OS')

        sns.scatterplot(x=sharpe_is, y=returns_is, ax=ax1, color='blue', label='IS')

        sns.regplot(x=sharpe_os, y=returns_os, ax=ax1, scatter=False, color='orange')

        sns.regplot(x=sharpe_is, y=returns_is, ax=ax1, scatter=False, color='blue')

        ax1.set_xlabel('Sharpe Ratio')

        ax1.set_ylabel('Returns')

        ax1.legend()

        ax1.set_title(f'Sharpe Ratio vs Returns in {region}')

        sns.scatterplot(x=sharpe_os, y=margin_os, ax=ax2, color='orange', label='OS')

        sns.scatterplot(x=sharpe_is, y=margin_is, ax=ax2, color='blue', label='IS')

        sns.regplot(x=sharpe_os, y=margin_os, ax=ax2, scatter=False, color='orange')

        sns.regplot(x=sharpe_is, y=margin_is, ax=ax2, scatter=False, color='blue')

        ax2.set_xlabel('Sharpe Ratio')

        ax2.set_ylabel('Margin')

        ax2.legend()

        ax2.set_title(f'Sharpe Ratio vs Margin in {region}')

        sns.scatterplot(x=sharpe_os, y=fitness_os, ax=ax3, color='orange', label='OS')

        sns.scatterplot(x=sharpe_is, y=fitness_is, ax=ax3, color='blue', label='IS')

        sns.regplot(x=sharpe_os, y=fitness_os, ax=ax3, scatter=False, color='orange')

        sns.regplot(x=sharpe_is, y=fitness_is, ax=ax3, scatter=False, color='blue')

        ax3.set_xlabel('Sharpe Ratio')

        ax3.set_ylabel('Fitness')

        ax3.legend()

        ax3.set_title(f'Sharpe Ratio vs Fitness in {region}')

        sns.scatterplot(x=sharpe_os, y=sharpe_is, ax=ax4, color='orange', label='OS')

        sns.scatterplot(x=sharpe_is, y=sharpe_is, ax=ax4, color='blue', label='IS')
        df = pd.DataFrame({'sharpe_os': sharpe_os, 'sharpe_is': sharpe_is})
        df = df.dropna(subset=['sharpe_os', 'sharpe_is'])
        sns.regplot(data=df, x='sharpe_os', y='sharpe_is', ax=ax4, scatter=False, color='orange')
        # sns.regplot(x=sharpe_os, y=sharpe_is, ax=ax4, scatter=False, color='orange')

        sns.regplot(x=sharpe_is, y=sharpe_is, ax=ax4, scatter=False, color='blue')

        ax4.set_xlabel('Sharpe Ratio OS')

        ax4.set_ylabel('Sharpe Ratio IS')

        ax4.legend()

        ax4.set_title(f'Sharpe Ratio OS vs Sharpe Ratio IS in {region}')

        plt.tight_layout()

        plt.show()

    @staticmethod
    def plot_sharpe_vs_performance_vs_month(sharpe_is2, turnover_is2, returns_is2, margin_is2, fitness_is2, sharpe_is1,
                                            turnover_is1, returns_is1, margin_is1, fitness_is1, region1, region2):
        # set up the figure and axes for the subplots

        fig = plt.figure(figsize=(15, 10))
        if len(sharpe_is1) == 0 or len(sharpe_is2) == 0:
            print("警告：没有足够数据绘制 regplot，跳过该图")
            return None

        gs = gridspec.GridSpec(3, 2, height_ratios=[1, 1, 1], width_ratios=[1, 1])

        ax0 = fig.add_subplot(gs[0, 0])

        ax1 = fig.add_subplot(gs[0, 1])

        ax2 = fig.add_subplot(gs[1, 0])

        ax3 = fig.add_subplot(gs[1, 1])

        ax4 = fig.add_subplot(gs[2, :])

        # plot the scatter plots for each metric

        sns.scatterplot(x=sharpe_is2, y=turnover_is2, ax=ax0, color='orange', label=f'{region2}')

        sns.scatterplot(x=sharpe_is1, y=turnover_is1, ax=ax0, color='blue', label=f'{region1}')

        sns.regplot(x=sharpe_is2, y=turnover_is2, ax=ax0, scatter=False, color='orange')

        sns.regplot(x=sharpe_is1, y=turnover_is1, ax=ax0, scatter=False, color='blue')

        ax0.set_xlabel('Sharpe Ratio')

        ax0.set_ylabel('Turnover')

        ax0.legend()

        ax0.set_title(f'Sharpe Ratio vs Turnover in {region1}vs{region2}')

        sns.scatterplot(x=sharpe_is2, y=returns_is2, ax=ax1, color='orange', label=f'{region2}')

        sns.scatterplot(x=sharpe_is1, y=returns_is1, ax=ax1, color='blue', label=f'{region1}')

        sns.regplot(x=sharpe_is2, y=returns_is2, ax=ax1, scatter=False, color='orange')

        sns.regplot(x=sharpe_is1, y=returns_is1, ax=ax1, scatter=False, color='blue')

        ax1.set_xlabel('Sharpe Ratio')

        ax1.set_ylabel('Returns')

        ax1.legend()

        ax1.set_title(f'Sharpe Ratio vs Returns in {region1}vs{region2}')

        sns.scatterplot(x=sharpe_is2, y=margin_is2, ax=ax2, color='orange', label=f'{region2}')

        sns.scatterplot(x=sharpe_is1, y=margin_is1, ax=ax2, color='blue', label=f'{region1}')

        sns.regplot(x=sharpe_is2, y=margin_is2, ax=ax2, scatter=False, color='orange')

        sns.regplot(x=sharpe_is1, y=margin_is1, ax=ax2, scatter=False, color='blue')

        ax2.set_xlabel('Sharpe Ratio')

        ax2.set_ylabel('Margin')

        ax2.legend()

        ax2.set_title(f'Sharpe Ratio vs Margin in {region1}vs{region2}')

        sns.scatterplot(x=sharpe_is2, y=fitness_is2, ax=ax3, color='orange', label=f'{region2}')

        sns.scatterplot(x=sharpe_is1, y=fitness_is1, ax=ax3, color='blue', label=f'{region1}')

        sns.regplot(x=sharpe_is2, y=fitness_is2, ax=ax3, scatter=False, color='orange')

        sns.regplot(x=sharpe_is1, y=fitness_is1, ax=ax3, scatter=False, color='blue')

        ax3.set_xlabel('Sharpe Ratio')

        ax3.set_ylabel('Fitness')

        ax3.legend()

        ax3.set_title(f'Sharpe Ratio vs Fitness in {region1}vs{region2}')

        sns.scatterplot(x=sharpe_is2, y=sharpe_is1, ax=ax4, color='orange', label=f'{region2}')

        sns.scatterplot(x=sharpe_is1, y=sharpe_is1, ax=ax4, color='blue', label=f'{region1}')

        sns.regplot(x=sharpe_is2, y=sharpe_is1, ax=ax4, scatter=False, color='orange')

        sns.regplot(x=sharpe_is1, y=sharpe_is1, ax=ax4, scatter=False, color='blue')

        ax4.set_xlabel('Sharpe')

        ax4.set_ylabel('Sharpe')

        ax4.legend()

        ax4.set_title(f'Sharpe Ratio OS vs Sharpe Ratio IS in month{region1}vs month{region2}')

        plt.tight_layout()

        plt.show()


if __name__ == '__main__':
    Brain = BrainTools()
    alpha_list_submitted = Brain.get_n_os_alphas(3000)

    df_alpha_list_submitted = pd.DataFrame(alpha_list_submitted)
    print(df_alpha_list_submitted.head())

    # months = [ '01', '02', '03', '04', '05', '06', '07','08', '09', '10', '11', '12']
    # 获取不同的month，画出不同的month的performance
    # months = ["07"]
    # for month in months:
    #     df_month = DearBrainJson.get_month(df_alpha_list_submitted, month)
    #     df_is_performance = DearBrainJson.get_performance(df_month, 'is')
    #     df_os_performance = DearBrainJson.get_performance(df_month, 'os')
    #     sharpe_os, turnover_os, returns_os, margin_os, fitness_os, _, _ = DearBrainJson.get_performance_metrics(df_os_performance)
    #     sharpe_is, turnover_is, returns_is, margin_is, fitness_is, _, _ = DearBrainJson.get_performance_metrics(df_is_performance)
    #
    #     # 调用绘图函数
    #     DearBrainJson.plot_sharpe_vs_performance(sharpe_os, turnover_os, returns_os, margin_os, fitness_os,
    #                                sharpe_is, turnover_is, returns_is, margin_is, fitness_is, month)
    #
    # month_pairs = [
    #     ('01', '02'), ('02', '03'), ('03', '04'),
    #     ('04', '05'), ('05', '06'), ('06', '07'),
    #     ('07', '08'), ('08', '09'), ('09', '10')
    # ]
    # month_pairs = [
    #     ('01', '02'), ('02', '03'), ('03', '04'),
    #     ('04', '05'), ('05', '06'),
    #     ('06', '07'),
    #     ('07', '08'),
    #     ('08', '09'), ('09', '10')
    # ]
    # # 对每一对月份进行对比分析
    # for month1, month2 in month_pairs:
    #     try:
    #         # 获取两个月份的数据
    #         df_month1 = DearBrainJson.get_month(df_alpha_list_submitted, month1)
    #         df_month2 = DearBrainJson.get_month(df_alpha_list_submitted, month2)
    #
    #         # 获取两个月份的IS和OS绩效数据
    #         df_is_performance1 = DearBrainJson.get_performance(df_month1, 'is')
    #         df_os_performance1 = DearBrainJson.get_performance(df_month1, 'os')
    #         sharpe_os1, turnover_os1, returns_os1, margin_os1, fitness_os1, selfcorrelation_os1, prodcorrelation_os1 = DearBrainJson.get_performance_metrics(
    #             df_os_performance1)
    #         sharpe_is1, turnover_is1, returns_is1, margin_is1, fitness_is1, selfcorrelation_is1, prodcorrelation_is1 = DearBrainJson.get_performance_metrics(
    #             df_is_performance1)
    #
    #         df_is_performance2 = DearBrainJson.get_performance(df_month2, 'is')
    #         df_os_performance2 = DearBrainJson.get_performance(df_month2, 'os')
    #         sharpe_os2, turnover_os2, returns_os2, margin_os2, fitness_os2, selfcorrelation_os2, prodcorrelation_os2 = DearBrainJson.get_performance_metrics(
    #             df_os_performance2)
    #         sharpe_is2, turnover_is2, returns_is2, margin_is2, fitness_is2, selfcorrelation_is2, prodcorrelation_is2 = DearBrainJson.get_performance_metrics(
    #             df_is_performance2)
    #         # 调用绘图函数
    #         DearBrainJson.plot_sharpe_vs_performance_vs_month(sharpe_is2, turnover_is2, returns_is2, margin_is2,
    #                                                           fitness_is2,
    #                                                           sharpe_is1, turnover_is1, returns_is1, margin_is1,
    #                                                           fitness_is1, month1,
    #                                                           month2)
    #     except ValueError as ve:
    #         # 特别处理维度不匹配错误
    #         print(f"ValueError in month {month1}: {str(ve)}. Skipping this month.")
    #     except Exception as e:
    #         print(f"Unexpected error in month {month1}: {str(e)}. Skipping this month.")
    #     else:
    #         print(f"Successfully plotted for month {month1}")
    # exit()

    # """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    # %%
    # 定义月份对比关系
    month_pairs = [
        ('01', '04'), ('02', '05'), ('03', '06'),
        ('04', '07'), ('05', '08'), ('06', '09'),
        ('07', '10'), ('08', '11'), ('09', '12')
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
        sns.histplot(sharpe_is1, bins=20, kde=True, ax=axes[0, 0], color='blue', label=f'Month {month1}')
        sns.histplot(sharpe_is2, bins=20, kde=True, ax=axes[0, 0], color='red', label=f'Month {month2}')
        axes[0, 0].set_title('Sharpe Ratio Distribution')
        axes[0, 0].legend()

        # Turnover 对比
        sns.histplot(turnover_is1, bins=20, kde=True, ax=axes[0, 1], color='blue', label=f'Month {month1}')
        sns.histplot(turnover_is2, bins=20, kde=True, ax=axes[0, 1], color='red', label=f'Month {month2}')
        axes[0, 1].set_title('Turnover Distribution')
        axes[0, 1].legend()

        # Returns 对比
        sns.histplot(returns_is1, bins=20, kde=True, ax=axes[1, 0], color='blue', label=f'Month {month1}')
        sns.histplot(returns_is2, bins=20, kde=True, ax=axes[1, 0], color='red', label=f'Month {month2}')
        axes[1, 0].set_title('Returns Distribution')
        axes[1, 0].legend()

        # Margin 对比
        sns.histplot(margin_is1, bins=20, kde=True, ax=axes[1, 1], color='blue', label=f'Month {month1}')
        sns.histplot(margin_is2, bins=20, kde=True, ax=axes[1, 1], color='red', label=f'Month {month2}')
        axes[1, 1].set_title('Margin Distribution')
        axes[1, 1].legend()

        # Fitness 对比
        sns.histplot(fitness_is1, bins=20, kde=True, ax=axes[2, 0], color='blue', label=f'Month {month1}')
        sns.histplot(fitness_is2, bins=20, kde=True, ax=axes[2, 0], color='red', label=f'Month {month2}')
        axes[2, 0].set_title('Fitness Distribution')
        axes[2, 0].legend()
        # Self-Correlation 对比
        sns.histplot(selfcorrelation_is1, bins=20, kde=True, ax=axes[2, 1], color='blue', label=f'Month {month1}')
        sns.histplot(selfcorrelation_is2, bins=20, kde=True, ax=axes[2, 1], color='red', label=f'Month {month2}')
        axes[2, 1].set_title('Self-Correlation Distribution')
        axes[2, 1].legend()
        # Prod-Correlation 对比
        sns.histplot(prodcorrelation_is1, bins=20, kde=True, ax=axes[3, 0], color='blue', label=f'Month {month1}')
        sns.histplot(prodcorrelation_is2, bins=20, kde=True, ax=axes[3, 0], color='red', label=f'Month {month2}')
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
