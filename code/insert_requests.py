# -*- coding: utf-8 -*-
# @author: wangqianlong
# @email: 1763423314@qq.com
# @date: 2021/11/13
import copy

import numpy as np

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
                is_insert_pass_D, truck_for_Deliver_insert = order_insert_greedy(truck, Pickup, Deliver, algorithm_input_data)
                if is_insert_pass_D:
                    objective_change = truck_for_Deliver_insert.travel_distance_line_of_route[-1] - truck.travel_distance_line_of_route[-1]
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