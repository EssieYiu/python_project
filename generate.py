import pandas as pd
import numpy as np
from datetime import date
import math

def get_label(s):
    s = s.split(':')
    if s[0]=='null':
        return 0
    elif (date(int(s[0][0:4]),int(s[0][4:6]),int(s[0][6:8]))-date(int(s[1][0:4]),int(s[1][4:6]),int(s[1][6:8]))).days<=15:
        return 1
    else:
        return -1

# Merge data
def merge_data(file1, file2, file3, file4, file5):
    coupon = pd.read_csv(file1)
    merchant = pd.read_csv(file2)
    user = pd.read_csv(file3)
    user_merchant = pd.read_csv(file4)
    other_feature = pd.read_csv(file5)

    dataset = pd.merge(coupon,merchant,on='Merchant_id',how='left')
    dataset = pd.merge(dataset,user,on='User_id',how='left')
    dataset = pd.merge(dataset,user_merchant,on=['User_id','Merchant_id'],how='left')
    dataset = pd.merge(dataset,other_feature,on=['User_id','Coupon_id','Date_received'],how='left')
    dataset.drop_duplicates(inplace=True)
    #print(dataset.shape)
    return dataset

# Label and Drop
def data_process(dataset, is_train):
    if is_train:
        dataset['Date'] = dataset['Date'].fillna('null')
        dataset['Label'] = dataset.Date.astype('str') + ':' + dataset.date_received.astype('str')
        dataset.Label = dataset.Label.apply(get_label)
        dataset.drop(['Merchant_id', 'Date', 'Date_received', 'Coupon_id'], axis=1, inplace=True)
    else:
        dataset.drop(['Merchant_id'], axis=1, inplace=True)
    dataset = dataset.replace('null',np.nan)
    return dataset


dataset1 = data_process(merge_data('coupon_feature1.csv','merchant_feature1.csv','user_feature1.csv','user_merchant_feature1.csv','other_feature1.csv'),True)
dataset2 = data_process(merge_data('coupon_feature2.csv','merchant_feature2.csv','user_feature2.csv','user_merchant_feature2.csv','other_feature2.csv'),True)
dataset3 = data_process(merge_data('coupon_feature3.csv','merchant_feature3.csv','user_feature3.csv','user_merchant_feature3.csv','other_feature3.csv'),False)

dataset1.to_csv('dataset1.csv',index=None)
dataset2.to_csv('dataset2.csv',index=None)
dataset3.to_csv('dataset3.csv',index=None)
