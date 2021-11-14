# -*- coding: utf-8 -*-
# @author: wangqianlong
# @email: 1763423314@qq.com
# @date: 2021/11/07

# 本模块为初始解生成代码
import random
import copy
import math

import numpy as np

from algorithm_data import Algorithm_inputdata, Truck
from insert_order import *
from removal_requests import *
from insert_requests import *

# first_stage
def first_stage(algorithm_input_data):
    # 初始化
    solution = {}
    orders = list(algorithm_input_data.OAs.loc[:, 'Pickup'])
    # 创建第一辆车
    truck_ID_MAX = 1
    truck = Truck(truck_ID_MAX)
    solution[truck_ID_MAX] = truck
    # 安排订单
    while orders:
        # 随机选择订单
        order = random.choice(orders)
        Pickup = algorithm_input_data.OAs.loc[order,'Pickup']
        Deliver = algorithm_input_data.OAs.loc[order, 'Deliver']
        is_insert_pass_D = 0
        truck_IDs = list(solution.keys())
        while truck_IDs:
            # 随机选择车辆
            truck_ID = random.choice(truck_IDs)
            truck_IDs.remove(truck_ID)
            truck = solution[truck_ID]
            # # 简单顺序插入
            # is_insert_pass_P, is_insert_pass_D, truck_for_Deliver_insert = order_insert_simple_in_order(truck, Pickup, Deliver, algorithm_input_data)
            # 随机插入
            is_insert_pass_P, is_insert_pass_D, truck_for_Deliver_insert = order_insert_random(truck, Pickup, Deliver, algorithm_input_data)
            # # 贪心插入
            # is_insert_pass_D, truck_for_Deliver_insert = order_insert_greedy(truck, Pickup, Deliver, algorithm_input_data)
            if is_insert_pass_D:  # 插入成功
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
    return solution

def LNS(solution, q, request_blank, num_of_iter, algorithm_input_data):
    # 初始化
    current_solution = copy.deepcopy(solution)
    current_objective = 1e5
    current_request_blank = copy.deepcopy(request_blank)
    best_solution = current_solution
    best_objective = current_objective
    best_request_blank = current_request_blank
    # 初最高温
    T_MAX = 10 * (sum(truck.travel_distance_line_of_route[-1] for truck in list(best_solution.values())) + algorithm_input_data.M * len(request_blank))
    T_MIN = 1
    iter = 1
    while iter <= num_of_iter or T_MAX <= T_MIN:
        # 订单移除
        removal_orders, removal_solution = random_removal(current_solution, q, algorithm_input_data)
        # 订单插入
        insert_orders = current_request_blank + removal_orders
        insert_request_blank, insert_solution = greedy_insert(removal_solution, insert_orders, algorithm_input_data)
        # 计算目标
        insert_objective = sum(truck.travel_distance_line_of_route[-1] for truck in list(insert_solution.values())) + algorithm_input_data.M * len(request_blank)
        # 更新最优解
        if insert_objective <= best_objective:
            best_objective = insert_objective
            best_solution = insert_solution
            best_request_blank = insert_request_blank
        # 模拟退火接受准则更新当前解
        if insert_objective <= current_objective:
            current_solution = insert_solution
            current_objective = insert_objective
            current_request_blank = insert_request_blank
        else:
            insert_accept_sa = random.random()
            if insert_accept_sa <= math.exp(-(insert_objective - current_objective) / T_MAX):
                current_solution = insert_solution
                current_objective = insert_objective
                current_request_blank = insert_request_blank
        iter += 1
        T_MAX = T_MAX * 0.95

    return best_request_blank, best_solution

# second_stage
def second_stage(algorithm_input_data,solution):
    # 初始化
    second_solution = copy.deepcopy(solution)
    is_continue = 1 if len(list(second_solution.keys())) > 1 else 0
    while is_continue:
        list_truck_ID = list(second_solution.keys())
        while list_truck_ID:
            # 重置 当前解
            second_solution_to_delete = copy.deepcopy(second_solution)
            # 选择移除车辆
            truck_ID_to_delete = random.choice(list_truck_ID)
            list_truck_ID.remove(truck_ID_to_delete)
            truck_to_delete = second_solution_to_delete[truck_ID_to_delete]
            # 建立request_blank 和 移除车辆和的部分解
            request_blank = truck_to_delete.order
            del second_solution_to_delete[truck_ID_to_delete]
            # 使用 LNS 算法安排request_blank中的订单
            LNS_request_blank, LNS_solution = LNS(second_solution_to_delete, 3, request_blank, 10, algorithm_input_data)
            # 如果所有订单均被安排——>break
            if not LNS_request_blank:
                second_solution = LNS_solution
                break
        # 如果循环到最后一辆车，LNS_request_blank仍不为空 或者只有一辆车——>break
        if LNS_request_blank or len(list(second_solution.keys())) <= 1:
            is_continue = 0

    return second_solution


if __name__ == '__main__' :
    path_of_file = '..//data'
    algorithm_input_data = Algorithm_inputdata(path_of_file)
    # test_first_stage pass
    first_stage_solution = first_stage(algorithm_input_data)
    first_stage_solution[10] = Truck(10)
    # test_second_stage pass
    second_stage_solution = second_stage(algorithm_input_data, first_stage_solution)

    print('finish')
