import pandas as pd
import numpy as np
#读入文件，输出文件概览信息
dfoff = pd.read_csv("ccf_offline_stage1_train.csv")
dfon = pd.read_csv("ccf_online_stage1_train.csv")
data_test = pd.read_csv("ccf_offline_stage1_test_revised.csv")
print("Finish reading data.")
print("offline")
print(dfoff.head(10))
print(dfoff.info())
print("online")
print(dfon.head(10))
print(dfon.info())

#对线下训练集进行一些简单的统计
def simple_statistics(dfoff):
    print("User amount:",len(set(dfoff['User_id'])))
    print("Merchant amount:",len(set(dfoff['Merchant_id'])))
    #print("Coupon type amount:",len(set(dfoff['Coupon_id'])))
    '''
    print("有优惠券，购买商品:%d"% dfoff[(dfoff['Date_received']!= np.nan)&(dfoff['Date']!=np.nan)].shape[0])
    print("有优惠券，不买商品:%d"% dfoff[(dfoff['Date_received']!= 'nan')&(dfoff['Date']=='nan')].shape[0])
    print("无优惠券，购买商品:%d"% dfoff[(dfoff['Date_received']== 'nan')&(dfoff['Date']!='nan')].shape[0])
    print("无优惠券，不买商品:%d"% dfoff[(dfoff['Date_received']== 'nan')&(dfoff['Date']=='nan')].shape[0])
    '''
    print('处理前Discount_rate栏：\n',dfoff['Discount_rate'].unique())
simple_statistics(dfoff)

def getDiscountType(row):
    if pd.isnull(row):
        return np.nan
    elif ':' in row:
        return 1
    else:
        return 0

def convertRate(row):
    """Convert discount to rate"""
    if pd.isnull(row):
        return 1.0
    elif ':' in str(row):
        rows = row.split(':')
        return 1.0 - float(rows[1])/float(rows[0])
    else:
        return float(row)

def getDiscountMan(row):
    if ':' in str(row):
        rows = row.split(':')
        return int(rows[0])
    else:
        return 0

def getDiscountJian(row):
    if ':' in str(row):
        rows = row.split(':')
        return int(rows[1])
    else:
        return 0
print("tool is ok.")

def processData(df):
    # convert discunt_rate
    df['discount_rate'] = df['Discount_rate'].apply(convertRate)
    df['discount_man'] = df['Discount_rate'].apply(getDiscountMan)
    df['discount_jian'] = df['Discount_rate'].apply(getDiscountJian)
    df['discount_type'] = df['Discount_rate'].apply(getDiscountType)
    print(df['discount_rate'].unique())
    # convert distance
    df['distance'] = df['Distance'].fillna(-1).astype(int)
    return df

dfoff = processData(dfoff)
data_test = processData(data_test)

date_received = dfoff['Date_received'].unique()
date_received = sorted(date_received[pd.notnull(date_received)])

date_buy = dfoff['Date'].unique()
date_buy = sorted(date_buy[pd.notnull(date_buy)])
date_buy = sorted(dfoff[dfoff['Date'].notnull()]['Date'])
couponbydate = dfoff[dfoff['Date_received'].notnull()][['Date_received', 'Date']].groupby(['Date_received'], as_index=False).count()
couponbydate.columns = ['Date_received','count']
buybydate = dfoff[(dfoff['Date'].notnull()) & (dfoff['Date_received'].notnull())][['Date_received', 'Date']].groupby(['Date_received'], as_index=False).count()
buybydate.columns = ['Date_received','count']
print("end")