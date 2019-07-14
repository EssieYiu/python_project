# python_project
python大作业
o2o优惠劵使用预测
大家所作工作的进展都可以写在这里

## 数据预处理
### 所给原始数据
Table1 用户线下消费和优惠劵领取行为

|Field|Description|
|--|--|
|User_id|用户ID|
|Merchant_id|商户ID|
|Coupon_id|优惠券ID：null表示无优惠券消费，此时Discount_rate和Date_received字段无意义|
|Discount_rate|优惠率：x \in [0,1]代表折扣率；x:y表示满x减y。单位是元|
|Distance|user经常活动的地点离该merchant的最近门店距离是x*500米（如果是连锁店，则取最近的一家门店），x\in[0,10]；null表示无此信息，0表示低于500米，10表示大于5公里|
|Date received|领取优惠劵日期|
|Date|	消费日期：如果Date=null & Coupon_id != null，该记录表示领取优惠券但没有使用，即负样本；如果Date!=null & Coupon_id = null，则表示普通消费日期；如果Date!=null & Coupon_id != null，则表示用优惠券消费日期，即正样本|

Table2 用户线上点击/消费和优惠劵领取行为

|Field|Description|
|--|--|
|User_id|用户ID|
|Merchant_id|商户ID|
|Action|0点击 1购买 2领取优惠劵|
|Coupon_id|优惠券ID：null表示无优惠券消费，此时Discount_rate和Date_received字段无意义。“fixed”表示该交易是限时低价活动。|
|Discount_rate|优惠率：x \in [0,1]代表折扣率；x:y表示满x减y；“fixed”表示低价限时优惠；|
|Date_received|领取优惠劵日期|
|Date|消费日期：如果Date=null & Coupon_id != null，该记录表示领取优惠券但没有使用；如果Date!=null & Coupon_id = null，则表示普通消费日期；如果Date!=null & Coupon_id != null，则表示用优惠券消费日期；|

Table3 用户O2O线下优惠劵使用预测样本

|Field|Description|
|--|--|
|User_id|用户ID|
|Merchant_id|商户ID|
|Coupon_id|优惠劵ID|
|Discount_rate|优惠率：x \in [0,1]代表折扣率；x:y表示满x减y.|
|Distance|user经常活动的地点离该merchant的最近门店距离是x*500米（如果是连锁店，则取最近的一家门店），x\in[0,10]；null表示无此信息，0表示低于500米，10表示大于5公里；|
|Date_received|领取优惠劵日期|

Table4 选手提交文件字段，其中user_id,coupon_id和date_received均来自Table 3,而Probability为预测值

|Field|Description|
|--|--|
|User_id|用户ID|
|Coupon_id|优惠劵ID|
|Date_received|领取优惠劵日期|
|Probability|15天内用劵概率，由参赛选手给出|

### 需要处理的数据
1. 缺失值处理
- 可能出现NULL的字段是Coupon_id,Discount_rate,Distance,Date_received,Date
- Distance字段为NULL意思应该是没有收集到这个数据，可能需要我们进行填充（当作预测值处理）或者直接把这个条目弃掉
- Coupon字段为NULL是无优惠劵消费，此时Discount_rate和Date_received无意义
- *会否可能出现Coupon_id不为NULL，但Discount_rate和Date_receive出现NULL的状况？（如何处理？）*
- Date为NULL表示的是没有进行消费
- *按照题目的表述，似乎是不会出现Coupon为NULL且Date为NULL的字段？（既没有领优惠券，也没有进行消费。但数据很多，不一定能够确定，处理的时候可能需要稍微注意一下）*

## 特征
1. 和Discount_rate相关的
折扣率（Discount_rate),满（Discount_man),减（Discount_jian),类型（Discount_type)
2. 工作日/周末（日期）
3. 距离
4. 用户

## 模型
可用参考模型：
1. XGboost
2. GBDT
3. Random Forest
4. Adaboost
5. DeepFM

## 其他说明
- readin.py读入三个原始文件，可以看到文件的概览信息
一些比较有用的参考链接(大家找到什么有用的资料链接都可以放在这里共享)
- [100行代码链接](https://tianchi.aliyun.com/course/courseConsole?spm=5176.12282070.0.0.e6c02042YHb4OP&courseId=263&chapterIndex=1&sectionIndex=1)
- [感觉很厉害的链接](https://tianchi.aliyun.com/notebook-ai/detail?spm=5176.12586969.1002.3.29281b48a8MasP&postId=58107)
- [season one 第一名github链接](https://github.com/wepe/O2O-Coupon-Usage-Forecast/tree/master/code/wepon/season%20one)
- [pandas基础](https://tianchi.aliyun.com/notebook-ai/detail?spm=5176.12282042.0.0.4a732042WRDDrk&postId=6068)
- [Groupby函数用法](https://blog.csdn.net/qq_24753293/article/details/78338263)
- [Groupby&agg](https://segmentfault.com/a/1190000012394176)
- [CSDN上的一个系统性总结思路](https://blog.csdn.net/orsonV/article/details/83509414)
- [模型选择和特征选择的基本方法](https://www.cnblogs.com/learninglife/p/9340636.html)

- 第一名所提取的特征如下，可以参考
    - other feature column =['user_id','coupon_id','date_received','this_month_user_receive_all_coupon_count','this_month_user_receive_same_coupon_count','receive_number','max_date_receive','min_date_receive','this_month_user_receive_same_coupon_lastone','this_month_user_receive_same_coupon_firstone','date_receive_date','day_gap_before','day_gap_after'],在dataset1，2，3中获取
    - coupon column =['user_id','merchant_id','discount_rate','distance','receive_date','day_of_week','day_of_month','days_distance','discount_man','discount_jian','is_man_jian','coupon_id','coupon_count'],在dataset1,2,3中获取
    - merchant column=['merchant_id,'coupon_id','distance','date_recieved','date','total_sales','sales_use_coupon','total_coupon','merchant_min_distance','merchant_max_distance','merchant_mean_distance','merchant_median_distance','coupon_rate']在feature1,2,3中获取
    - user column =['user_id','merchant_id','count_merchant','distance','user_max_distance','user_min_distance','user_mean_distance','user_median_distance','buy_user_coupon','buy_total','coupon_received','user_date_datereceived_gap','gap_avg','gap_min','gap_max']在feature1,2,3中获取
    - user-merchant column =['user_id','merchant_id','user_merchant_buy_total','user_merchant_received','user_merchant_buy_use_coupon','user_merchant_any','user_merchant_buy_common','user_merchant_coupon_transfer_rate','user_merchant_coupon_buy_rate','user_merchant_rate','user_merchant_common_buy_rate']
    在feature1,2,3中获取
    - 将上述的特征分别整合进dataset1，2，3中，除dataset3没有label列以外，其他的都和另两个相同
    - label:dataset1,2有label,dataset3没有，指示的是正、零、负样本
    - label作为y，其他特征作为x，进行训练，预测dataset3的label值

## 遇到的困难（及解决方案）
1. nan不能使用等号比较，要使用isnan函数。在选取DataFrame的元素的时候，又不能对series直接调用函数之类，因此，先将原来的NAN值填为-1，因此得以判断原位置是否NAN
