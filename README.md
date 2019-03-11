# svd

## 基于SVD的菜品推荐系统

* 不同用户以不同身份登陆，系统调取用户已经购买过的菜品及评分记录，输入到推荐算法中，运行程序计算出该用户未购买过并可能会喜爱的菜品前三名，为该用户推荐。
* 用户在网页前端可以对菜品消费情况进行查看，分为<推荐的菜品>，<已经购买过的菜品>和<其他菜品>三部分，并可进行点菜评分操作。
* 用户对菜品的评分和算法得出的推荐菜品存储在MySQL数据库中，便于前台显示和后端程序的调用。用户未做出评价的菜品评分默认为0 。
* 根据用户最新的消费情况和菜品评分，更新推荐菜品。

![基于SVD的菜品推荐系统](https://github.com/FengYue95/svd/blob/master/img/1.png)
![基于SVD的菜品推荐系统](https://github.com/FengYue95/svd/blob/master/img/2.png)
![基于SVD的菜品推荐系统](https://github.com/FengYue95/svd/blob/master/img/3.png)
![基于SVD的菜品推荐系统](https://github.com/FengYue95/svd/blob/master/img/4.png)
![基于SVD的菜品推荐系统](https://github.com/FengYue95/svd/blob/master/img/5.png)


