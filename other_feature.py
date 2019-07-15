import pandas as pd
import numpy as np
import datetime as dt
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


"""
other feature:
      this_month_user_receive_all_coupon_count
      this_month_user_receive_same_coupon_count
      this_month_user_receive_same_coupon_lastone
      this_month_user_receive_same_coupon_firstone
      this_day_user_receive_all_coupon_count
      this_day_user_receive_same_coupon_count
      day_gap_before, day_gap_after  (receive the same coupon)
"""


def get_other_feature(dataset):
    t = dataset[['User_id']]
    t['this_month_user_receive_all_coupon_count'] = 1
    t = t.groupby('User_id').agg('sum').reset_index()

    t1 = dataset[['User_id', 'Coupon_id']]
    t1['this_month_user_receive_same_coupon_count'] = 1
    t1 = t1.groupby(['User_id', 'Coupon_id']).agg('sum').reset_index()

    t2 = dataset[['User_id', 'Coupon_id', 'Date_received']]
    t2.Date_received = t2.Date_received.astype('str')
    t2 = t2.groupby(['User_id', 'Coupon_id'])['Date_received'].agg(lambda x: ':'.join(x)).reset_index()
    t2['receive_number'] = t2.Date_received.apply(lambda s: len(s.split(':')))
    t2 = t2[t2.receive_number > 1]
    t2['max_date_received'] = t2.Date_received.apply(lambda s: max([int(float(d)) for d in s.split(':')]))
    t2['min_date_received'] = t2.Date_received.apply(lambda s: min([int(float(d)) for d in s.split(':')]))
    t2 = t2[['User_id', 'Coupon_id', 'max_date_received', 'min_date_received']]

    t3 = dataset[['User_id', 'Coupon_id', 'Date_received']]
    t3 = pd.merge(t3, t2, on=['User_id', 'Coupon_id'], how='left')
    t3['this_month_user_receive_same_coupon_lastone'] = t3.max_date_received - t3.Date_received
    t3['this_month_user_receive_same_coupon_firstone'] = t3.Date_received - t3.min_date_received

    def is_firstlastone(x):
        if x == 0:
            return 1
        elif x > 0:
            return 0
        else:
            return -1  # those only receive once

    t3.this_month_user_receive_same_coupon_lastone = t3.this_month_user_receive_same_coupon_lastone.apply(
        is_firstlastone)
    t3.this_month_user_receive_same_coupon_firstone = t3.this_month_user_receive_same_coupon_firstone.apply(
        is_firstlastone)
    t3 = t3[['User_id', 'Coupon_id', 'Date_received', 'this_month_user_receive_same_coupon_lastone',
             'this_month_user_receive_same_coupon_firstone']]

    t4 = dataset[['User_id', 'Date_received']]
    t4['this_day_user_receive_all_coupon_count'] = 1
    t4 = t4.groupby(['User_id', 'Date_received']).agg('sum').reset_index()

    t5 = dataset[['User_id', 'Coupon_id', 'Date_received']]
    t5['this_day_user_receive_same_coupon_count'] = 1
    t5 = t5.groupby(['User_id', 'Coupon_id', 'Date_received']).agg('sum').reset_index()

    t6 = dataset[['User_id', 'Coupon_id', 'Date_received']]
    t6.Date_received = t6.Date_received.astype('str')
    t6 = t6.groupby(['User_id', 'Coupon_id'])['Date_received'].agg(lambda x: ':'.join(x)).reset_index()
    t6.rename(columns={'Date_received': 'Dates'}, inplace=True)

    def get_day_gap_before(s):
        date_received, dates = s.split('-')
        dates = dates.split(':')
        gaps = []
        for d in dates:
            this_gap = (dt.date(int(date_received[0:4]), int(date_received[4:6]), int(date_received[6:8])) - dt.date(
                int(d[0:4]),
                int(d[4:6]),
                int(d[
                    6:8]))).days
            if this_gap > 0:
                gaps.append(this_gap)
        if len(gaps) == 0:
            return -1
        else:
            return min(gaps)

    def get_day_gap_after(s):
        date_received, dates = s.split('-')
        dates = dates.split(':')
        gaps = []
        for d in dates:
            this_gap = (dt.date(int(d[0:4]), int(d[4:6]), int(d[6:8])) - dt.date(int(date_received[0:4]),
                                                                           int(date_received[4:6]),
                                                                           int(date_received[6:8]))).days
            if this_gap > 0:
                gaps.append(this_gap)
        if len(gaps) == 0:
            return -1
        else:
            return min(gaps)

    t7 = dataset[['User_id', 'Coupon_id', 'Date_received']]
    t7 = pd.merge(t7, t6, on=['User_id', 'Coupon_id'], how='left')
    t7['date_received_date'] = t7.Date_received.astype('str') + '-' + t7.Dates
    t7['date_received_date'] = t7.Date_received.astype('str') + '-' + t7.Dates
    t7['day_gap_before'] = t7.date_received_date.apply(get_day_gap_before)
    t7['day_gap_after'] = t7.date_received_date.apply(get_day_gap_after)
    t7 = t7[['User_id', 'Coupon_id', 'Date_received', 'day_gap_before', 'day_gap_after']]

    other_feature = pd.merge(t1, t, on='User_id')
    other_feature = pd.merge(other_feature, t3, on=['User_id', 'Coupon_id'])
    other_feature = pd.merge(other_feature, t4, on=['User_id', 'Date_received'])
    other_feature = pd.merge(other_feature, t5, on=['User_id', 'Coupon_id', 'Date_received'])
    other_feature = pd.merge(other_feature, t7, on=['User_id', 'Coupon_id', 'Date_received'])
    print(other_feature.shape)
    return other_feature


other_feature1 = get_other_feature(dataset1)
other_feature1.to_csv('other_feature1.csv',index='None')
other_feature2 = get_other_feature(dataset2)
other_feature2.to_csv('other_feature2.csv',index='None')
other_feature3 = get_other_feature(dataset3)
other_feature3.to_csv('other_feature3.csv',index='None')