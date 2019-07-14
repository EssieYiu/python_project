
import pandas as pd
import numpy as np
import datetime
import math
#读入文件，输出文件概览信息
dfoff = pd.read_csv("ccf_offline_stage1_train.csv")
#dfoff.columns = ['User_id','Merchant_id','Coupon_id','Discount_rate','Distance','Date_received','Date']
data_test = pd.read_csv("ccf_offline_stage1_test_revised.csv")
#data_test.columns = ['User_id','Merchant_id','Coupon_id','Discount_rate','Distance','Date_received']
print("Finish reading data.")
print("offline")
print(dfoff.head(10))
print(dfoff.info())

#处理消费折率discount_rate
def convert_rate(row):
    if pd.isnull(row):
        return 1.0
    elif ':' in str(row):
        rows = row.split(':')
        return 1 - float(rows[1])/float(rows[0])
    else:
        return float(row)
dfoff['Discount_rate'].apply(convert_rate)
#处理null
dfoff['Distance'].fillna(11,inplace = True)
dfoff.fillna(-1,inplace=True)

dataset3 = data_test
feature3 = dfoff[((dfoff.Date>=20160315)&(dfoff.Date<=20160630))|((dfoff.Date==-1)&(dfoff.Date_received>=20160315)&(dfoff.Date_received<=20160630))]
dataset2 = dfoff[(dfoff.Date_received>=20160515)&(dfoff.Date_received<=20160615)]
feature2 = dfoff[(dfoff.Date>=20160201)&(dfoff.Date<=20160514)|((dfoff.Date==-1)&(dfoff.Date_received>=20160201)&(dfoff.Date_received<=20160514))]
dataset1 = dfoff[(dfoff.Date_received>=20160414)&(dfoff.Date_received<=20160514)]
feature1 = dfoff[(dfoff.Date>=20160101)&(dfoff.Date<=20160413)|((dfoff.Date==-1)&(dfoff.Date_received>=20160101)&(dfoff.Date_received<=20160413))]

'''
user feature
    user_coupon_use,user_coupon_use_rate,user_avg_discount_rate,user_min_discount_rate,user_max_discount_rate,user_avg_coupon_per_merchant
Input: feature
        date_begin
        date_end
Output: DataFrame

'''
def user_feature(feature,date_begin,date_end):
    user = feature[['User_id','Merchant_id','Coupon_id','Discount_rate','Distance','Date_received','Date']]
    t = user[['User_id']]
    t.drop_duplicates(inplace = True)

    #用户领取优惠券核销次数
    t1 = user[('Coupon_id'!=-1)&('Date'!=-1)][['User_id']]
    t1['user_coupon_use'] = 1
    t1 = t1.groupby('User_id').agg('sum').reset_index()

    #用户领取优惠券总数,merge后再计算优惠券核销率
    t2 = user['Date_received'!=-1][['User_id']]
    t2['coupon_total'] = 1
    t2.groupby('User_id').agg('sum').reset_index()

    #用户核销优惠券的平均消费折率
    t3 = user[('Coupon_id'!=-1)&('Date'!=-1)][['User_id','Discount_rate']]
    t3 = t3.groupby('User_id').agg('mean').reset_index()
    t3.rename(columns={'Discount_rate':'user_avg_discount_rate'},inplace=True)

    #用户核销优惠券的最小消费折率
    t4 = user[('Coupon_id'!=-1)&('Date'!=-1)][['User_id','Discount_rate']]
    t4 = t4.groupby('User_id').agg('min').reset_index()
    t4.rename(columns={'Discount_rate':'user_min_discount_rate'},inplace=True)

    #用户核销优惠券的最大消费折率
    t5 = user[('Coupon_id'!=-1)&('Date'!=-1)][['User_id','Discount_rate']]
    t5 = t5.groupby('User_id').agg('max').reset_index()
    t5.rename(columns={'Discount_rate':'user_max_discount_rate'},inplace=True)

    #用户平均核销每个商家多少张优惠券：用户核销优惠券总数/商家总数
    #这里计算用户对应的商家总数，后面用user_coupon_use除
    t6 = user[['User_id','Merchant_id']]
    t6.drop_duplicates()
    t6['Merchant_id'] = 1
    t6 = t6.groupby('User_id').agg('sum').reset_index()
    t6.rename(columns={'Merchant_id':'merchant_count'},inplace=True)

    user_feature = pd.merge(t,t1,on='User_id',how = 'left')
    user_feature = pd.merge(user_feature,t2,on='User_id',how='left')
    