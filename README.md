# ALNS

## This is a repository for ALNS


## 如发现代码有问题可与我邮件、微信、公众号等联系，或者在issue发布等

## 如果您喜欢或认为对您有帮助，还请 star 和 fork ！

### Contact me

### Mail: 1763423314@qq.com

### 公众号: Sandiago
![微信图片_20220411144643](https://user-images.githubusercontent.com/67860270/162680224-6e57647a-de34-4897-9ec1-0435dcbcfd42.jpg)


# 文件说明

## 输入文件夹：

![image](https://user-images.githubusercontent.com/67860270/162675189-e1058e02-b05c-48c3-89af-3a4f1717268b.png)

包括文件：

![image](https://user-images.githubusercontent.com/67860270/162675284-68bbfde8-3d9b-43c7-b092-e0d8af0197c1.png)

OAs为需求信息，ID，PICKUP，DELIVERY节点，（服务费）

Nodes为节点信息：ID，坐标(x,y)，时间窗(a,b)，需求量(dm)，服务时间(st)

txt为基本信息说明

## 输出文件夹 output

![image](https://user-images.githubusercontent.com/67860270/162675824-8b9f3fbb-dffa-45d1-aa30-bed3185aaad2.png)

为了便于分析，保留了三个阶段的解：初始解，LNS最小化车辆数，ALNS优化

![image](https://user-images.githubusercontent.com/67860270/162675879-dcc0ef43-b6fd-45e1-91bb-61f43bcd7dc4.png)

ALNS求解结果：可视化，解输出，算子得分曲线变化图，ALNS目标值变化曲线

# 数据结构说明

## 类 Algorithm_inputdata

参数：文件夹位置，订单的数量（该参数暂时不用）

属性说明：

Nodes_numpy：将dataframe转换为array，提高算法中访问节点各类信息的效率

# 类 Truck

参数：ID，卡车的最大载重，数据集中时间窗的最大值（一般就是depot的b值）

## 属性说明：

time_line：卡车离开某节点的时间

其余属性说明见代码注释
## 函数说明
### truck_copy()
由于在算法中需要频繁的区分当前解和搜索返回解、python面向对象的特性以及数据结构的复杂，使用deepcopy函数复杂度较高，使用时时间开销过大，故定义一个该数据结构专用的copy函数
### check_and_update()
入参：修改点位置、inputdata、removal还是insert、如果为insert那么为插入PICKUP还是DELIVERY、如果为插入DELIVERY则还需要传入PICKUP的插入位置

return 插入是否成功

说明：如果时insert则使用了参数latest_possible_time 进行O(1)检查加速

其他函数见代码注释

# 算法解释

公众号文章链接：https://mp.weixin.qq.com/s/yoZu_bMw0b1DzL4GDgHxXQ

# 实验
