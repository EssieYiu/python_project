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
dfoff['Discount_rate'] = dfoff['Discount_rate'].apply(convert_rate)
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
    user_coupon_use,
    user_coupon_use_rate,
    user_avg_discount_rate,
    user_min_discount_rate,
    user_max_discount_rate,
    user_avg_coupon_per_merchant
Input: feature
Output: DataFrame

'''
def get_user_feature(feature):
    user = feature[['User_id','Merchant_id','Coupon_id','Discount_rate','Distance','Date_received','Date']]
    t = user[['User_id']]
    t = t.drop_duplicates()

    #用户领取优惠券核销次数
    t1 = user[(user.Coupon_id != -1)&(user.Date != -1)][['User_id']]
    t1['user_coupon_use'] = 1
    t1 = t1.groupby('User_id').agg('sum').reset_index()

    #用户领取优惠券总数,merge后再计算优惠券核销率
    t2 = user[user.Date_received != -1][['User_id']]
    t2['coupon_total'] = 1
    t2 = t2.groupby('User_id').agg('sum').reset_index()

    #用户核销优惠券的平均消费折率
    t3 = user[(user.Coupon_id != -1)&(user.Date != -1)][['User_id','Discount_rate']]
    t3 = t3.groupby('User_id').agg('mean').reset_index()
    t3.rename(columns={'Discount_rate':'user_avg_discount_rate'},inplace=True)

    #用户核销优惠券的最小消费折率
    t4 = user[(user.Coupon_id != -1)&(user.Date != -1)][['User_id','Discount_rate']]
    t4 = t4.groupby('User_id').agg('min').reset_index()
    t4.rename(columns={'Discount_rate':'user_min_discount_rate'},inplace=True)

    #用户核销优惠券的最大消费折率
    t5 = user[(user.Coupon_id !=-1)&(user.Date !=-1)][['User_id','Discount_rate']]
    t5 = t5.groupby('User_id').agg('max').reset_index()
    t5.rename(columns={'Discount_rate':'user_max_discount_rate'},inplace=True)

    #用户平均核销每个商家多少张优惠券：用户核销优惠券总数/商家总数
    #这里计算用户对应的商家总数，后面用user_coupon_use除
    t6 = user[['User_id','Merchant_id']]
    t6 = t6.drop_duplicates()
    t6['Merchant_id'] = 1
    t6 = t6.groupby('User_id').agg('sum').reset_index()
    t6.rename(columns={'Merchant_id':'merchant_count'},inplace=True)

    user_feature = pd.merge(t,t1,on='User_id',how = 'left')
    user_feature = pd.merge(user_feature,t2,on='User_id',how='left')
    user_feature = pd.merge(user_feature,t3,on='User_id',how='left')
    user_feature = pd.merge(user_feature,t4,on='User_id',how='left')
    user_feature = pd.merge(user_feature,t5,on='User_id',how='left')
    user_feature = pd.merge(user_feature,t6,on='User_id',how='left')
    user_feature.user_coupon_use = user_feature.user_coupon_use.replace(np.nan,0)
    user_feature.merchant_count = user_feature.merchant_count.replace(np.nan,0)
    user_feature['user_coupon_use_rate'] = user_feature.user_coupon_use.astype('float')/user_feature.coupon_total.astype('float')
    user_feature['user_avg_coupon_per_merchant'] = user_feature.user_coupon_use.astype('float')/user_feature.merchant_count.astype('float')
    user_feature.coupon_total = user_feature.coupon_total.replace(np.nan,0)
    return user_feature


user_feature1 = get_user_feature(feature1)
user_feature1.to_csv('user_feature1.csv',index='None')
user_feature2 = get_user_feature(feature2)
user_feature2.to_csv('user_feature2.csv',index='None')
user_feature3 = get_user_feature(feature3)
user_feature3.to_csv('user_feature3.csv',index='None')


'''
merchant feature
商家优惠券被领取后核销率 merchant_coupon_used_rate = coupon_used/coupon_out
商家优惠券被核销的平均消费折率 merchant_coupon_avg_discount_rate
商家优惠券被核销的最小消费折率 merchant_coupon_min_discount_rate
商家优惠券被核销的最大消费折率 merchant_coupon_max_discount_rate
商家平均每种优惠券核销多少张 merchant_per_kind_coupon_used = coupon_used/coupon_kinds?
商家被核销优惠券中的平均用户-商家距离 merchant_user_avg_distance
商家被核销优惠券中的最小用户-商家距离 merchant_user_min_distance
商家被核销优惠券中的最大用户-商家距离 merchant_user_max_distance
'''
def get_merchant_feature(feature):
    merchant = feature[['Merchant_id','Coupon_id','Discount_rate','Distance','Date_received','Date']]

    t = merchant[['Merchant_id']]
    t = t.drop_duplicates()

    #merchant coupon total get by user:coupon_out
    t1 = merchant[(merchant.Coupon_id !=-1)][['Merchant_id']]
    t1['coupon_out'] = 1
    t1 = t1.groupby('Merchant_id').agg('sum').reset_index()

    #merchant coupon total use by user:coupon_used
    t2 = merchant[(merchant.Coupon_id !=-1)&(merchant.Date !=-1)][['Merchant_id']]
    t2['coupon_used'] = 1
    t2 = t2.groupby('Merchant_id').agg('sum').reset_index()

    #merchant_coupon_avg_discount_rate
    t3 = merchant[(merchant.Coupon_id !=-1)&(merchant.Date !=-1)][['Merchant_id','Discount_rate']]
    t3 = t3.groupby('Merchant_id').agg('mean').reset_index()
    t3.rename(columns={'Discount_rate':'merchant_coupon_avg_discount_rate'},inplace=True)

    #merchant_coupon_min_discount_rate
    t4 = merchant[(merchant.Coupon_id !=-1)&(merchant.Date !=-1)][['Merchant_id','Discount_rate']]
    t4 = t4.groupby('Merchant_id').agg('min').reset_index()
    t4.rename(columns={'Discount_rate':'merchant_coupon_min_discount_rate'},inplace=True)

    #merchant_coupon_max_discount_rate
    t5 = merchant[(merchant.Coupon_id !=-1)&(merchant.Date !=-1)][['Merchant_id','Discount_rate']]
    t5 = t5.groupby('Merchant_id').agg('max').reset_index()
    t5.rename(columns={'Discount_rate':'merchant_coupon_max_discount_rate'},inplace=True)   

    #merchant kinds of coupon:coupon_kinds
    t6 = merchant[(merchant.Coupon_id !=-1)][['Merchant_id','Discount_rate']]
    t6 = t6.drop_duplicates()
    t6['Discount_rate'] = 1
    t6 = t6.groupby('Merchant_id').agg('sum').reset_index()
    t6.rename(columns={'Discount_rate':'coupon_kinds'},inplace=True)

    #merchant_user_avg_distance
    t7 = merchant[(merchant.Coupon_id !=-1)&(merchant.Date !=-1)][['Merchant_id','Distance']]
    t7 = t7.groupby('Merchant_id').agg('mean').reset_index()
    t7.rename(columns={'Distance':'merchant_user_avg_distance'},inplace = True)

    #merchant_user_min_distance
    t8 = merchant[(merchant.Coupon_id !=-1)&(merchant.Date !=-1)][['Merchant_id','Distance']]
    t8 = t8.groupby('Merchant_id').agg('min').reset_index()
    t8.rename(columns={'Distance':'merchant_user_min_distance'},inplace = True)

    #merchnat_user_max_distance
    t9 = merchant[(merchant.Coupon_id !=-1)&(merchant.Date !=-1)][['Merchant_id','Distance']]
    t9 = t9.groupby('Merchant_id').agg('max').reset_index()
    t9.rename(columns={'Distance':'merchant_user_max_distance'},inplace = True)

    merchant_feature = pd.merge(t,t1,on='Merchant_id',how='left')
    merchant_feature = pd.merge(merchant_feature,t2,on='Merchant_id',how='left')
    merchant_feature = pd.merge(merchant_feature,t3,on='Merchant_id',how='left')
    merchant_feature = pd.merge(merchant_feature,t4,on='Merchant_id',how='left')
    merchant_feature = pd.merge(merchant_feature,t5,on='Merchant_id',how='left')
    merchant_feature = pd.merge(merchant_feature,t6,on='Merchant_id',how='left')
    merchant_feature = pd.merge(merchant_feature,t7,on='Merchant_id',how='left')
    merchant_feature = pd.merge(merchant_feature,t8,on='Merchant_id',how='left')
    merchant_feature = pd.merge(merchant_feature,t9,on='Merchant_id',how='left')
    merchant_feature.coupon_used = merchant_feature.coupon_used.replace(np.nan,0)
    merchant_feature.coupon_out = merchant_feature.coupon_out.replace(np.nan,0)
    merchant_feature.coupon_kinds = merchant_feature.coupon_kinds.replace(np.nan,0)
    merchant_feature['merchant_coupon_used_rate'] = merchant_feature.coupon_used.astype('float')/merchant_feature.coupon_out.astype('float')
    merchant_feature['merchant_per_kind_coupon_used'] = merchant_feature.coupon_used.astype('float')/merchant_feature.coupon_kinds.astype('float')
    return merchant_feature

merchant_feature1 = get_merchant_feature(feature1)
merchant_feature1.to_csv('merchant_feature1.csv')
merchant_feature2 = get_merchant_feature(feature2)
merchant_feature2.to_csv('merchant_feature2.csv')
merchant_feature3 = get_merchant_feature(feature3)
merchant_feature3.to_csv('merchnat_feature3.csv')
