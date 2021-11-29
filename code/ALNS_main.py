# -*- coding: utf-8 -*-
# @author: wangqianlong
# @email: 1763423314@qq.com
# @date: 2021/11/2
# 算法主结构，包括算法框架和轮盘赌函数以及得分更新函数
# 轮盘赌函数：input: grade_of_removal_insert_pair = {('random', 'greedy'): value,...}; output: pair_select_sorted = [('random', 'greedy'),...]
# 算子集合 [('random', 'greedy'),('random', 'regret'),('shaw', 'greedy'),('shaw', 'regret'),('worst', 'greedy'),('worst', 'regret')]
import copy
import random
import numpy as np

from initial_solution import *
from removal_requests import *
from insert_requests import *


# 区间定位函数：二分法，用于轮盘赌选择法
def dr_index(r, Q_list):
    up_index = len(Q_list) - 1  # 指数减一
    low_index = 0
    Q_list_half_index = up_index
    while up_index - low_index > 1:
        Q_list_half_index = int((up_index + low_index) / 2)
        if r <= Q_list[Q_list_half_index]:
            up_index = Q_list_half_index
        else:
            low_index = Q_list_half_index
    return low_index


# 轮盘赌选择破坏-修复方法
def rouletteselectionmethod(grades):
    grade_sum = sum(grades)
    P_list = list(np.array(grades) / grade_sum)
    Q_list = [0]
    for q in range(len(P_list)):
        Q_list.append(sum(P_list[0:q + 1]))
    r = random.random()
    index_dr = dr_index(r, Q_list)
    print(P_list)
    print(Q_list)
    print(r)
    print(index_dr)
    destroy_method = int(index_dr / 3) + 1  # 3为修复方法的个数
    repair_method = index_dr % 3 + 1  # 3为破坏方法的个数
    return destroy_method, repair_method, index_dr


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
        if insert_accept_sa <= math.exp(-(ALNS_solution['insert']['objective'] - ALNS_solution['current']['objective']) / T_max):
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
    # elif removal_method == 'worst':
    #     removal_solution = worst_removal(solution)
    return removal_solution


# 插入函数
def insert(insert_method, solution, request_blank, regret_level, algorithm_input_data):
    # 根据轮盘赌选择结果选择对应的方法
    if insert_method == 'greedy':
        insert_solution = greedy_insert(solution, request_blank, algorithm_input_data)
    elif insert_method == 'regret':
        insert_solution = regret_insert(solution, request_blank, regret_level, algorithm_input_data)
    return insert_solution


def ALNS(solution, pair_of_removal_and_insert, number_of_iter, number_of_segment_iter,algorithm_input_data):
    # 初始化
    number_of_segment = int(number_of_iter / number_of_segment_iter)
    grades = {pair: {'segment': [0], 'grade': [1]} for pair in pair_of_removal_and_insert}
    solution_fomat = {'solution': None, 'request_blank': [], 'objective': np.inf}
    ALNS_solution = {'current': copy.deepcopy(solution_fomat), 'insert': copy.deepcopy(solution_fomat), 'best': copy.deepcopy(solution_fomat)}
    ALNS_solution['current']['solution'] = copy.deepcopy(solution)
    # 计算当前解目标
    ALNS_solution['current']['objective'] = sum(truck.travel_distance_line_of_route[-1] for truck in
                                                list(solution.values())) + algorithm_input_data.M * len([])
    ALNS_solution['best']['solution'] = ALNS_solution['current']['solution']
    ALNS_solution['best']['objective'] = ALNS_solution['current']['objective']
    for segment in range(1, number_of_segment + 1):
        print('segment', segment)
        # 得分初始化
        for pair, value in grades.items():
            grades[pair]['segment'].append(segment)
            r = 0.5
            grades[pair]['grade'] += [grades[pair]['grade'][-1] * (1 - r) + r * grades[pair]['grade'][-1] / segment]
        # 循环测试
        # 初最高温
        T_MAX = 100
        T_MIN = 1
        for iter in range(number_of_segment_iter):
            print('iter', iter)
            # 初始化
            current_solution = ALNS_solution['current']['solution']
            request_blank = ALNS_solution['current']['request_blank']

            # # 轮盘赌选择法 选择
            # select_pair = rouletteselectionmethod(grades)
            select_pair = random.choice(pair_of_removal_and_insert)
            removal_method, insert_method = select_pair[0], select_pair[1]
            # 破坏
            number_of_removal_order = 3
            # p 控制随机程度(shaw,worst)
            p = 100
            request_blank_removal, removal_solution = removal(removal_method, current_solution, number_of_removal_order, p, algorithm_input_data)
            # 修复
            request_blank += request_blank_removal
            regret_level = 2
            ALNS_solution['insert']['request_blank'], ALNS_solution['insert']['solution'] = insert(insert_method, removal_solution, request_blank, regret_level, algorithm_input_data)
            # 更新得分和others
            ALNS_solution['insert']['objective'] = sum(truck.travel_distance_line_of_route[-1] for truck in
                                                       list(ALNS_solution['insert']['solution'].values())) + algorithm_input_data.M * len(ALNS_solution['insert']['request_blank'])
            ALNS_solution, grades = update_grades_and_others(ALNS_solution, select_pair, grades, segment, algorithm_input_data, T_MAX)
            T_MAX = 0.95 * T_MAX
            if T_MAX < T_MIN:
                print('segment_%s:T_MAX < T_MIN' % segment)
                break
    return ALNS_solution, grades


if __name__ == '__main__':
    # 初始化
    number_of_orders = 50
    path_of_file = '..//data_50'
    algorithm_input_data = Algorithm_inputdata(path_of_file,number_of_orders)
    # 生成初始解
    first_stage_solution = first_stage(algorithm_input_data)
    output_to_picture('..//output//first_stage', first_stage_solution, algorithm_input_data)
    output_to_log('..//output//first_stage', first_stage_solution)
    first_stage_solution_objective = sum(truck.travel_distance_line_of_route[-1] for truck in
                                         list(first_stage_solution.values())) + algorithm_input_data.M * len([])
    print('first_stage_solution:',first_stage_solution_objective)
    # 初始解提升（使用LNS算法减少最小使用车辆和第二目标）
    second_stage_solution = second_stage(algorithm_input_data, first_stage_solution)
    output_to_picture('..//output//second_stage', second_stage_solution, algorithm_input_data)
    output_to_log('..//output//second_stage', second_stage_solution)
    second_stage_solution_objective = sum(truck.travel_distance_line_of_route[-1] for truck in
                                          list(second_stage_solution.values())) + algorithm_input_data.M * len([])
    print('second_stage_solution:', second_stage_solution_objective)
    # 使用ALNS算法求解
    # pair_of_removal_and_insert = [('random', 'greedy'), ('random', 'regret'), ('shaw', 'greedy'), ('shaw', 'regret'),
    #                               ('worst', 'greedy'), ('worst', 'regret')]
    # todo regret_insert has problem
    pair_of_removal_and_insert = [('random', 'greedy'), ('shaw', 'greedy')]
    # todo notation: here second_stage_solution should be complete
    number_of_iter = 30
    number_of_segment_iter = 10
    ALNS_solution, grades = ALNS(second_stage_solution, pair_of_removal_and_insert, number_of_iter, number_of_segment_iter,algorithm_input_data)
    ALNS_best_sulution = ALNS_solution['best']['solution']
    output_to_picture('..//output//ALNS', ALNS_best_sulution, algorithm_input_data)
    output_to_log('..//output//ALNS', ALNS_best_sulution)
