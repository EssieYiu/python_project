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
coupon related: 
      discount_rate 优惠券折率
      manjian_min_cost 满减优惠券的最低消费
      discount_type 优惠券类型(0-直接折扣，1-满减)
      coupon_use 历史上该优惠券核销量
      coupon_total 历史上该优惠券领取总量
      use_coupon_rate 历史上用户对该优惠券的核销率
Input: feature
Output: DataFrame
'''


def calc_discount_rate(s):
    s = str(s)
    s = s.split(':')
    if len(s) == 1: # 直接打折
        return float(s[0])
    else: # 满减
        return 1.0 - float(s[1]) / float(s[0])


def get_discount_man(s):
    s = str(s)
    s = s.split(':')
    if len(s) == 1:
        return -1 #若是直接折扣，返回-1
    else:
        return int(s[0])


def get_discount_jian(s):
    s = str(s)
    s = s.split(':')
    if len(s) == 1:
        return 'null'
    else:
        return int(s[1])


def is_man_jian(s):
    s = str(s)
    s = s.split(':')
    if len(s) == 1:
        return 0
    else:
        return 1


def get_coupon_feature(dataset):
    '''
    coupon = feature[['User_id','Merchant_id', 'Coupon_id', 'Discount_rate', 'Distance', 'Date_received', 'Date']]
    t = coupon[['User_id','Merchant_id','Coupon_id','Date_received']]
    t = t.drop_duplicates()

    #discount_rate 优惠券折率
    t['discount_rate'] = feature.Discount_rate.apply(calc_discount_rate)
    #manjian_min_cost 满减优惠券的最低消费
    t['manjian_min_cost'] = feature.Discount_rate.apply(get_discount_man)
    #discount_type 优惠券类型(0-直接折扣，1-满减)
    t['discount_type'] = feature.Discount_rate.apply(is_man_jian)

    #优惠券被核销次数
    t1 = coupon[(coupon.Coupon_id != -1)&(coupon.Date != -1)][['Coupon_id']]
    t1['coupon_use'] = 1
    t1 = t1.groupby('Coupon_id').agg('sum').reset_index()

    #优惠券被领取总数
    t2 = coupon[coupon.Date_received != -1][['Coupon_id']]
    t2['coupon_total'] = 1
    t2 = t2.groupby('Coupon_id').agg('sum').reset_index()

    coupon_feature = pd.merge(t, t1, on='Coupon_id', how='left')
    coupon_feature = pd.merge(coupon_feature, t2, on='Coupon_id', how='left')

    #历史上用户对该优惠券的核销率
    coupon_feature['use_coupon_rate'] = coupon_feature.coupon_use.astype('float') / coupon_feature.coupon_total.astype('float')

    return coupon_feature
    '''
    dataset['discount_man'] = dataset.Discount_rate.apply(get_discount_man)
    dataset['discount_jian'] = dataset.Discount_rate.apply(get_discount_jian)
    dataset['is_man_jian'] = dataset.Discount_rate.apply(is_man_jian)
    dataset['discount_rate'] = dataset.Discount_rate.apply(calc_discount_rate)
    d = dataset[['Coupon_id']]
    d['coupon_count'] = 1
    d = d.groupby('Coupon_id').agg('sum').reset_index()
    dataset = pd.merge(dataset,d,on='Coupon_id',how='left')
    return dataset

coupon_feature1 = get_coupon_feature(dataset1)
coupon_feature1.to_csv('coupon_feature1.csv',index='None')
coupon_feature2 = get_coupon_feature(dataset2)
coupon_feature2.to_csv('coupon_feature2.csv',index='None')
coupon_feature3 = get_coupon_feature(dataset3)
coupon_feature3.to_csv('coupon_feature3.csv',index='None')


'''
coupon related: 
      discount_rate 优惠券折率
      manjian_min_cost 满减优惠券的最低消费
      discount_type 优惠券类型(0-直接折扣，1-满减)
      coupon_use 历史上该优惠券核销量
      coupon_total 历史上该优惠券领取总量
      use_coupon_rate 历史上用户对该优惠券的核销率
Input: feature
Output: DataFrame
'''


def get_user_merchant_feature(feature):
    user_merchant = feature[['User_id', 'Merchant_id']]
    user_merchant.drop_duplicates(inplace=True)

    t1 = feature[['User_id', 'Merchant_id', 'Coupon_id']]
    t1 = t1[t1.Coupon_id != -1][['User_id', 'Merchant_id']]
    t1['user_merchant_received'] = 1
    t1 = t1.groupby(['User_id', 'Merchant_id']).agg('sum').reset_index()
    t1.drop_duplicates(inplace=True)

    t2 = feature[['User_id', 'Merchant_id', 'Date', 'Date_received']]
    t2 = t2[(t2.Date != -1) & (t2.Date_received != -1)][['User_id', 'Merchant_id']]
    t2['user_merchant_buy_use_coupon'] = 1
    t2 = t2.groupby(['User_id', 'Merchant_id']).agg('sum').reset_index()
    t2.drop_duplicates(inplace=True)

    user_merchant = pd.merge(user_merchant, t1, on=['User_id', 'Merchant_id'], how='left')
    user_merchant = pd.merge(user_merchant, t2, on=['User_id', 'Merchant_id'], how='left')
    user_merchant['user_merchant_buy_use_coupon'].fillna(0, inplace=True)

    user_merchant['user_merchant_coupon_transfer_rate'] = user_merchant.user_merchant_buy_use_coupon.astype(
        'float') / user_merchant.user_merchant_received.astype('float')
    user_merchant.fillna(0,inplace=True)
    return user_merchant


user_feature1 = get_user_merchant_feature(feature1)
user_feature1.to_csv('user_merchant_feature1.csv',index='None')
user_feature2 = get_user_merchant_feature(feature2)
user_feature2.to_csv('user_merchant_feature2.csv',index='None')
user_feature3 = get_user_merchant_feature(feature3)
user_feature3.to_csv('user_merchant_feature3.csv',index='None')

