import pandas as pd
import numpy as np
import datetime
import math
#读入文件，输出文件概览信息
dfoff = pd.read_csv("ccf_offline_stage1_train.csv")
data_test = pd.read_csv("ccf_offline_stage1_test_revised.csv")
print("Finish reading data.")
print("offline")
print(dfoff.head(10))
print(dfoff.info())
'''
print("nans number",dfoff.isna().sum().sum())
print("nulll number",dfoff.isnull().sum().sum())
'''
#处理NAN值
dfoff.fillna(-1,inplace = True)

#划分数据集，目前参考的是第一名的划分方案
dataset3 = data_test
feature3 = dfoff[((dfoff.Date>=20160315)&(dfoff.Date<=20160630))|((dfoff.Date==-1)&(dfoff.Date_received>=20160315)&(dfoff.Date_received<=20160630))]
dataset2 = dfoff[(dfoff.Date_received>=20160515)&(dfoff.Date_received<=20160615)]
feature2 = dfoff[(dfoff.Date>=20160201)&(dfoff.Date<=20160514)|((dfoff.Date==-1)&(dfoff.Date_received>=20160201)&(dfoff.Date_received<=20160514))]
dataset1 = dfoff[(dfoff.Date_received>=20160414)&(dfoff.Date_received<=20160514)]
feature1 = dfoff[(dfoff.Date>=20160101)&(dfoff.Date<=20160413)|((dfoff.Date==-1)&(dfoff.Date_received>=20160101)&(dfoff.Date_received<=20160413))]


t = dataset3[['User_id']]
t['this_month_user_receive_all_coupon_count'] = 1
t = t.groupby('User_id').agg('sum').reset_index()
print("t",t.head())
t1 = dataset3[['User_id','Coupon_id']]
t1['this_month_user_receive_same_coupon_count'] = 1
t1 = t1.groupby(['User_id','Coupon_id']).agg('sum').reset_index()

print("t1",t1.head())
#对线下训练集进行一些简单的统计
def simple_statistics(dfoff):
    print("User amount:",len(set(dfoff['User_id'])))
    print("Merchant amount:",len(set(dfoff['Merchant_id'])))
    #print("Coupon type amount:",len(set(dfoff['Coupon_id'])))
    print("有优惠券，购买商品:", dfoff[(dfoff['Date_received'] != -1)&(dfoff['Date'] != -1)].shape[0])
    print("有优惠券，不买商品:%d"% dfoff[(dfoff['Date_received']!= -1)&(dfoff['Date']==-1)].shape[0])
    print("无优惠券，购买商品:%d"% dfoff[(dfoff['Date_received']== -1)&(dfoff['Date']!=-1)].shape[0])
    print("无优惠券，不买商品:%d"% dfoff[(dfoff['Date_received']== -1)&(dfoff['Date']==-1)].shape[0])
    
    print('处理前Discount_rate栏：\n',dfoff['Discount_rate'].unique())


#simple_statistics(dfoff)