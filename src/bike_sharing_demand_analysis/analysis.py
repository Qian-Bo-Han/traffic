import pandas as pd
from sklearn.cluster import KMeans


def run(data_folder):
    df_task3 = pd.read_csv(data_folder / "003merged_data.csv")
    df_task3['net_dispatch']=df_task3['dispatch_in']-df_task3['dispatch_out']
    df_task3['gap_index']=df_task3['demand_start']-(df_task3['demand_end']+df_task3['net_dispatch'])
    df_task3['date']=pd.to_datetime(df_task3['date'])
    df_005=(df_task3['date']>='2024-01-01') & (df_task3['date']<='2024-03-31')
    df_005=df_task3.loc[df_005].groupby(['district']).agg(mean_demand_start=('demand_start','mean'),
                                                std_demand_start=('demand_start','std'),
                                                min_demand_start=('demand_start','min'),
                                                max_demand_start=('demand_start','max'),
                                                mean_gap_index=('gap_index','mean'),
                                                std_gap_index=('gap_index','std'),
                                                min_gap_index=('gap_index','min'),
                                                max_gap_index=('gap_index','max'),
                                                mean_peak_ratio=('peak_ratio','mean'),
                                                std_peak_ratio=('peak_ratio','std'),
                                                min_peak_ratio=('peak_ratio','min'),
                                                max_peak_ratio=('peak_ratio','max')).reset_index()
    save_path = data_folder / "005descriptive_stats.csv"
    df_005.to_csv(save_path, index=False)

    df_task3=pd.read_csv(data_folder / "003merged_data.csv")
    df_task3['slope']=df_task3.groupby('district')['demand_start'].pct_change(fill_method=None)
    df_006=df_task3[['district','slope']]
    save_path = data_folder / "006district_trend.csv"
    df_006.to_csv(save_path,index=False)

    df_task3=pd.read_csv(data_folder / "003merged_data.csv")
    df_corr=df_task3.groupby('district')[['rain_mm','demand_start']].corr()
    df_res = df_corr.reset_index()
    df_007 = df_res[df_res['level_1'] == 'rain_mm'][['district', 'demand_start']]
    df_007.columns = ['district', 'correlation']
    save_path = data_folder / "007correlation.csv"
    df_007.to_csv(save_path,index=False)

    df_task3=pd.read_csv(data_folder / "003merged_data.csv")
    df_task3['date']=pd.to_datetime(df_task3['date'],errors='coerce')
    df_1=df_task3[df_task3['date']=='2024-01-01'][['grid_id', 'gap_index', 'net_dispatch']]
    df_31=df_task3[df_task3['date']=='2024-03-31'][['grid_id', 'gap_index', 'net_dispatch']]
    df_merged=pd.merge(df_31,df_1,on='grid_id',suffixes=('_31', '_1'))
    df_merged['change']=df_merged['gap_index_31']-df_merged['gap_index_1']
    df_merged['net_dispatch_change']=df_merged['net_dispatch_31']-df_merged['net_dispatch_1']
    df_012=df_merged.sort_values(by='change',ascending=True).head(5)
    df_012=df_012[['grid_id', 'change', 'net_dispatch_change']]
    save_path = data_folder / "012top_reduction.csv"
    df_012.to_csv(save_path,index=False)

    df_task3=pd.read_csv(data_folder / "003merged_data.csv")
    df_task4=pd.read_csv(data_folder / "004processed_data.csv")
    features=['demand_start_zscore', 'demand_growth_rate_zscore', 'gap_index_zscore']
    df_task4_clean = df_task4.dropna(subset=features).copy()
    X = df_task4_clean[features]
    kmeans=KMeans(
    n_clusters=4,            # 题目要求聚成 4 个簇（分 4 个门派）
        init="k-means++",    # 默认最佳的初始点选择算法
        n_init=10,           # 让机器人重复实验 10 次，挑出效果最好的一次
        max_iter=300,        # 最多让它迭代调整 300 次
        tol=1e-4,            # 收敛阈值，当变化极小时就提前停止
        random_state=42
    )
    df_task4_clean['cluster_label'] = kmeans.fit_predict(X)
    df_analysis = df_task4_clean
    df_analysis_clean = df_analysis.dropna(subset=['cluster_label']).copy()
    df_summary = df_analysis_clean.groupby('cluster_label').agg(
        avg_demand_start=('demand_start', 'mean'),  # 算 demand_start 的平均值
        avg_gap_index=('gap_index', 'mean'),        # 算 gap_index 的平均值
        avg_peak_ratio=('peak_ratio', 'mean'),      # 算 peak_ratio 的平均值
        grid_count=('grid_id', 'nunique')             # 顺便数一下这个门派一共有多少个网格
    ).reset_index()  # 恢复表头，让表格整齐
    df_summary.to_csv(data_folder / "013cluster_summary.csv", index=False)
