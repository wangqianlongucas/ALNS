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
    elif removal_method == 'worst':
        removal_solution = worst_removal(solution, number_of_removal_order, p, algorithm_input_data)
    return removal_solution


# 插入函数
def insert(insert_method, solution, request_blank, regret_level, algorithm_input_data):
    # 根据轮盘赌选择结果选择对应的方法
    if insert_method == 'greedy':
        insert_solution = greedy_insert(solution, request_blank, algorithm_input_data)
    elif insert_method == 'regret':
        insert_solution = regret_insert(solution, request_blank, regret_level, algorithm_input_data)
    return insert_solution


def ALNS(solution, pair_of_removal_and_insert, number_of_iter, number_of_segment_iter, number_of_removal_orders, algorithm_input_data):
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
            select_pair = roulette_selection_method(grades)
            print(select_pair)
            # print('输出grades：', grades)
            # select_pair = random.choice(pair_of_removal_and_insert)
            removal_method, insert_method = select_pair[0], select_pair[1]
            # removal
            # p 控制随机程度(shaw,worst)  todo here this parameter is not hyper-parameter now
            p = 100
            request_blank_removal, removal_solution = removal(removal_method, current_solution, number_of_removal_orders, p, algorithm_input_data)
            # insert
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
    number_of_orders = 15
    path_of_file = '..//data_output//data_15_new_2'
    algorithm_input_data = Algorithm_inputdata(path_of_file, number_of_orders)

    # 生成初始解
    first_stage_solution = first_stage(algorithm_input_data)
    first_stage_solution_output_path = path_of_file + '//output//first_stage'
    mkdir(first_stage_solution_output_path)
    output_to_picture(first_stage_solution_output_path, first_stage_solution, algorithm_input_data)
    output_to_log(first_stage_solution_output_path, first_stage_solution)
    first_stage_solution_objective = sum(truck.travel_distance_line_of_route[-1] for truck in
                                         list(first_stage_solution.values())) + algorithm_input_data.M * len([])
    print('first_stage_solution:',first_stage_solution_objective)

    # 初始解提升（使用LNS算法减少最小使用车辆和第二目标）
    number_of_removal_orders = int(0.3 * len(algorithm_input_data.orders))
    number_of_iter_LNS = 10
    second_stage_solution = second_stage(algorithm_input_data, first_stage_solution, number_of_removal_orders, number_of_iter_LNS)
    second_stage_solution_output_path = path_of_file + '//output//second_stage'
    mkdir(second_stage_solution_output_path)
    output_to_picture(second_stage_solution_output_path, second_stage_solution, algorithm_input_data)
    output_to_log(second_stage_solution_output_path, second_stage_solution)
    second_stage_solution_objective = sum(truck.travel_distance_line_of_route[-1] for truck in
                                          list(second_stage_solution.values())) + algorithm_input_data.M * len([])
    print('second_stage_solution:', second_stage_solution_objective)

    # 使用ALNS算法求解
    # pair_of_removal_and_insert = [('random', 'greedy'), ('random', 'regret'), ('shaw', 'greedy'), ('shaw', 'regret'),
    #                               ('worst', 'greedy'), ('worst', 'regret')]
    # todo regret_insert has problem
    pair_of_removal_and_insert = [('random', 'greedy'), ('shaw', 'greedy'), ('worst', 'greedy')]
    # todo notation: here second_stage_solution should be complete
    number_of_iter_ALNS = 15
    number_of_segment_iter = 5
    ALNS_solution, grades = ALNS(second_stage_solution, pair_of_removal_and_insert, number_of_iter_ALNS, number_of_segment_iter, number_of_removal_orders, algorithm_input_data)
    ALNS_best_sulution = ALNS_solution['best']['solution']
    ALNS_solution_objective = ALNS_solution['best']['objective']
    ALNS_stage_solution_output_path = path_of_file + '//output//ALNS'
    mkdir(ALNS_stage_solution_output_path)
    output_to_picture(ALNS_stage_solution_output_path, ALNS_best_sulution, algorithm_input_data)
    output_to_log(ALNS_stage_solution_output_path, ALNS_best_sulution)

    print('first_stage_solution:', first_stage_solution_objective)
    print('second_stage_solution:', second_stage_solution_objective)
    print('ALNS_solution:', ALNS_solution_objective)
