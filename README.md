# ALNS

This is a repository for ALNS

Contact me

Mail: 1763423314@qq.com

公众号: Sandiago

如发现代码有问题可与我邮件、微信、公众号等联系

# 文件说明

## 输入文件夹：

![image](https://user-images.githubusercontent.com/67860270/162675189-e1058e02-b05c-48c3-89af-3a4f1717268b.png)

包括文件：

![image](https://user-images.githubusercontent.com/67860270/162675284-68bbfde8-3d9b-43c7-b092-e0d8af0197c1.png)

OAs为需求信息，ID，PICKUP，DELIVERY节点，（服务费）

Nodes为节点信息：ID，坐标(x,y)，时间窗(a,b)，需求量(dm)，服务时间(st)

txt为基本信息说明

## 输出文件夹 output

![image](https://user-images.githubusercontent.com/67860270/162675879-dcc0ef43-b6fd-45e1-91bb-61f43bcd7dc4.png)

为了便于分析，保留了三个阶段的解：初始解，LNS最小化车辆数，ALNS优化

![image](https://user-images.githubusercontent.com/67860270/162675824-8b9f3fbb-dffa-45d1-aa30-bed3185aaad2.png)

ALNS求解结果：可视化，解输出，算子得分曲线变化图，ALNS目标值变化曲线

# 数据结构说明

## 类 Algorithm_inputdata

参数：文件夹位置，订单的数量（该参数暂时不用）

属性说明：

Nodes_numpy：将dataframe转换为array，提高算法中访问节点各类信息的效率

# 类 Truck

参数：ID，卡车的最大载重，数据集中时间窗的最大值（一般就是depot的b值）

属性说明：

time_line：卡车离开某节点的时间

其余属性说明见代码注释
