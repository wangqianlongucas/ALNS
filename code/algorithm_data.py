# -*- coding: utf-8 -*-
# @author: wangqianlong
# @email: 1763423314@qq.com
# @date: 2021/11/07

# 本代码文件包括数据结构定义、数据读取和处理
import pandas as pd
import numpy as np


class Truck():
    def __init__(self, ID):
        self.id = ID
        self.capacity = 1 # todo 最大载重，检查是否需要调参
        self.origin = [0]
        self.end = [0]
        self.order = []
        self.route = self.origin + self.end
        self.time_line = [0,0]
        self.capacity_line = [0,0]
        self.travel_distance_line_of_route = [0,0]
        self.v = 35  # km/h

    def time_line_update(self, insert_position, algorithm_input_data):
        # 只需要更新插入位置及其后续位置的时间
        self.time_line = self.time_line[:insert_position]
        node_last = self.route[insert_position - 1]
        is_insert_pass = 1
        for node in self.route[insert_position:]:
            # # 未计算服务时间 # node_time 开始服务时间（离开时间）
            # node_time = max(self.time_line[-1] + (algorithm_input_data.Distance_Mat[node_last,node])/self.v, algorithm_input_data.Nodes.loc[node, 'a'])
            # if node_time <= algorithm_input_data.Nodes.loc[node, 'b']:
            #     self.time_line.append(node_time)
            #     node_last = node
            # else:
            #     is_insert_pass = 0
            #     break
            # 计算服务时间
            start_time = max(self.time_line[-1] + (algorithm_input_data.Distance_Mat[node_last, node]) / self.v,
                             algorithm_input_data.Nodes.loc[node, 'a'])
            leave_time = start_time + algorithm_input_data.Nodes.loc[node, 'st']
            if start_time <= algorithm_input_data.Nodes.loc[node, 'b']:
                self.time_line.append(leave_time)
                node_last = node
            else:
                is_insert_pass = 0
                break
        return is_insert_pass

    def capacity_line_update(self, insert_position, algorithm_input_data):
        is_insert_pass = 1
        self.capacity_line = self.capacity_line[:insert_position]
        for node in self.route[insert_position:]:
            node_capacity = self.capacity_line[-1] + algorithm_input_data.Nodes.loc[node, 'dm']
            if node_capacity <= self.capacity:
                self.capacity_line.append(node_capacity)
            else:
                is_insert_pass = 0
                break
        return is_insert_pass

    def check_and_update(self, insert_position, algorithm_input_data):
        is_insert_pass_time = self.time_line_update(insert_position, algorithm_input_data)
        if is_insert_pass_time:
            is_insert_pass_capacity = self.capacity_line_update(insert_position, algorithm_input_data)
            return is_insert_pass_capacity
        return is_insert_pass_time

    def travel_distance_line_of_route_update_insert(self, insert_position, algorithm_input_data):
        node_before, node, node_after = self.route[insert_position - 1], self.route[insert_position], self.route[insert_position + 1]
        # 插入新增点的行驶距离
        travel_node = self.travel_distance_line_of_route[insert_position - 1] + algorithm_input_data.Distance_Mat[node_before,node]
        self.travel_distance_line_of_route.insert(insert_position,travel_node)
        # 更新插入点后的行驶距离
        travel_change = algorithm_input_data.Distance_Mat[node, node_after] + algorithm_input_data.Distance_Mat[
            node_before, node] - algorithm_input_data.Distance_Mat[node_before, node_after]
        self.travel_distance_line_of_route[insert_position + 1:] = [travel + travel_change for travel in self.travel_distance_line_of_route[insert_position + 1:]]

    def travel_distance_line_of_route_update_remove(self, remove_position, algorithm_input_data):
        del self.travel_distance_line_of_route[remove_position]
        node_before, node = self.route[remove_position - 1], self.route[remove_position]
        travel_node = self.travel_distance_line_of_route[remove_position - 1] + algorithm_input_data.Distance_Mat[node_before,node]
        travel_change = self.travel_distance_line_of_route[remove_position] - travel_node
        # 更新移除点后的行驶距离
        self.travel_distance_line_of_route[remove_position:] = [travel - travel_change for travel in self.travel_distance_line_of_route[remove_position:]]

class Algorithm_inputdata():
    # 初始化：读取数据和生成参数
    def __init__(self, path_of_file, number_of_orders):
        # 读取订单数据和节点数据
        self.OAs = pd.read_csv(path_of_file + '\\OAs%s.csv'%number_of_orders, index_col=0)
        self.orders = list(self.OAs.loc[:, 'Pickup'])
        # Nodes[0]表示卡车出发点
        self.Nodes = pd.read_csv(path_of_file + '\\Nodes%s.csv'%number_of_orders)
        # 计算距离矩阵
        self.Distance_Mat = self.distance_matrix(self.Nodes)
        # 惩罚
        self.M = 800
        # 相似度系数
        self.weight = {'d': 9, 'T': 3, 'l': 2, 'K': 5}
        # self.sita = {'sita_1': 33, 'sita_2': 9, 'sita_3': 13}
        self.sita = {'sita_1': 0.4, 'sita_2': 0.3, 'sita_3': 0.2}

    def distance_matrix(self,pd_data):
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
        D_XY = (XX + YY - 2 * XY)**0.5
        return D_XY


if __name__ == '__main__':
    # 初始化
    number_of_orders = 10
    path_of_file = '..//data_output//data_10_model'
    algorithm_input_data = Algorithm_inputdata(path_of_file, number_of_orders)
    truck = Truck(1)
