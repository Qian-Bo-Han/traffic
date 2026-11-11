import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def run(data_folder):
    df_task3=pd.read_csv(data_folder / "003merged_data.csv")
    df_task3['date']=pd.to_datetime(df_task3['date'],errors='coerce')
    target_grids=['G0001', 'G0002', 'G0003']
    df_filtered = df_task3[df_task3['grid_id'].isin(target_grids)].sort_values(by=['grid_id','date']).copy()
    all_results = []
    for grid in target_grids:
        df_grid = df_filtered[df_filtered['grid_id']==grid].copy()
        df_grid['day_num']=range(1,len(df_grid) +1)
        train_set = df_grid[(df_grid['date'] >= '2024-01-01') & (df_grid['date'] <= '2024-03-24')]
        test_set = df_grid[(df_grid['date'] >= '2024-03-25') & (df_grid['date'] <= '2024-03-31')].copy()
        X_train=train_set['day_num'].values.reshape(-1,1)
        y_train=train_set['demand_start'].values
        X_test=test_set['day_num'].values.reshape(-1,1)
        y_test=test_set['demand_start'].values
        model=LinearRegression()
        model.fit(X_train,y_train) # 喂数据给模型，让它找规律画直线
        predictions = model.predict(X_test) # 吐出未来 7 天的预测值
        rmse_value=np.sqrt(np.mean((y_test - predictions) ** 2))
        test_set['actual'] = y_test
        test_set['forecast'] = predictions
        test_set['rmse'] = rmse_value
        final_cols=['grid_id', 'date', 'actual', 'forecast', 'rmse']
        all_results.append(test_set[final_cols])
    df_008 = pd.concat(all_results,ignore_index=True)
    df_008.to_csv(data_folder / "008forecast_results.csv", index=False)
