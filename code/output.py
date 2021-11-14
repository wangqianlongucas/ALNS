# -*- coding: utf-8 -*-
# @author: wangqianlong
# @email: 1763423314@qq.com
# @date: 2021/11/14

import matplotlib.pyplot as plt

def output_to_picture(output_picture_path, solution,algorithm_input_data):
    t_color = ['g--', 'r-', 'y--', 'g--', 'r-', 'y--', 'g--', 'r-', 'y--', 'g--', 'r-', 'y--', 'g--', 'r-', 'y--', 'g--', 'r-', 'y--']
    plt.figure()
    # 所有节点
    for node in range(1, len(algorithm_input_data.OAs) * 2 + 1):
        plt.scatter(algorithm_input_data.Nodes.loc[node].x, algorithm_input_data.Nodes.loc[node].y, s=5,
                    color='#35b779')
        plt.text(algorithm_input_data.Nodes.loc[node].x, algorithm_input_data.Nodes.loc[node].y, '%s' % node,
                 fontsize=5)
    # 卡车出发点
    plt.scatter(algorithm_input_data.Nodes.loc[0].x,
                algorithm_input_data.Nodes.loc[0].y, s=5, color='b')
    plt.text(algorithm_input_data.Nodes.loc[0].x,
             algorithm_input_data.Nodes.loc[0].y, 'Depot', fontsize=5)
    for truck_ID, truck in solution.items():
        node_1 = truck.route[-1]
        for node_2 in truck.route:
            x_plt = [algorithm_input_data.Nodes.loc[node_1].x, algorithm_input_data.Nodes.loc[node_2].x]
            y_plt = [algorithm_input_data.Nodes.loc[node_1].y, algorithm_input_data.Nodes.loc[node_2].y]
            plt.plot(x_plt, y_plt, t_color[truck_ID], linewidth=0.5)
            node_1 = node_2
    plt.savefig(output_picture_path + '\\trucks.png', dpi=600)
