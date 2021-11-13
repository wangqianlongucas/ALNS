# -*- coding: utf-8 -*-
# @author: wangqianlong
# @email: 1763423314@qq.com
# @date: 2021/11/07

# 本模块为初始解生成代码
import random
import copy

from algorithm_data import Algorithm_inputdata, Truck
from insert_order import order_insert_simple_in_order, order_insert_greedy, order_insert_random

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
        truck_IDs = list(solution.keys())
        while truck_IDs:
            truck_ID = random.choice(truck_IDs)
            truck_IDs.remove(truck_ID)
            truck = solution[truck_ID]
            # 先插入 Pickup
            # # 简单顺序插入
            # is_insert_pass_P, is_insert_pass_D, truck_for_Deliver_insert = order_insert_simple_in_order(truck, Pickup, Deliver, algorithm_input_data)
            # 随机插入
            is_insert_pass_P, is_insert_pass_D, truck_for_Deliver_insert = order_insert_random(truck, Pickup, Deliver, algorithm_input_data)
            # # 贪心插入
            # is_insert_pass_D, truck_for_Deliver_insert = order_insert_greedy(truck, Pickup, Deliver, algorithm_input_data)
            if is_insert_pass_D:
                truck_for_Deliver_insert.order.append(order)
                solution[truck_ID] = truck_for_Deliver_insert
                orders.remove(order)
                break  # 结束truck插入循环
        # 如果所有的车辆均无法插入
        if not is_insert_pass_D:
            # 此时现有车辆均无法插入需求 order，需要新增加truck
            truck_ID_MAX += 1
            truck_new = Truck(truck_ID_MAX)
            is_insert_pass_P, is_insert_pass_D, truck_new_for_Deliver_insert = order_insert_simple_in_order(truck_new, Pickup, Deliver, algorithm_input_data)

            if is_insert_pass_D:
                truck_new_for_Deliver_insert.order.append(order)
                solution[truck_ID_MAX] = truck_new_for_Deliver_insert
                orders.remove(order)
            else:
                print(order, 'data时间设置不合理——时间窗')
                if not is_insert_pass_P:
                    print(order, 'data时间设置不合理——从卡车出发点至Pickup点')

# second_stage
def second_stage(algorithm_input_data,solution):
    is_continue = 1
    while is_continue:
        list_truck_ID = solution.keys()
        truck_to_delete = random.choice(list_truck_ID)
        order_blank = truck_to_delete.order



# test_first_stage pass
solution = {}
first_stage(algorithm_input_data, solution)

# test order remove  pass
truck = copy.deepcopy(solution[1])

node_remove = 9
node_remove_index = truck.route.index(node_remove)
truck.route.remove(node_remove)
truck.travel_distance_line_of_route_update_remove(node_remove_index, algorithm_input_data)
truck.check_and_update(node_remove_index, algorithm_input_data)
# test_second_stage
