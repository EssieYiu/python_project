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
1.缺失值处理
- 可能出现NULL的字段是Coupon_id,Discount_rate,Distance,Date_received,Date
- Distance字段为NULL意思应该是没有收集到这个数据，可能需要我们进行填充（当作预测值处理）或者直接把这个条目弃掉
- Coupon字段为NULL是无优惠劵消费，此时Discount_rate和Date_received无意义
- *会否可能出现Coupon_id不为NULL，但Discount_rate和Date_receive出现NULL的状况？（如何处理？）*
- Date为NULL表示的是没有进行消费
- *按照题目的表述，似乎是不会出现Coupon为NULL且Date为NULL的字段？（既没有领优惠券，也没有进行消费。但数据很多，不一定能够确定，处理的时候可能需要稍微注意一下）*

## 特征
1.和Discount_rate相关的
折扣率（Discount_rate),满（Discount_man),减（Discount_jian),类型（Discount_type)
2.工作日/周末（日期）
3.（待补充，可能会有很多）

## 模型
