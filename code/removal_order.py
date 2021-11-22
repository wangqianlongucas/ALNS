# -*- coding: utf-8 -*-
# @author: wangqianlong
# @email: 1763423314@qq.com
# @date: 2021/11/22
import copy


def order_removal(solution, orders, algorithm_input_data):
    removal_solution = copy.deepcopy(solution)
    for order in orders:
        Pickup = algorithm_input_data.OAs.loc[order, 'Pickup']
        for truck_ID, truck in removal_solution.items():
            if Pickup in truck.route:
                truck_remove_order = copy.deepcopy(truck)
                truck_remove_order.order.remove(order)
                Pickup_position = truck_remove_order.route.index(Pickup)
                truck_remove_order.route.remove(Pickup)
                truck_remove_order.travel_distance_line_of_route_update_remove(Pickup_position, algorithm_input_data)

                Deliver = algorithm_input_data.OAs.loc[order, 'Deliver']
                Deliver_position = truck_remove_order.route.index(Deliver)
                truck_remove_order.route.remove(Deliver)
                truck_remove_order.travel_distance_line_of_route_update_remove(Deliver_position, algorithm_input_data)
                # 时间和载重线更新
                truck_remove_order.check_and_update(Pickup_position, algorithm_input_data)
                removal_solution[truck_ID] = truck_remove_order
    return removal_solution
