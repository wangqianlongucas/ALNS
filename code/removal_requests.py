# -*- coding: utf-8 -*-
# @author: wangqianlong
# @email: 1763423314@qq.com
# @date: 2021/11/13

import random
import copy

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
