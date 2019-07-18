import pandas as pd
import numpy as np
from datetime import date
import math

def get_label(s):
    print("debug:",s)
    s = s.split(':')
    if s[0][0]=='-':
        print("null return0")
        return 0
    elif s[1][0] =='-':
        print("return-1")
        return -1
    elif (date(int(s[0][0:4]),int(s[0][4:6]),int(s[0][6:8]))-date(int(s[1][0:4]),int(s[1][4:6]),int(s[1][6:8]))).days<=15:
        print("positive sample")
        return 1
    else:
        return -1
# Merge data
def merge_data(file1, file2, file3, file4, file5,is_train):
    coupon = pd.read_csv(file1,index_col=0,header=0)
    merchant = pd.read_csv(file2,index_col=0,header=0)
    user = pd.read_csv(file3,index_col=0,header=0)
    user_merchant = pd.read_csv(file4,index_col=0,header=0)
    other_feature = pd.read_csv(file5,index_col=0,header=0)
    '''
    dataset = pd.merge(user,user_merchant,on='User_id',how='left')
    dataset = pd.merge(dataset,merchant,on='Merchant_id',how='left')
    dataset = pd.merge(dataset,coupon,on=['User_id','Merchant_id'],how='left')
    dataset = pd.merge(dataset,other_feature,on=['User_id','Coupon_id','Date_received'],how='left')

    '''
    dataset = pd.merge(coupon,merchant,on='Merchant_id',how='left')
    print("coupon merge merchant")
    print(dataset.info())
    dataset = pd.merge(dataset,user,on='User_id',how='left')
    print("merge user")
    print(dataset.info())
    dataset = pd.merge(dataset,user_merchant,on=['User_id','Merchant_id'],how='left')
    print("merge user-merchant")
    print(dataset.info())
    if is_train:
        dataset = pd.merge(dataset,other_feature,on=['User_id','Coupon_id','Date_received'],how='left')
    else:
        dataset = pd.merge(dataset,other_feature,on=['User_id','Coupon_id','Date_received'],how='left')
    print("merge other")
    print(dataset.info())
    dataset.drop_duplicates(inplace=True)
    print("drop duplicates")
    print(dataset.info())
    #print(dataset.shape)
    return dataset

# Label and Drop
def data_process(dataset, is_train):
    if is_train:
        dataset['Date'] = dataset['Date'].fillna(-1)
        dataset['Label'] = dataset.Date.astype('str') + ':' + dataset.Date_received.astype('str')
        dataset.Label = dataset.Label.apply(get_label)
        dataset.drop(['Merchant_id', 'Date', 'Date_received', 'Coupon_id','Discount_rate'], axis=1, inplace=True)
    else:
        dataset.drop(['Merchant_id','Discount_rate'], axis=1, inplace=True)
    dataset = dataset.fillna(-1)
    return dataset

dataset1 = merge_data('coupon_feature1.csv','merchant_feature1.csv','user_feature1.csv','user_merchant_feature1.csv','other_feature1.csv',True)
dataset2 = merge_data('coupon_feature2.csv','merchant_feature2.csv','user_feature2.csv','user_merchant_feature2.csv','other_feature2.csv',True)
dataset3 = merge_data('coupon_feature3.csv','merchant_feature3.csv','user_feature3.csv','user_merchant_feature3.csv','other_feature3.csv',False)
#dataset1.to_csv('dtmp1.csv',index=None)
print("dataset1 info")
print(dataset1.info())
dataset1 = data_process(dataset1,True)
dataset2 = data_process(dataset2,True)
dataset3 = data_process(dataset3,False)

dataset1.to_csv('dataset1.csv',index=None)
dataset2.to_csv('dataset2.csv',index=None)
dataset3.to_csv('dataset3.csv',index=None)
