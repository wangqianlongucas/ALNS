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
        new_choice = int((y ** p) * len(relatedness_i_with_any_sorted))
        D.append(relatedness_i_with_any_sorted[new_choice][0])
    # step 2 移除订单
    solution_shaw = order_removal(solution, D, algorithm_input_data)
    return D, solution_shaw


def worst_removal(solution, q, p, algorithm_input_data):
    p = p
    removal_solution = copy.deepcopy(solution)
    # 记录所有移除的订单
    q_orders = []
    # 记录所有order的的cost
    all_order_cost = []
    #  数据结构为[{truck_id:[order_id,order removal cost]}]
    #  为了计算简便数据结构变更为[[truck_id,order_id,order removal cost]]
    for truck_id, truck_values in solution.items():
        # print('truck_ID:', truck_id)
        # print('当前车辆的索引为:', truck_id)
        truck_distance_before = truck_values.travel_distance_line_of_route[-1]
        # print('当前卡车行驶的距离：', truck_distance_before)
        for ii in truck_values.order:
            # 索引
            # print('%s车辆的订单为' % truck_id, ii)
            truck_values_can_change = copy.deepcopy(truck_values)
            # 计算去掉该点之后的卡车行驶距离
            Pickup = algorithm_input_data.OAs.loc[ii, 'Pickup']
            Pickup_position = truck_values_can_change.route.index(Pickup)
            truck_values_can_change.route.remove(Pickup)
            truck_values_can_change.travel_distance_line_of_route_update_remove(Pickup_position, algorithm_input_data)
            truck_distance_after_pickup = truck_values_can_change.travel_distance_line_of_route[-1]
            # print('去掉订单%s的pickup点后车辆%s的行驶距离为' % (ii, truck_id), truck_distance_after_pickup)
            Deliver = algorithm_input_data.OAs.loc[ii, 'Deliver']
            Deliver_position = truck_values_can_change.route.index(Deliver)
            truck_values_can_change.route.remove(Deliver)
            truck_values_can_change.travel_distance_line_of_route_update_remove(Deliver_position, algorithm_input_data)
            truck_distance_after = truck_values_can_change.travel_distance_line_of_route[-1]
            # print('去掉订单%s后车辆%s的行驶距离为' % (ii, truck_id), truck_distance_after)
            cost_ii = [truck_id, ii, truck_distance_before - truck_distance_after]
            all_order_cost.append(cost_ii)
        # truck_cost_dict[truck_id]=each_truck_cost
        # all_order_cost.append(truck_cost_dict)
    # print('未排序前的cost：', all_order_cost)
    # 按照cost值从小到大排序
    all_order_cost = sorted(all_order_cost, key=(lambda x: x[2]))
    # print('排序后的cost：', all_order_cost)
    planned_order = [all_order_cost[i][1] for i in range(len(all_order_cost))]
    # print('排序好的已经规划的订单：', planned_order)

    while len(q_orders) < q:
        # 随机生成一个[0,1)之间的小数
        y = random.random()
        # 目前已经规划好的订单
        # 在已经排好序的订单中随机选择车辆 索引是在排序好的订单里得到的
        order_index = int((y ** p) * len(planned_order))
        q_order = planned_order[order_index]
        # print('打算移除的order为：',q_order)
        truck_id_to_remove_order = all_order_cost[order_index][0]
        # print('打算移除的order所在的车辆为：',truck_id_to_remove_order)
        q_orders.append(q_order)
        all_order_cost.pop(order_index)
        # 移除当前选中的订单
        planned_order.remove(q_order)
        # truck_remove_order = random.choice(list(removal_solution.values()))
        truck_remove_order = removal_solution[truck_id_to_remove_order]
        # print(truck_remove_order)
        # 订单移除
        if truck_remove_order.order:
            # print('第188行的order：',truck_remove_order.order)
            # 随机选择订单
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
            # removal_solution[truck_remove_order.id] = truck_remove_order
            removal_solution[truck_id_to_remove_order] = truck_remove_order

            # 更新cost列表
            truck_values = truck_remove_order
            truck_id = truck_id_to_remove_order
            truck_distance_before = truck_values.travel_distance_line_of_route[-1]
            for ii in truck_values.order:
                # 索引
                # print('%s车辆的订单为' % truck_id, ii)
                truck_values_can_change = copy.deepcopy(truck_values)
                # 计算去掉该点之后的卡车行驶距离
                Pickup = algorithm_input_data.OAs.loc[ii, 'Pickup']
                Pickup_position = truck_values_can_change.route.index(Pickup)
                truck_values_can_change.route.remove(Pickup)
                truck_values_can_change.travel_distance_line_of_route_update_remove(Pickup_position,
                                                                                    algorithm_input_data)
                truck_distance_after_pickup = truck_values_can_change.travel_distance_line_of_route[-1]
                # print('去掉订单%s的pickup点后车辆%s的行驶距离为' % (ii, truck_id), truck_distance_after_pickup)
                Deliver = algorithm_input_data.OAs.loc[ii, 'Deliver']
                Deliver_position = truck_values_can_change.route.index(Deliver)
                truck_values_can_change.route.remove(Deliver)
                truck_values_can_change.travel_distance_line_of_route_update_remove(Deliver_position,
                                                                                    algorithm_input_data)
                truck_distance_after = truck_values_can_change.travel_distance_line_of_route[-1]
                # print('去掉订单%s后车辆%s的行驶距离为' % (ii, truck_id), truck_distance_after)
                cost_ii_change = truck_distance_before - truck_distance_after
                index_order = planned_order.index(ii)
                all_order_cost[index_order][2] = cost_ii_change
            # print('未排序前的cost：', all_order_cost)
            # 按照cost值从小到大排序
            all_order_cost = sorted(all_order_cost, key=(lambda x: x[2]))
            # print('排序后的cost：', all_order_cost)
            planned_order = [all_order_cost[i][1] for i in range(len(all_order_cost))]
    return q_orders, removal_solution
