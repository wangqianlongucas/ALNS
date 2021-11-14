# -*- coding: utf-8 -*-
# @author: wangqianlong
# @email: 1763423314@qq.com
# @date: 2021/11/08

# 此模块定义单个需求插入方式
import copy
import random

# 简单顺序插入
import numpy as np


def order_insert_simple_in_order(truck,Pickup,Deliver,algorithm_input_data):
    is_insert_pass_D = 0
    Pickup_insert_positions = list(range(1, len(truck.route)))
    # 按前后顺序插入
    for position_P in Pickup_insert_positions:
        # 复制一份做插入测试
        truck_for_Pickup_insert = copy.deepcopy(truck)
        truck_for_Pickup_insert.route.insert(position_P, Pickup)
        # 时间线计算和检查
        is_insert_pass_P = truck_for_Pickup_insert.check_and_update(position_P, algorithm_input_data)

        if is_insert_pass_P:
            # 更新行驶距离参数
            truck_for_Pickup_insert.travel_distance_line_of_route_update_insert(position_P, algorithm_input_data)
            Deliver_insert_positions = list(range(position_P + 1, len(truck_for_Pickup_insert.route)))
            # 按前后顺序插入
            for position_D in Deliver_insert_positions:
                # 复制一份做插入测试
                truck_for_Deliver_insert = copy.deepcopy(truck_for_Pickup_insert)
                truck_for_Deliver_insert.route.insert(position_D, Deliver)
                # 时间线计算和检查
                is_insert_pass_D = truck_for_Deliver_insert.check_and_update(position_D, algorithm_input_data)

                if is_insert_pass_D:
                    # 更新行驶距离参数
                    truck_for_Deliver_insert.travel_distance_line_of_route_update_insert(position_D, algorithm_input_data)
                    break  # 结束Deliver插入循环
        if is_insert_pass_D:
            break  # 结束Pickup插入循环
    return is_insert_pass_P, is_insert_pass_D, truck_for_Deliver_insert if is_insert_pass_D else truck

# 随机插入
def order_insert_random(truck,Pickup,Deliver,algorithm_input_data):
    is_insert_pass_D = 0
    Pickup_insert_positions = list(range(1, len(truck.route)))
    # 随机插入
    while Pickup_insert_positions:
        position_P = random.choice(Pickup_insert_positions)
        Pickup_insert_positions.remove(position_P)
        # 复制一份做插入测试
        truck_for_Pickup_insert = copy.deepcopy(truck)
        truck_for_Pickup_insert.route.insert(position_P, Pickup)
        # 时间线计算和检查
        is_insert_pass_P = truck_for_Pickup_insert.check_and_update(position_P, algorithm_input_data)

        if is_insert_pass_P:
            # 更新行驶距离参数
            truck_for_Pickup_insert.travel_distance_line_of_route_update_insert(position_P, algorithm_input_data)
            Deliver_insert_positions = list(range(position_P + 1, len(truck_for_Pickup_insert.route)))
            while Deliver_insert_positions:
                position_D = random.choice(Deliver_insert_positions)
                Deliver_insert_positions.remove(position_D)
                # 复制一份做插入测试
                truck_for_Deliver_insert = copy.deepcopy(truck_for_Pickup_insert)
                truck_for_Deliver_insert.route.insert(position_D, Deliver)
                # 时间线计算和检查
                is_insert_pass_D = truck_for_Deliver_insert.check_and_update(position_D, algorithm_input_data)

                if is_insert_pass_D:
                    # 更新行驶距离参数
                    truck_for_Deliver_insert.travel_distance_line_of_route_update_insert(position_D, algorithm_input_data)
                    break  # 结束Deliver插入循环
        if is_insert_pass_D:
            break  # 结束Pickup插入循环
    return is_insert_pass_P, is_insert_pass_D, truck_for_Deliver_insert if is_insert_pass_D else truck

# 寻找最好的插入位置：second_objective

def order_insert_greedy(truck,Pickup,Deliver,algorithm_input_data):
    # 初始化
    truck_best = truck
    second_objective_best = np.Inf
    is_insert_pass_Ds = [0]

    Pickup_insert_positions = list(range(1, len(truck.route)))
    # 按前后顺序插入
    for position_P in Pickup_insert_positions:
        # 复制一份做插入测试
        truck_for_Pickup_insert = copy.deepcopy(truck)
        truck_for_Pickup_insert.route.insert(position_P, Pickup)
        # 时间线计算和检查
        is_insert_pass_P = truck_for_Pickup_insert.check_and_update(position_P, algorithm_input_data)

        if is_insert_pass_P:
            # 更新行驶距离参数
            truck_for_Pickup_insert.travel_distance_line_of_route_update_insert(position_P, algorithm_input_data)
            Deliver_insert_positions = list(range(position_P + 1, len(truck_for_Pickup_insert.route)))
            # 按前后顺序插入
            for position_D in Deliver_insert_positions:
                # 复制一份做插入测试
                truck_for_Deliver_insert = copy.deepcopy(truck_for_Pickup_insert)
                truck_for_Deliver_insert.route.insert(position_D, Deliver)
                # 时间线计算和检查
                is_insert_pass_D = truck_for_Deliver_insert.check_and_update(position_D, algorithm_input_data)

                if is_insert_pass_D:
                    # 更新行驶距离参数
                    truck_for_Deliver_insert.travel_distance_line_of_route_update_insert(position_D, algorithm_input_data)
                    second_objective = truck_for_Deliver_insert.travel_distance_line_of_route[-1]
                    if second_objective <= second_objective_best:
                        second_objective_best = second_objective
                        truck_best = truck_for_Deliver_insert
                        is_insert_pass_Ds.append(is_insert_pass_D)
    return max(is_insert_pass_Ds), truck_best