import matplotlib
import pandas as pd

matplotlib.use('Agg')
import matplotlib.pyplot as plt


def run(data_folder):
    df_task4=pd.read_csv(data_folder / "004processed_data.csv")
    df_009=df_task4.groupby(['date']).agg(total_demand_start=('demand_start','sum'),
                                          avg_gap_index=('gap_index','mean')).reset_index()
    save_path = data_folder / "009global_trends.csv"
    df_009.to_csv(save_path,index=False)
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    fig,ax1=plt.subplots(figsize=(12,6))
    ax2=ax1.twinx()
    x = df_009['date']
    y1 = df_009['total_demand_start']
    y2 = df_009['avg_gap_index']
    ax1.set_title('每日全市总需求与平均缺口指标趋势', fontsize=16, pad=20)
    ax1.set_xlabel('日期')
    ax1.set_ylabel('全市总需求 (total_demand_start)',color='blue')
    ax2.set_ylabel('平均缺口指标 (avg_gap_index)', color='red')
    lns1=ax1.plot(x,y1,color='blue',marker='o',label='全市总需求')
    lns2=ax2.plot(x,y2,color='red',marker='o',label='平均缺口指标')
    lns=lns1+lns2
    labs=[l.get_label() for l in lns]
    ax1.legend(lns,labs,loc='upper left')
    ax1.set_xticks(range(0, len(x), 15))
    ax1.set_xticklabels(x[::15], rotation=45, ha='right')
    ax1.grid(True, linestyle='--', alpha=0.3)
    ax1.set_axisbelow(True)  # 网格线沉底，不穿过折线
    plt.tight_layout()
    save_img_path = data_folder / "global_trends.png"
    plt.savefig(save_img_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

    df_task3=pd.read_csv(data_folder / "003merged_data.csv")
    df_task3['date']=pd.to_datetime(df_task3['date'],errors='coerce')
    df_010=df_task3[df_task3['date']=='2024-03-31'].copy()
    df_010['bubble_size'] = df_010['demand_start']
    df_010=df_010[['grid_id','date','district','lng','lat','demand_start','gap_index','bubble_size']]
    save_path = data_folder / "010map_data.csv"
    df_010.to_csv(save_path,index=False)
    fig,ax=plt.subplots(figsize=(10,8))
    sc=ax.scatter(df_010['lng'],
                  df_010['lat'],
                  s=df_010['bubble_size'] * 100,
                  c=df_010['gap_index'],
                  cmap='Reds',
                  alpha=0.6,
                  edgecolors="grey"
                 )
    cbar =plt.colorbar(sc)
    cbar.set_label('供需缺口指数 (gap_index)')
    ax.set_title('2024-03-31 网格需求与缺口气泡图', fontsize=14, pad=15)
    ax.set_xlabel('经度(lng)')
    ax.set_ylabel('纬度(lat)')
    plt.tight_layout()
    plt.savefig(data_folder / "map_2024.png", dpi=300, bbox_inches='tight')
    plt.close(fig)

    df_task3=pd.read_csv(data_folder / "003merged_data.csv")
    df_task3['date']=pd.to_datetime(df_task3['date'],errors='coerce')
    grid_list=['G0001', 'G0002', 'G0003']
    df_task3=df_task3[df_task3['grid_id'].isin(grid_list)]
    df_011=df_task3[(df_task3['date']>='2024-01-01') & (df_task3['date']<='2024-03-31')].copy()
    df_011=df_011[['grid_id','date','demand_start','gap_index','district']]
    save_path = data_folder / "011combo_data.csv"
    df_011.to_csv(save_path,index=False)
    fig,ax1=plt.subplots(figsize=(12,6))
    ax2=ax1.twinx()
    x=df_011['date']
    y1=df_011['demand_start']
    y2=df_011['gap_index']
    ax1.set_title('G0001/G0002/G0003 : 2024-01-01 至 2024-03-31 需求与缺口双轴折线图')
    ax1.set_xlabel('日期')
    ax1.set_ylabel('需求量 (demand_start)',color='blue')
    ax2.set_ylabel('供需缺口指数 (gap_index)',color='red')
    colors={'G0001':'blue','G0002':'green','G0003':'orange'}
    for grid in ['G0001','G0002','G0003']:
        df_temp = df_011[df_011['grid_id'] == grid]
        c=colors[grid]
        ax1.plot(df_temp['date'],df_temp['demand_start'],
                 color=c,marker='o',linestyle='-',label=f'{grid}demand_start')
        ax2.plot(df_temp['date'],df_temp['gap_index'],
                 color=c,marker='o',linestyle='--',label=f'{grid}gap_index')
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    lines = lines1 + lines2
    labels = labels1 + labels2
    ax1.legend(lines, labels, loc='upper left')
    ax1.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()
    save_img_path = data_folder / "combo_chart.png"
    plt.savefig(save_img_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
