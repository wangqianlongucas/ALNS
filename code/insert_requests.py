# -*- coding: utf-8 -*-
# @author: wangqianlong
# @email: 1763423314@qq.com
# @date: 2021/11/13
import copy

import numpy as np
import pandas as pd
from insert_order import *


def greedy_insert(solution, request_blank, algorithm_input_data):
    # 初始化
    insert_solution = copy.deepcopy(solution)
    insert_orders = copy.deepcopy(request_blank)
    best_insert_solution = insert_solution
    is_continue = 1 if request_blank else 0
    while is_continue:
        # 插入订单初始化
        best_insert_order = None
        best_objective_change = np.Inf
        best_insert_solution_order = best_insert_solution  # todo 此处变量赋值可能有问题
        # 遍历所有的订单选择最好的订单插入
        for order in insert_orders:
            # 重置当前解
            current_insert_solution_order = copy.deepcopy(best_insert_solution)
            Pickup = algorithm_input_data.OAs.loc[order, 'Pickup']
            Deliver = algorithm_input_data.OAs.loc[order, 'Deliver']
            for truck_ID, truck in current_insert_solution_order.items():
                # 重置当前解
                current_insert_solution_order_truck = copy.deepcopy(current_insert_solution_order)
                # 插入方式选择 贪心插入
                is_insert_pass_D, truck_for_Deliver_insert = order_insert_greedy(truck, Pickup, Deliver,
                                                                                 algorithm_input_data)
                if is_insert_pass_D:
                    objective_change = truck_for_Deliver_insert.travel_distance_line_of_route[-1] - \
                                       truck.travel_distance_line_of_route[-1]
                    truck_for_Deliver_insert.order.append(order)
                    if objective_change <= best_objective_change:
                        best_objective_change = objective_change
                        best_insert_order = order
                        # 此处注意
                        current_insert_solution_order_truck[truck_ID] = truck_for_Deliver_insert
                        best_insert_solution_order = current_insert_solution_order_truck

        if best_insert_order:
            insert_orders.remove(best_insert_order)
            best_insert_solution = best_insert_solution_order
        else:
            is_continue = 0
            request_blank = insert_orders
    return request_blank, best_insert_solution


def delta_f_i_x_ik_calculate(solution, request_blank, algorithm_input_data):
    # 初始化
    insert_solution = copy.deepcopy(solution)
    columns_name = ['order', 'truck_id_P_D', 'cost', 'truck']
    delta_f_i_x_ik_data = []
    for order in request_blank:
        Pickup = algorithm_input_data.OAs.loc[order, 'Pickup']
        Deliver = algorithm_input_data.OAs.loc[order, 'Deliver']
        for truck_ID, truck in insert_solution.items():
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
                    truck_for_Pickup_insert.travel_distance_line_of_route_update_insert(position_P,
                                                                                        algorithm_input_data)
                    Deliver_insert_positions = list(range(position_P + 1, len(truck_for_Pickup_insert.route)))
                    # 按前后顺序插入
                    for position_D in Deliver_insert_positions:
                        # 复制一份做插入测试
                        truck_for_Deliver_insert = copy.deepcopy(truck_for_Pickup_insert)
                        truck_for_Deliver_insert.route.insert(position_D, Deliver)
                        # 时间线计算和检查
                        is_insert_pass_D = truck_for_Deliver_insert.check_and_update(position_D, algorithm_input_data)

                        if is_insert_pass_D:
                            truck_for_Deliver_insert.order.append(order)
                            # 更新行驶距离参数
                            truck_for_Deliver_insert.travel_distance_line_of_route_update_insert(position_D,
                                                                                                 algorithm_input_data)
                            second_objective = truck_for_Deliver_insert.travel_distance_line_of_route[-1]
                            delta_f_i_x_ik_data.append(
                                [order, (truck_for_Deliver_insert.id, position_P, position_D),
                                 second_objective - truck.travel_distance_line_of_route[-1], truck_for_Deliver_insert])
    delta_f_i_x_ik = pd.DataFrame(delta_f_i_x_ik_data, columns=columns_name)
    return delta_f_i_x_ik


def regret_insert(solution, request_blank, regret_periods, algorithm_input_data):
    # regret_periods >=2 为后悔的期数
    # 初始化
    insert_solution = copy.deepcopy(solution)
    insert_orders = copy.deepcopy(request_blank)
    is_continue = 1 if request_blank else 0
    while is_continue:
        delta_f_i_x_ik = delta_f_i_x_ik_calculate(insert_solution, insert_orders, algorithm_input_data)
        if len(delta_f_i_x_ik):
            delta_f_i_x_ik_sorted = delta_f_i_x_ik.sort_values(['order', 'cost'], ascending=[True, True])
            c_i_star = {}
            for order in insert_orders:
                c_i_star_order = 0
                delta_f_i_x_ik_sorted_order = delta_f_i_x_ik_sorted[delta_f_i_x_ik_sorted['order'] == order]
                if len(delta_f_i_x_ik_sorted_order):
                    delta_f_i_x_ik_sorted_order.reset_index(inplace=True)
                    for regret_period in range(1, regret_periods):
                        c_i_star_order += - delta_f_i_x_ik_sorted_order.loc[0, 'cost'] \
                                          + delta_f_i_x_ik_sorted_order.loc[regret_period, 'cost'] if len(
                            delta_f_i_x_ik_sorted_order) > regret_period else delta_f_i_x_ik_sorted_order.loc[
                            len(delta_f_i_x_ik_sorted_order) - 1, 'cost']

                c_i_star[order] = c_i_star_order
            # 排序,升序，数据类为[()...]
            c_i_star_sorted = sorted(c_i_star.items(), key=lambda kv: (kv[1], kv[0]))
            best_order = c_i_star_sorted[-1][0]
            delta_f_i_x_ik_sorted_best_order = delta_f_i_x_ik_sorted[delta_f_i_x_ik_sorted['order'] == best_order]
            delta_f_i_x_ik_sorted_best_order.reset_index(inplace=True)
            # todo error
            best_truck = delta_f_i_x_ik_sorted_best_order.loc[0, 'truck']
            insert_orders.remove(best_order)
            insert_solution[best_truck.id] = best_truck
        else:
            is_continue = 0
    return insert_orders, insert_solution
