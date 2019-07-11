import pandas as pd
import numpy as numpy

#读入文件，输出文件概览信息
data_off_train = pd.read_csv("ccf_offline_stage1_train.csv")
data_on_train = pd.read_csv("ccf_online_stage1_train.csv")
data_test = pd.read_csv("ccf_offline_stage1_test_revised.csv")
print("Finish reading data.")
print("offline")
print(data_off_train.head(10))
print(data_off_train.info())
print("online")
print(data_on_train.head(10))
print(data_on_train.info())

#统计单个条目信息
print("User amount:",len(set(data_off_train['User_id'])))
print("Merchant amount:",len(set(data_off_train['Merchant_id'])))
print("Coupon type amount:",len(set(data_off_train['Coupon_id'])))

