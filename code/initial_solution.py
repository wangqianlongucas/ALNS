# -*- coding: utf-8 -*-
# @author: wangqianlong
# @email: 1763423314@qq.com
# @date: 2021/11/07

# 本模块为初始解生成代码
import random
import copy

import numpy as np

from algorithm_data import Algorithm_inputdata, Truck
from insert_order import order_insert_simple_in_order, order_insert_greedy, order_insert_random
from removal_requests import *
from insert_requests import *

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

def LNS(solution, q, request_blank, num_of_iter, algorithm_input_data):
    best_solution = solution
    best_objective = np.Inf
    best_request_blank = request_blank
    iter = 1
    while iter <= num_of_iter:
        iter += 1
        current_solution = copy.deepcopy(best_solution)
        # 订单移除
        q_orders, removal_solution = random_removal(current_solution, q, algorithm_input_data)
        # 订单插入
        insert_orders = request_blank + q_orders
        request_blank, insert_solution = greedy_insert(removal_solution, insert_orders, algorithm_input_data)
        current_objective = sum(truck.travel_distance_line_of_route[-1] for truck in list(insert_solution.values())) + algorithm_input_data.M * len(request_blank)
        if current_objective <= best_objective:
            best_objective = current_objective
            best_solution = insert_solution
            best_request_blank = request_blank

    return best_request_blank, best_solution




# second_stage
def second_stage(algorithm_input_data,solution):
    is_continue = 1
    best_solution = solution
    current_solution = copy.deepcopy(solution)
    while is_continue:
        list_truck_ID = list(current_solution.keys())
        truck_ID_to_delete = random.choice(list_truck_ID)
        truck_to_delete = current_solution[truck_ID_to_delete]
        order_blank = truck_to_delete.order
        del current_solution[truck_ID_to_delete]
        LNS_request_blank, LNS_solution = LNS(current_solution, 3, order_blank, 10, algorithm_input_data)
        if LNS_request_blank:
            is_continue = 0
        else:
            best_solution = LNS_solution
            current_solution = copy.deepcopy(best_solution)
    return best_solution


# test_first_stage pass
solution = {}
first_stage(algorithm_input_data, solution)

second_stage_solution = second_stage(algorithm_input_data,solution)
# test order remove  pass
# truck = copy.deepcopy(solution[1])
#
# node_remove = 9
# node_remove_index = truck.route.index(node_remove)
# truck.route.remove(node_remove)
# truck.travel_distance_line_of_route_update_remove(node_remove_index, algorithm_input_data)
# truck.check_and_update(node_remove_index, algorithm_input_data)
# test_second_stage

q_orders, removal_solution = random_removal(copy.deepcopy(solution), 3, algorithm_input_data)
request_blank, insert_solution = greedy_insert(removal_solution, q_orders, algorithm_input_data)