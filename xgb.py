import pandas as pd
import xgboost as xgb
from sklearn.preprocessing import MinMaxScaler


def get_processed_dataset():
    #导入数据集
    #dataset1: 训练集1
    #dataset2: 训练集2
    #dataset3: 测试集
    dataset1 = pd.read_csv('dataset1.csv')
    dataset2 = pd.read_csv('dataset2.csv')
    dataset3 = pd.read_csv('dataset3.csv')

    dataset1['Label'].replace(-1,0,inplace=True)
    dataset2['Label'].replace(-1,0,inplace=True)

    # 删除重复项
    dataset1.drop_duplicates(inplace=True)
    dataset2.drop_duplicates(inplace=True)
    dataset3.drop_duplicates(inplace=True)


    #将dataset1和dataset2连起来
    dataset12 = pd.concat([dataset1, dataset2], axis=0)

    print("dataset1 info")
    print(dataset1.info())
    print("dataset2 info")
    print(dataset2.info())
    print("dataset3 info")
    print(dataset3.info())
    print("dataset12 info")
    print(dataset12.info())

    #如果碰到空值就转换成0
    #--------------------------------这一步不知道需不需要
    dataset12.fillna(0, inplace=True)
    dataset3.fillna(0, inplace=True)

    return dataset1, dataset2,dataset3,dataset12


def train_xgb(dataset1,dataset2, dataset3,dataset12):
    # dataset1_y, dataset2_y, dataset12_y赋值为dataset1, dataset2, dataset12_y的Label列
    dataset1_y = dataset1.Label
    dataset2_y = dataset2.Label
    dataset12_y = dataset12.Label
    # 删除dataset1, dataset2, dataset12的’User_id’, ’Label’, ’day_gap_before’, ’day_gap_after’字段，赋值给dataset1_x, dataset2_x, dataset12_x
    dataset1_x = dataset1.drop(columns = ['User_id', 'Label', 'day_gap_before', 'day_gap_after'], axis=1)
    dataset2_x = dataset2.drop(columns = ['User_id', 'Label', 'day_gap_before', 'day_gap_after'], axis=1)
    dataset12_x = dataset12.drop(columns = ['User_id', 'Label', 'day_gap_before', 'day_gap_after'], axis=1)
    # 复制dataset3的'User_id', 'Coupon_id', 'Date_received'这三列，拷贝给dataset3_preds
    dataset3_preds = dataset3[['User_id', 'Coupon_id', 'Date_received']].copy()
    # 删除dataset3的'User_id', 'Coupon_id', 'Date_received', 'day_gap_before', 'day_gap_after'，赋值给dataset3_x
    dataset3_x = dataset3.drop(columns = ['User_id', 'Coupon_id', 'Date_received', 'day_gap_before', 'day_gap_after','Date'], axis=1)

    #加载数据到xgboost

    dataset1 = xgb.DMatrix(dataset1_x, label=dataset1_y)
    dataset2 = xgb.DMatrix(dataset2_x, label=dataset2_y)
    dataset12 = xgb.DMatrix(dataset12_x, label=dataset12_y)
    dataset3 = xgb.DMatrix(dataset3_x)

    # xgboost模型训练
    params = {'booster': 'gbtree',
              'objective': 'rank:pairwise',
              'eval_metric': 'auc',
              'gamma': 0.1,
              'min_child_weight': 1.1,
              'max_depth': 5,
              'lambda': 10,
              'subsample': 0.7,
              'colsample_bytree': 0.7,
              'colsample_bylevel': 0.7,
              'eta': 0.01,
              'tree_method': 'exact',
              'seed': 0,
              'nthread': 12 #nthread默认值为最大可能的线程数, 这个参数用来进行多线程控制
              }

    # 训练模型



    watchlist = [(dataset12, 'train')]
    model = xgb.train(params, dataset12, num_boost_round = 100, evals = watchlist)

    # 第一名的num_boost_round是直接设定为3500，下面这种计算了最优的num_boost_round
    # # 使用xgb.cv优化num_boost_round参数
    # cvresult = xgb.cv(params, train_dmatrix, num_boost_round=10000, nfold=2, metrics='auc', seed=0, callbacks=[
    #     xgb.callback.print_evaluation(show_stdv=False),
    #     xgb.callback.early_stop(50)
    # ])
    # num_round_best = cvresult.shape[0] - 1
    #print('Best round num: ', num_round_best)
    # # 使用优化后的num_boost_round参数训练模型
    # watchlist = [(dataset12, 'train')]
    # model = xgb.train(params, dataset12, num_boost_round=num_round_best, evals=watchlist)

    print("begin to predict")
    # 使用上述模型预测测试集
    dataset3_preds['Label'] = model.predict(dataset3)
    # 标签归一化（Sklearn的MinMaxScaler，最简单的归一化）
    dataset3_preds.Label = MinMaxScaler(copy = True, feature_range = (0, 1)).fit_transform(dataset3_preds.Label.values.reshape(-1, 1))
    # 对数据进行排序，用到了sort_values，by参数可以指定根据哪一列数据进行排序，
    # ascending是设置升序和降序（选择多列或者多行排序要加[ ]，把选择的行列转换为列表，排序方式也可以同样的操作）
    dataset3_preds.sort_values(by = ['Coupon_id', 'Label'], inplace = True)
    #将结果保存在当前工作路径下
    dataset3_preds.to_csv("xgb_preds.csv", index = None, header = None)
    # print(dataset3_preds.describe()) #打印dataset3_preds


dataset1,dataset2,dataset3,dataset12 = get_processed_dataset()
train_xgb(dataset1,dataset2,dataset3,dataset12)