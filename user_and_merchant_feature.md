# user and merchant feature
提取特征（用户特征和商家特征）
## 用户特征（线下）
- 用户领取优惠劵核销次数 user_coupon_use
- 用户领取优惠券后进行核销率 user_coupon_use_rate
- 用户核销优惠券的平均消费折率 user_avg_discount_rate
- 用户核销优惠券的最低消费折率 user_min_discount_rate
- 用户核销优惠券的最高消费折率 user_max_discount_rate
- 用户平均核销每个商家多少张优惠券 user_avg_coupon_per_merchant

## 商家特征
- 商家优惠券被领取后核销率 merchant_coupon_used
- 商家优惠券被核销的平均消费折率 merchant_coupon_avg_discount_rate
- 商家优惠券被核销的最小消费折率 merchant_coupon_min_discount_rate
- 商家优惠券被核销的最大消费折率 merchant_coupon_max_discount_rate
- 商家平均每种优惠券核销多少张 merchant_per_kind_coupon_used
- 商家被核销优惠券中的平均用户-商家距离 merchant_user_avg_distance
- 商家被核销优惠券中的最小用户-商家距离 merchant_user_min_distance
- 商家被核销优惠券中的最大用户-商家距离 merchant_user_max_distance