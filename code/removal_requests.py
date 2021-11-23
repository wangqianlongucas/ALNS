# -*- coding: utf-8 -*-
# @author: wangqianlong
# @email: 1763423314@qq.com
# @date: 2021/11/13

import random
import copy
from removal_order import *


def random_removal(solution, q, algorithm_input_data):
    removal_solution = copy.deepcopy(solution)
    q_orders = []
    while len(q_orders) < q:
        # 随机选择车辆
        truck_remove_order = random.choice(list(removal_solution.values()))
        # 订单移除
        if truck_remove_order.order:
            # 随机选择订单
            q_order = random.choice(truck_remove_order.order)
            q_orders.append(q_order)
            truck_remove_order.order.remove(q_order)
            # 更新其他参数
            Pickup = algorithm_input_data.OAs.loc[q_order, 'Pickup']
            Pickup_position = truck_remove_order.route.index(Pickup)
            truck_remove_order.route.remove(Pickup)
            truck_remove_order.travel_distance_line_of_route_update_remove(Pickup_position, algorithm_input_data)

            Deliver = algorithm_input_data.OAs.loc[q_order, 'Deliver']
            Deliver_position = truck_remove_order.route.index(Deliver)
            truck_remove_order.route.remove(Deliver)
            truck_remove_order.travel_distance_line_of_route_update_remove(Deliver_position, algorithm_input_data)
            # 时间和载重线更新
            truck_remove_order.check_and_update(Pickup_position, algorithm_input_data)

            removal_solution[truck_remove_order.id] = truck_remove_order

    return q_orders, removal_solution


def relatedness_calculate_all(solution, algorithm_input_data):
    # 输入解（完整解），参数
    relatedness = {}
    orders = algorithm_input_data.orders
    for order_i in orders:
        relatedness_i_with_any = {}
        for order_j in orders:
            if order_j != order_i:
                locations = {'A_i': algorithm_input_data.OAs.loc[order_i, 'Pickup'],
                             'B_i': algorithm_input_data.OAs.loc[order_j, 'Pickup'],
                             'A_j': algorithm_input_data.OAs.loc[order_i, 'Deliver'],
                             'B_j': algorithm_input_data.OAs.loc[order_j, 'Deliver'],
                             }
                relatedness_d = algorithm_input_data.Distance_Mat[locations['A_i'], locations['B_i']] + \
                                algorithm_input_data.Distance_Mat[locations['A_j'], locations['B_j']]
                T = {}
                for truck_ID, truck in solution.items():
                    for location_key, location in locations.items():
                        if location in truck.route:
                            location_index = truck.route.index(location)
                            T[location_key] = truck.time_line[location_index]
                relatedness_T = abs(T['A_i'] - T['A_j']) + abs(T['B_i'] - T['B_j'])
                relatedness_l = abs(
                    algorithm_input_data.Nodes.loc[order_i, 'dm'] - algorithm_input_data.Nodes.loc[order_j, 'dm'])
                relatedness_K = 0  # todo 未异质化订单
                relatedness_i_with_any[order_j] = algorithm_input_data.weight['d'] * relatedness_d + \
                                                  algorithm_input_data.weight['T'] * relatedness_T \
                                                  + algorithm_input_data.weight['l'] * relatedness_l + \
                                                  algorithm_input_data.weight['K'] * relatedness_K
        relatedness[order_i] = relatedness_i_with_any
    return relatedness


def relatedness_calculate(solution, order_i, algorithm_input_data):
    # 输入解（完整解），参数
    orders = algorithm_input_data.orders
    relatedness_i_with_any = {}
    for order_j in orders:
        if order_j != order_i:
            locations = {'A_i': algorithm_input_data.OAs.loc[order_i, 'Pickup'],
                         'B_i': algorithm_input_data.OAs.loc[order_j, 'Pickup'],
                         'A_j': algorithm_input_data.OAs.loc[order_i, 'Deliver'],
                         'B_j': algorithm_input_data.OAs.loc[order_j, 'Deliver'],
                         }
            relatedness_d = algorithm_input_data.Distance_Mat[locations['A_i'], locations['B_i']] + \
                            algorithm_input_data.Distance_Mat[locations['A_j'], locations['B_j']]
            T = {}
            for truck_ID, truck in solution.items():
                for location_key, location in locations.items():
                    if location in truck.route:
                        location_index = truck.route.index(location)
                        T[location_key] = truck.time_line[location_index]
            if 'B_i' not in T.keys():
                continue
            relatedness_T = abs(T['A_i'] - T['A_j']) + abs(T['B_i'] - T['B_j'])
            relatedness_l = abs(
                algorithm_input_data.Nodes.loc[order_i, 'dm'] - algorithm_input_data.Nodes.loc[order_j, 'dm'])
            relatedness_K = 0  # todo 未异质化订单
            relatedness_i_with_any[order_j] = algorithm_input_data.weight['d'] * relatedness_d + \
                                              algorithm_input_data.weight['T'] * relatedness_T + \
                                              algorithm_input_data.weight['l'] * relatedness_l + \
                                              algorithm_input_data.weight['K'] * relatedness_K
    return relatedness_i_with_any


def shaw_removal(solution, q, p, algorithm_input_data):
    # step 1 选择移除订单集合
    orders = algorithm_input_data.orders
    r_order = random.choice(orders)
    D = [r_order]
    # relatedness = relatedness_calculate_all(solution, algorithm_input_data)
    while len(D) < q:
        i_relatedness = random.choice(D)
        relatedness_i_with_any = relatedness_calculate(solution, i_relatedness, algorithm_input_data)
        # 删除在D中的订单
        for order_d in D:
            if order_d in list(relatedness_i_with_any.keys()):
                del relatedness_i_with_any[order_d]
        # 排序,升序，数据类为[()...]
        relatedness_i_with_any_sorted = sorted(relatedness_i_with_any.items(), key=lambda kv: (kv[1], kv[0]))
        y = random.random()
        new_choice = int((y**p) * len(relatedness_i_with_any_sorted))
        D.append(relatedness_i_with_any_sorted[new_choice][0])
    # step 2 移除订单
    solution_shaw = order_removal(solution, D, algorithm_input_data)
    return D, solution_shaw
