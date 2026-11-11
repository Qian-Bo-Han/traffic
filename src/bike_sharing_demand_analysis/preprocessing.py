import numpy as np
import pandas as pd


def run(data_folder):
    raw_dir = data_folder.parent / "data" / "raw"
    df_trips = pd.read_csv(raw_dir / "trips.csv")
    df_grids = pd.read_csv(raw_dir / "grids.csv")
    df_weather = pd.read_csv(raw_dir / "weather.csv").sort_values("date")
    df_ops = pd.read_csv(raw_dir / "ops.csv")

    res1=df_trips.isnull().sum().reset_index()
    res2=df_weather.isnull().sum().reset_index()
    res3=df_ops.isnull().sum().reset_index()
    df=pd.concat([res1,res2,res3])
    df.columns=['columns','missing_columns']
    save_path = data_folder / "001cleaned_data.csv"
    df.to_csv(save_path, index=False)

    cols=['temp_c','rain_mm','wind_ms']
    df_weather[cols]=df_weather[cols].interpolate(limit_direction='both')
    cols1=['dispatch_in','dispatch_out']
    df_ops[cols1]=df_ops[cols1].fillna(0).astype(int)
    cols2=['end_time','distance_km']
    df_trips=df_trips.dropna(subset=cols2).copy()
    df_trips['start_time']=pd.to_datetime(df_trips['start_time'])
    df_trips['end_time']=pd.to_datetime(df_trips['end_time'])
    df_trips['duration_min'] = (df_trips['end_time'] - df_trips['start_time']).dt.total_seconds()/60
    df_trips=df_trips[(df_trips['duration_min'] >0) & (df_trips['duration_min'] <= 180)]
    df_trips=df_trips[(df_trips['distance_km'] >0) & (df_trips['distance_km'] <= 30)]
    # 与天气和调度表使用相同的 YYYY-MM-DD 日期键。
    df_trips['date'] = df_trips['start_time'].dt.strftime('%Y-%m-%d')
    df_trips['hour']=df_trips['start_time'].dt.hour
    target_cols = ['trip_id', 'start_time', 'end_time', 'start_grid', 'end_grid', 'distance_km', 'date', 'hour', 'duration_min']
    df_trips_final = df_trips[target_cols]
    save_path = data_folder / "002cleaned_data.csv"
    df_trips_final.to_csv(save_path, index=False)

    df_task2 = df_trips_final.copy()
    df_task2['start_time']=pd.to_datetime(df_task2['start_time'])
    df_task2['end_time']=pd.to_datetime(df_task2['end_time'])
    df_task2['duration_min']=(df_task2['end_time']-df_task2['start_time']).dt.total_seconds() / 60
    df_task2['is_peak']=df_task2['hour'].apply(lambda x : 1 if (7<=x<=9) or (17<=x<=19) else 0)
    df_start=df_task2.groupby(['start_grid','date']).agg(
        demand_start=('start_time','count'),
        avg_distance_km=('distance_km','mean'),
        avg_duration_min=('duration_min','mean'),
        peak_ratio=('is_peak','mean')# 这个 mean 出来的就是占比
       ).reset_index().rename(columns={'start_grid':'grid_id'})
    df_end=df_task2.groupby(['end_grid','date']).agg(demand_end=('end_time','count')
            ).reset_index().rename(columns={'end_grid': 'grid_id'})
    df_md=pd.merge(df_start,df_end,on=['grid_id','date'],how='outer')
    df_md=pd.merge(df_md,df_grids,on='grid_id',how='left')
    df_md=pd.merge(df_md,df_weather,on='date',how='left')
    df_md=pd.merge(df_md,df_ops,on=['date','grid_id'],how='left')
    zero_cols = ['demand_start', 'demand_end', 'peak_ratio', 'dispatch_in', 'dispatch_out']
    df_md[zero_cols] = df_md[zero_cols].fillna(0)
    df_md['avg_distance_km'] = df_md['avg_distance_km'].fillna(0)
    df_md['avg_duration_min'] = df_md['avg_duration_min'].fillna(0)

    df_task3 = df_md.copy()
    df_task3['net_dispatch']=df_task3['dispatch_in']-df_task3['dispatch_out']
    df_task3['gap_index']=df_task3['demand_start']-(df_task3['demand_end']+df_task3['net_dispatch'])
    df_task3=df_task3.sort_values(by=['grid_id','date'],ascending=True)
    df_task3['demand_growth_rate']=df_task3.groupby('grid_id')['demand_start'].pct_change(fill_method=None)
    df_task3['demand_growth_rate']=df_task3['demand_growth_rate'].replace([np.inf,-np.inf],0)
    save_path = data_folder / "003merged_data.csv"
    df_task3.to_csv(save_path, index=False)
    ddg = ['demand_start','demand_growth_rate','gap_index']
    for col in ddg:
        mean=df_task3.groupby('grid_id')[col].transform('mean')
        std=df_task3.groupby('grid_id')[col].transform('std')
        df_task3[f'{col}_zscore']=(df_task3[col]-mean)/std
    save_path = data_folder / "004processed_data.csv"
    df_task3.to_csv(save_path, index=False)
