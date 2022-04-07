# -*- coding: utf-8 -*-
# @author: wangqianlong
# @email: 1763423314@qq.com
# @date: 2021/11/07

# 本代码文件包括数据结构定义、数据读取和处理
import pandas as pd
import numpy as np


class Truck():
    def __init__(self, ID, capacity_max, time_latest):
        self.id = ID
        self.capacity = capacity_max  # 最大载重
        self.origin = [0]
        self.end = [0]
        self.v = 1  # km/h
        # 以下为会修改的指标
        self.order = []
        self.route = self.origin + self.end
        self.time_line = [0, 0]
        self.capacity_line = [0, 0]
        self.travel_distance_line_of_route = [0, 0]
        # 定义时间窗检查辅助变量

        # # 对于点i，最早可能的完成服务的时间，从前往后计算，假设i点以前的点都能恰好在到达时刻（a<到达时刻）开始服务，到达i点的时间
        # self.earliest_possible_time = None  # 这个参数可能不必要，因为已经有时间线，可以直接用时间线计算？暂时不计算

        # 对于点i，最晚可能的开始服务的时间，从后往前计算，假设i点以后的点也能开始于时刻b或者后一个点的最晚开始时刻减去两点之间的行驶时间、服务时间
        # 初始化需要给最晚时间参数
        self.latest_possible_time = [time_latest, time_latest]  # min(i_b,(i+1)_latest_time - d_i,i+1 - i_service_time)

    def truck_copy(self):
        r_truck = Truck(self.id, self.capacity, None)
        r_truck.order = [i for i in self.order]
        r_truck.route = [i for i in self.route]
        r_truck.time_line = [i for i in self.time_line]
        r_truck.capacity_line = [i for i in self.capacity_line]
        r_truck.travel_distance_line_of_route = [i for i in self.travel_distance_line_of_route]
        r_truck.latest_possible_time = [i for i in self.latest_possible_time]
        return r_truck

    # this part is about time.
    def time_line_update(self, insert_position, algorithm_input_data):
        # 只需要更新插入位置及其后续位置的时间
        self.time_line = self.time_line[:insert_position]
        node_last = self.route[insert_position - 1]
        is_insert_pass = 1
        for node in self.route[insert_position:]:
            # 计算服务时间
            start_time = max(self.time_line[-1] + (algorithm_input_data.Distance_Mat[node_last, node]) / self.v,
                             algorithm_input_data.Nodes_numpy[node, 3])
            leave_time = start_time + algorithm_input_data.Nodes_numpy[node, 6]
            if start_time <= algorithm_input_data.Nodes_numpy[node, 4]:
                self.time_line.append(leave_time)
                node_last = node
            else:
                is_insert_pass = 0
                break
        return is_insert_pass

    # this is about insert.
    def latest_possible_time_update(self, insert_position, algorithm_input_data):
        # 只需要更新插入位置及其前续位置的时间
        self.latest_possible_time = self.latest_possible_time[insert_position:]
        node_after = self.route[insert_position + 1]
        for node in reversed(self.route[:insert_position + 1]):
            # 计算服务时间
            reverse_time = self.latest_possible_time[0] - algorithm_input_data.Distance_Mat[node, node_after] / self.v \
                           - algorithm_input_data.Nodes_numpy[node, 6]
            node_latest_possible_time = min(algorithm_input_data.Nodes_numpy[node, 4], reverse_time)
            self.latest_possible_time.insert(0, node_latest_possible_time)
            node_after = node

    # this is about initial.
    def latest_possible_time_initial(self, algorithm_input_data):
        # 从最后向前更新
        self.latest_possible_time = [algorithm_input_data.Nodes_numpy[self.route[-1], 4]]
        node_before = self.route[0]
        for node in reversed(self.route[:-1]):
            # 计算服务时间
            reverse_time = self.latest_possible_time[0] - algorithm_input_data.Distance_Mat[node, node_before] / self.v \
                           - algorithm_input_data.Nodes_numpy[node, 6]
            node_latest_possible_time = min(algorithm_input_data.Nodes_numpy[node, 4], reverse_time)
            self.latest_possible_time.insert(0, node_latest_possible_time)
            node_before = node

    # this is about removal.
    def latest_possible_time_removal(self, removal_position, algorithm_input_data):
        # 只需要更新移除位置及其前续位置的时间
        self.latest_possible_time = self.latest_possible_time[removal_position + 1:]
        node_after = self.route[removal_position]
        for node in reversed(self.route[:removal_position]):
            # 计算服务时间
            reverse_time = self.latest_possible_time[0] - algorithm_input_data.Distance_Mat[node, node_after] / self.v \
                           - algorithm_input_data.Nodes_numpy[node, 6]
            node_latest_possible_time = min(algorithm_input_data.Nodes_numpy[node, 4], reverse_time)
            self.latest_possible_time.insert(0, node_latest_possible_time)
            node_after = node

    # this part is about capacity.
    def capacity_line_update(self, insert_position, algorithm_input_data):
        is_insert_pass = 1
        self.capacity_line = self.capacity_line[:insert_position]
        for node in self.route[insert_position:]:
            node_capacity = self.capacity_line[-1] + algorithm_input_data.Nodes_numpy[node, 5]
            if node_capacity <= self.capacity:
                self.capacity_line.append(node_capacity)
            else:
                is_insert_pass = 0
                break
        return is_insert_pass

    # 以下两个函数测试通过
    def capacity_line_insert_pickup_update_and_check(self, insert_pickup_position, algorithm_input_data):
        is_insert_pass = 1
        pickup_node = self.route[insert_pickup_position]
        pickup_position_capacity = self.capacity_line[insert_pickup_position - 1] + algorithm_input_data.Nodes_numpy[
            pickup_node, 5]
        if pickup_position_capacity <= self.capacity:
            self.capacity_line.insert(insert_pickup_position, pickup_position_capacity)
        else:
            is_insert_pass = 0
        return is_insert_pass

    def capacity_line_insert_delivery_update_and_check(self, insert_pickup_position, insert_delivery_position,
                                                       algorithm_input_data):
        is_insert_pass = 1
        pickup_node, delivery_node = self.route[insert_pickup_position], self.route[insert_delivery_position]
        capacity_change_list = self.capacity_line[insert_pickup_position + 1:insert_delivery_position]
        # 检查是否可行
        if capacity_change_list:
            capacity_change_list = [algorithm_input_data.Nodes_numpy[pickup_node, 5] + capacity_change_list[i]
                                    for i in range(len(capacity_change_list))]
            if max(capacity_change_list) <= self.capacity:
                # 修改载重线
                self.capacity_line[insert_pickup_position + 1:insert_delivery_position] = capacity_change_list
                self.capacity_line.insert(insert_delivery_position,
                                          capacity_change_list[-1] + algorithm_input_data.Nodes_numpy[
                                              delivery_node, 5])
            else:
                is_insert_pass = 0
        else:
            self.capacity_line.insert(insert_delivery_position, self.capacity_line[insert_pickup_position - 1])
        return is_insert_pass

    def check_and_update(self, insert_position, algorithm_input_data, R_or_I='insert', insert_tpye='', Pickup_position=None):
        # R_or_I = 'test'
        # insert
        if R_or_I == 'insert':
            # 进行O(1)检查,计算insert_position两个指标：到达时间，最早可能的开始服务时间
            before_node, insert_node, after_node = self.route[insert_position - 1], self.route[insert_position], \
                                                   self.route[
                                                       insert_position + 1]
            # 加入node a
            arrival_time = max(self.time_line[insert_position - 1] + algorithm_input_data.Distance_Mat[
                before_node, insert_node], algorithm_input_data.Nodes_numpy[insert_node, 3])
            latest_time = min(
                self.latest_possible_time[insert_position] - algorithm_input_data.Distance_Mat[insert_node, after_node] \
                - algorithm_input_data.Nodes_numpy[insert_node, 6], algorithm_input_data.Nodes_numpy[insert_node, 4])
            if arrival_time > latest_time:
                return 0
            else:
                is_insert_pass_time = self.time_line_update(insert_position, algorithm_input_data)
                if is_insert_pass_time:
                    if insert_tpye == 'Pickup':
                        is_insert_pass_capacity = self.capacity_line_insert_pickup_update_and_check(insert_position,
                                                                                           algorithm_input_data)
                    else:
                        is_insert_pass_capacity = self.capacity_line_insert_delivery_update_and_check(Pickup_position, insert_position,
                                                                                                         algorithm_input_data)
                    return is_insert_pass_capacity
                else:
                    return is_insert_pass_time
        # removal
        is_insert_pass_time = self.time_line_update(insert_position, algorithm_input_data)
        if is_insert_pass_time:
            is_insert_pass_capacity = self.capacity_line_update(insert_position, algorithm_input_data)
            return is_insert_pass_capacity
        return is_insert_pass_time

    # this part is about travel distance.
    def travel_distance_line_of_route_update_insert(self, insert_position, algorithm_input_data):
        node_before, node, node_after = self.route[insert_position - 1], self.route[insert_position], self.route[
            insert_position + 1]
        # 插入新增点的行驶距离
        travel_node = self.travel_distance_line_of_route[insert_position - 1] + algorithm_input_data.Distance_Mat[
            node_before, node]
        self.travel_distance_line_of_route.insert(insert_position, travel_node)
        # 更新插入点后的行驶距离
        travel_change = algorithm_input_data.Distance_Mat[node, node_after] + algorithm_input_data.Distance_Mat[
            node_before, node] - algorithm_input_data.Distance_Mat[node_before, node_after]
        self.travel_distance_line_of_route[insert_position + 1:] = [travel + travel_change for travel in
                                                                    self.travel_distance_line_of_route[
                                                                    insert_position + 1:]]

    def travel_distance_line_of_route_update_remove(self, remove_position, algorithm_input_data):
        del self.travel_distance_line_of_route[remove_position]
        node_before, node = self.route[remove_position - 1], self.route[remove_position]
        travel_node = self.travel_distance_line_of_route[remove_position - 1] + algorithm_input_data.Distance_Mat[
            node_before, node]
        travel_change = self.travel_distance_line_of_route[remove_position] - travel_node
        # 更新移除点后的行驶距离
        self.travel_distance_line_of_route[remove_position:] = [travel - travel_change for travel in
                                                                self.travel_distance_line_of_route[remove_position:]]


class Algorithm_inputdata():
    # 初始化：读取数据和生成参数
    def __init__(self, path_of_file, number_of_orders):
        # 读取订单数据和节点数据
        # self.OAs = pd.read_csv(path_of_file + '\\OAs%s.csv'%number_of_orders, index_col=0)
        self.OAs = pd.read_csv(path_of_file + '\\OAs.csv', index_col=0)
        self.orders = list(self.OAs.loc[:, 'Pickup'])
        # Nodes[0]表示卡车出发点
        # self.Nodes = pd.read_csv(path_of_file + '\\Nodes%s.csv'%number_of_orders)
        self.Nodes = pd.read_csv(path_of_file + '\\Nodes.csv')
        self.Nodes_numpy = self.Nodes.values
        # 计算距离矩阵
        self.Distance_Mat = self.distance_matrix(self.Nodes)
        # 惩罚
        self.M = 800
        # 相似度系数
        self.weight = {'d': 9, 'T': 3, 'l': 2, 'K': 5}
        # self.sita = {'sita_1': 33, 'sita_2': 9, 'sita_3': 13}
        self.sita = {'sita_1': 0.4, 'sita_2': 0.3, 'sita_3': 0.2}

    def distance_matrix(self, pd_data):
        list_include_index_etc = pd_data.values
        mat_include_index_etc = np.matrix(list_include_index_etc)
        # 横纵坐标向量，此处用array ，没有用matrix，方便使用点乘和*乘
        cor_XY = np.array(mat_include_index_etc[:, 1:3])
        # 数据点个数
        num_data = len(cor_XY)
        cor_XY_2 = cor_XY * cor_XY
        XY_sqrtsum = [cor_XY_2[i, 0] + cor_XY_2[i, 1] for i in range(num_data)]
        XX = np.array([XY_sqrtsum for i in range(num_data)])
        YY = XX.T
        XY = np.dot(cor_XY, cor_XY.T)
        D_XY = (XX + YY - 2 * XY) ** 0.5
        return D_XY


if __name__ == '__main__':
    # 初始化
    number_of_orders = 10
    path_of_file = '..//benchmark//200//LC1_2_2'
    algorithm_input_data = Algorithm_inputdata(path_of_file, number_of_orders)
    parameters = {
        'capacity_max': 200,
        'time_latest': algorithm_input_data.Nodes.loc[0, 'b']
    }
    truck = Truck(1, parameters['capacity_max'], parameters['time_latest'])
