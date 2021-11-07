# -*- coding: utf-8 -*-
# @author: wangqianlong
# @email: 1763423314@qq.com
# @date: 2021/11/07

# 本模块为初始解生成代码
import random

from algorithm_data import Algorithm_inputdata, Truck
import copy

path_of_file = '..//data'
algorithm_input_data = Algorithm_inputdata(path_of_file)

# first_stage
def first_stage(algorithm_input_data,solution):
    orders = list(algorithm_input_data.OAs.loc[:, 'Pickup'])
    truck_ID_MAX = 1
    truck = Truck(truck_ID_MAX)
    solution[truck_ID_MAX] = truck
    while orders:
        # 随机选择订单
        order = random.choice(orders)
        Pickup = algorithm_input_data.OAs.loc[order,'Pickup']
        Deliver = algorithm_input_data.OAs.loc[order, 'Deliver']
        is_insert_pass_D = 0
        # 先插入 Pickup
        for truck_ID, truck in solution.items():
            Pickup_insert_positions = list(range(1, len(truck.route)))
            # 此处和下面Deliver插入均可改为随机插入
            for position_P in Pickup_insert_positions:
                # 复制一份做插入测试
                truck_for_Pickup_insert = copy.deepcopy(truck)
                truck_for_Pickup_insert.route.insert(position_P, Pickup)
                # 时间线计算和检查
                is_insert_pass_P = truck_for_Pickup_insert.time_line_update(position_P, algorithm_input_data)

                if is_insert_pass_P:
                    Deliver_insert_positions = list(range(position_P + 1, len(truck_for_Pickup_insert.route)))
                    for position_D in Deliver_insert_positions:
                        # 复制一份做插入测试
                        truck_for_Deliver_insert = copy.deepcopy(truck_for_Pickup_insert)
                        truck_for_Deliver_insert.route.insert(position_D, Deliver)
                        # 时间线计算和检查
                        is_insert_pass_D = truck_for_Deliver_insert.time_line_update(position_D, algorithm_input_data)

                        if is_insert_pass_D:
                            truck_for_Deliver_insert.order.append(order)
                            solution[truck_ID] = truck_for_Deliver_insert
                            orders.remove(order)
                            break  # 结束Deliver插入循环
                if is_insert_pass_D:
                    break  # 结束Pickup插入循环
            if is_insert_pass_D:
                break  # 结束truck插入循环
        # 如果所有的车辆均无法插入
        if not is_insert_pass_D:
            # 此时现有车辆均无法插入需求 order，需要新增加truck
            truck_ID_MAX += 1
            truck_new = Truck(truck_ID_MAX)
            truck_new.route.insert(1,Pickup)
            is_insert_pass_P = truck_new.time_line_update(1, algorithm_input_data)
            if is_insert_pass_P:
                truck_new.route.insert(2, Deliver)
                is_insert_pass_D = truck_new.time_line_update(2, algorithm_input_data)
                if is_insert_pass_D:
                    truck_new.order.append(order)
                    solution[truck_ID_MAX] = truck_new
                    orders.remove(order)
                else:
                    print(order, 'data时间设置不合理——时间窗')
            else:
                print(order, 'data时间设置不合理——从卡车出发点至Pickup点')

# test_first_stage
solution = {}
first_stage(algorithm_input_data, solution)