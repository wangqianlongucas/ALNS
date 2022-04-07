# -*- coding: utf-8 -*-
# @author: wangqianlong
# @email: 1763423314@qq.com
# @date: 2021/11/2
# 算法主结构，包括算法框架和轮盘赌函数以及得分更新函数
# 轮盘赌函数：input: grade_of_removal_insert_pair = {('random', 'greedy'): value,...}; output: pair_select_sorted = [('random', 'greedy'),...]
# 算子集合 [('random', 'greedy'),('random', 'regret'),('shaw', 'greedy'),('shaw', 'regret'),('worst', 'greedy'),('worst', 'regret')]
import copy
import random
import time

import numpy as np
from collections import Counter

from initial_solution import *
from removal_requests import *
from insert_requests import *
from file_create import *
from output import *


# 轮盘赌选择移除-插入方法  by YJY 2021/11/30
def roulette_selection_method(grades):
    grades_by_using_rsm = []
    grades_pair_by_using_rsm = []
    for pair, grade in grades.items():
        grades_by_using_rsm.append(grade['grade'][-1])
        grades_pair_by_using_rsm.append(pair)
    grade_sum = sum(grades_by_using_rsm)
    P_list = list(np.array(grades_by_using_rsm) / grade_sum)
    Q_list = []
    i = 0
    while i < len(P_list):
        # 累积概率
        sum_prob = 0
        select_prob = np.random.rand()
        # print('随机生成的选择概率为select_prob', select_prob)
        for j in range(0, len(P_list)):
            sum_prob = P_list[j] + sum_prob
            # sum_prob = (fitness[j] - fitness.min()) / (fitness.sum() - POP_size * fitness.min()) + sum_prob
            if sum_prob > select_prob:
                # print("当前适应度的值的和", sum_prob)
                # print(j)
                # 存放的是索引号
                Q_list.append(j)
                i = i + 1
                break
            else:
                continue

    # 想找到出现次数最多的索引，使用字典去计数
    i = 0
    Q_list.sort()
    index_dic = []
    while i < len(Q_list):
        num_ii = Q_list.count(Q_list[i])
        num_dic = [Q_list[i], num_ii]
        index_dic.append(num_dic)
        i += num_ii
    # print(index_dic)

    i_index = 0
    value_upper = 0
    for item in index_dic:
        # print(item)
        if item[1] > value_upper:
            i_index = item[0]
            value_upper = item[1]
    # print(i_index)
    # 返回的是轮盘赌选择的插入移除算子对应的索引
    select_pair = grades_pair_by_using_rsm[i_index]
    return select_pair


# 更新得分,others函数
def update_grades_and_others(ALNS_solution, select_pair, grades, segment, algorithm_input_data, T_max):
    # 更新全局最优
    if ALNS_solution['insert']['objective'] <= ALNS_solution['best']['objective']:
        # 更新解
        ALNS_solution['best']['solution'] = ALNS_solution['insert']['solution']
        ALNS_solution['best']['objective'] = ALNS_solution['insert']['objective']
        ALNS_solution['best']['request_blank'] = ALNS_solution['insert']['request_blank']
        # 更新得分
        grades[select_pair]['grade'][segment] += algorithm_input_data.sita['sita_1']
    # 更新当前解
    if ALNS_solution['insert']['objective'] <= ALNS_solution['current']['objective']:
        ALNS_solution['current']['solution'] = ALNS_solution['insert']['solution']
        ALNS_solution['current']['objective'] = ALNS_solution['insert']['objective']
        ALNS_solution['current']['request_blank'] = ALNS_solution['insert']['request_blank']
        grades[select_pair]['grade'][segment] += algorithm_input_data.sita['sita_2']
    else:
        insert_accept_sa = random.random()
        if insert_accept_sa <= math.exp(
                -(ALNS_solution['insert']['objective'] - ALNS_solution['current']['objective']) / T_max):
            ALNS_solution['current']['solution'] = ALNS_solution['insert']['solution']
            ALNS_solution['current']['objective'] = ALNS_solution['insert']['objective']
            ALNS_solution['current']['request_blank'] = ALNS_solution['insert']['request_blank']
            grades[select_pair]['grade'][segment] += algorithm_input_data.sita['sita_3']
    return ALNS_solution, grades


# 移除函数
def removal(removal_method, solution, number_of_removal_order, p, algorithm_input_data):
    # 根据轮盘赌选择结果选择对应的方法
    if removal_method == 'random':
        removal_solution = random_removal(solution, number_of_removal_order, algorithm_input_data)
    elif removal_method == 'shaw':
        removal_solution = shaw_removal(solution, number_of_removal_order, p, algorithm_input_data)
    elif removal_method == 'worst':
        removal_solution = worst_removal(solution, number_of_removal_order, p, algorithm_input_data)
    elif removal_method == 'string':
        removal_solution = string_removal(solution, number_of_removal_order, algorithm_input_data)
        # removal_solution = string_removal(solution, 4, algorithm_input_data)
    return removal_solution


# 插入函数
def insert(insert_method, solution, request_blank, regret_level, algorithm_input_data):
    # 根据轮盘赌选择结果选择对应的方法
    if insert_method == 'greedy':
        insert_solution = greedy_insert(solution, request_blank, algorithm_input_data)
    elif insert_method == 'regret':
        insert_solution = regret_insert(solution, request_blank, regret_level, algorithm_input_data)
    return insert_solution

def checking_solution_whether_has_empty_route(solution):
    for truck_ID in list(solution.keys()):
        if not solution[truck_ID].order:
            del solution[truck_ID]
    return solution

def ALNS(solution, pair_of_removal_and_insert, number_of_iter, number_of_segment_iter, number_of_removal_orders,
         algorithm_input_data):
    # 初始化
    number_of_segment = int(number_of_iter / number_of_segment_iter)
    grades = {pair: {'segment': [0], 'grade': [1], 'times': [1]} for pair in pair_of_removal_and_insert}
    solution_fomat = {'solution': None, 'request_blank': [], 'objective': np.inf}
    ALNS_solution = {'current': copy.deepcopy(solution_fomat), 'insert': copy.deepcopy(solution_fomat),
                     'best': copy.deepcopy(solution_fomat)}
    ALNS_solution['current']['solution'] = {id: solution[id].truck_copy() for id in solution.keys()}
    # 计算当前解目标
    ALNS_solution['current']['objective'] = sum(truck.travel_distance_line_of_route[-1] for truck in
                                                list(solution.values())) + algorithm_input_data.M * len([])
    ALNS_solution['best']['solution'] = ALNS_solution['current']['solution']
    ALNS_solution['best']['objective'] = ALNS_solution['current']['objective']
    ALNS_best_objectives = []
    pi_start = {pair: 0 for pair in pair_of_removal_and_insert}
    for segment in range(1, number_of_segment + 1):
        print('segment', segment)
        # 得分初始化
        for pair, value in grades.items():
            grades[pair]['segment'].append(segment)
            r = 0.5
            # grades[pair]['grade'] += [grades[pair]['grade'][-1] * (1 - r) + r * (grades[pair]['grade'][-1] - pi_start[pair]) / grades[pair]['times'][-1]]
            # todo 避免 某一算子的分数太低
            grades[pair]['grade'] += [
                max(grades[pair]['grade'][-1] * (1 - r) + r * (grades[pair]['grade'][-1] - pi_start[pair]) /
                    grades[pair]['times'][-1], 0.1)]

            grades[pair]['times'].append(1)  # 初始化为 1，这两行代码顺序不可交换！！！
        # segment 开始时的得分
        pi_start = {pair: grades[pair]['grade'][-1] for pair in pair_of_removal_and_insert}
        # 循环测试
        # 初最高温
        T_MAX = 100
        T_MIN = 1
        for iter in range(number_of_segment_iter):
            print('iter', iter)
            # 初始化
            current_solution = ALNS_solution['current']['solution']
            current_solution = checking_solution_whether_has_empty_route(current_solution)
            request_blank = [order_i for order_i in ALNS_solution['current']['request_blank']]

            # # 轮盘赌选择法 选择
            select_pair = roulette_selection_method(grades)
            # 更新算子使用次数
            grades[select_pair]['times'][-1] += 1
            print(select_pair)
            # print('输出grades：', grades)
            # select_pair = random.choice(pair_of_removal_and_insert)
            removal_method, insert_method = select_pair[0], select_pair[1]
            # removal
            # p 控制随机程度(shaw,worst)  todo here this parameter is not hyper-parameter now
            p = 3
            print('ALNS,removal')
            number_of_removal_orders_else = max(number_of_removal_orders - len(request_blank),
                                                int(0.5 * number_of_removal_orders))
            request_blank_removal, removal_solution = removal(removal_method, current_solution,
                                                              number_of_removal_orders_else, p, algorithm_input_data)
            # insert
            request_blank += request_blank_removal
            # todo debug-->pass
            request_blank_counter = dict(Counter(request_blank))
            if list(request_blank_counter.values()):
                if max(list(request_blank_counter.values())) > 1:  # 同一订单移除超过一次
                    print('warning!--------------------------------------1')
            regret_level = 2
            print('ALNS,insert')
            ALNS_solution['insert']['request_blank'], ALNS_solution['insert']['solution'] = insert(insert_method,
                                                                                                   removal_solution,
                                                                                                   request_blank,
                                                                                                   regret_level,
                                                                                                   algorithm_input_data)
            print('ALNS,update_grades_and_others')
            # 更新得分和others
            ALNS_solution['insert']['objective'] = sum(truck.travel_distance_line_of_route[-1] for truck in
                                                       list(ALNS_solution['insert'][
                                                                'solution'].values())) + algorithm_input_data.M * len(
                ALNS_solution['insert']['request_blank'])
            ALNS_solution, grades = update_grades_and_others(ALNS_solution, select_pair, grades, segment,
                                                             algorithm_input_data, T_MAX)
            ALNS_best_objectives.append(ALNS_solution['best']['objective'])
            T_MAX = 0.9999 * T_MAX
            if T_MAX < T_MIN:
                print('segment_%s:T_MAX < T_MIN' % segment)
                break
    return ALNS_solution, grades, ALNS_best_objectives


if __name__ == '__main__':
    random.seed(100)
    # 初始化
    number_of_orders = 10
    path_of_file = '..//benchmark//200//LC1_2_2'
    algorithm_input_data = Algorithm_inputdata(path_of_file, number_of_orders)
    parameters = {
        'capacity_max': 200,
        'time_latest': algorithm_input_data.Nodes.loc[0, 'b']
    }
    # 生成初始解
    first_stage_solution = first_stage(algorithm_input_data, parameters)
    first_stage_solution_trucks = len(first_stage_solution)
    first_stage_solution_output_path = path_of_file + '//output//first_stage'
    mkdir(first_stage_solution_output_path)
    output_to_picture(first_stage_solution_output_path, first_stage_solution, algorithm_input_data)
    first_stage_solution_objective = sum(truck.travel_distance_line_of_route[-1] for truck in
                                         list(first_stage_solution.values())) + algorithm_input_data.M * len([])
    output_to_log(first_stage_solution_output_path, first_stage_solution, first_stage_solution_objective,
                  first_stage_solution_trucks)
    print('first_stage_solution:', first_stage_solution_objective)

    # 初始解提升（使用LNS算法减少最小使用车辆和第二目标）
    number_of_removal_orders = int(0.2 * len(algorithm_input_data.orders))
    number_of_iter_LNS = int(first_stage_solution_trucks/3)
    t_3 = time.time()
    second_stage_solution = second_stage(algorithm_input_data, first_stage_solution, number_of_removal_orders,
                                         number_of_iter_LNS)
    t_4 = time.time()
    print('----------------------', t_4 - t_3)
    second_stage_solution_trucks = len(second_stage_solution)
    second_stage_solution_output_path = path_of_file + '//output//second_stage'
    mkdir(second_stage_solution_output_path)
    output_to_picture(second_stage_solution_output_path, second_stage_solution, algorithm_input_data)
    second_stage_solution_objective = sum(truck.travel_distance_line_of_route[-1] for truck in
                                          list(second_stage_solution.values())) + algorithm_input_data.M * len([])
    output_to_log(second_stage_solution_output_path, second_stage_solution, second_stage_solution_objective,
                  second_stage_solution_trucks)
    print('second_stage_solution:', second_stage_solution_objective)

    # 使用ALNS算法求解
    # pair_of_removal_and_insert = [('random', 'greedy'), ('random', 'regret'), ('shaw', 'greedy'), ('shaw', 'regret'),
    #                               ('worst', 'greedy'), ('worst', 'regret')]
    # todo regret_insert has problem
    pair_of_removal_and_insert = [('random', 'greedy'), ('shaw', 'greedy'), ('worst', 'greedy')]
    # pair_of_removal_and_insert = [('shaw', 'greedy'), ('worst', 'greedy'), ('string', 'greedy')]
    # todo notation: here second_stage_solution should be complete
    number_of_iter_ALNS = 100
    number_of_segment_iter = 2
    ALNS_solution, grades, ALNS_best_objectives = ALNS(second_stage_solution, pair_of_removal_and_insert,
                                                       number_of_iter_ALNS, number_of_segment_iter,
                                                       number_of_removal_orders, algorithm_input_data)
    ALNS_best_solution = ALNS_solution['best']['solution']
    ALNS_best_solution_trucks = len(ALNS_best_solution)
    ALNS_solution_objective = ALNS_solution['best']['objective']
    ALNS_stage_solution_output_path = path_of_file + '//output//ALNS'
    mkdir(ALNS_stage_solution_output_path)
    output_to_picture(ALNS_stage_solution_output_path, ALNS_best_solution, algorithm_input_data)
    output_to_log(ALNS_stage_solution_output_path, ALNS_best_solution, ALNS_solution_objective,
                  ALNS_best_solution_trucks)
    ALNS_output(grades, ALNS_best_objectives, ALNS_stage_solution_output_path)

    print('first_stage_solution:', first_stage_solution_objective)
    print('second_stage_solution:', second_stage_solution_objective)
    print('ALNS_solution:', ALNS_solution_objective)
