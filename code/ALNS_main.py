# -*- coding: utf-8 -*-
# @author: wangqianlong
# @email: 1763423314@qq.com
# @date: 2021/11/2
# 算法主结构，包括算法框架和轮盘赌函数以及得分更新函数
# 轮盘赌函数：input: grade_of_removal_insert_pair = {('random', 'greedy'): value,...}; output: pair_select_sorted = [('random', 'greedy'),...]
# 算子集合 [('random', 'greedy'),('random', 'regret'),('shaw', 'greedy'),('shaw', 'regret'),('worst', 'greedy'),('worst', 'regret')]

import random
import numpy as np


# 区间定位函数：二分法，用于轮盘赌选择法
def dr_index(r,Q_list):
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
    index_dr = dr_index(r,Q_list)
    print(P_list)
    print(Q_list)
    print(r)
    print(index_dr)
    destroy_method = int(index_dr / 3) + 1  # 3为修复方法的个数
    repair_method = index_dr % 3 + 1  # 3为破坏方法的个数
    return destroy_method,repair_method,index_dr


# 更新得分,R_best函数
def update_gradesandR_best(R_re,R_best,index_dr,grades):
    print('update_gradesandR_best')
    # 设置接受准则、计算得分并更新等
    return R_best,grades


def ALNS(initial_solution):
    # 循环测试
    i = 1
    while i <= 100:
        # 轮盘赌选择法——pass
        destroy_method,repair_method,index_dr = rouletteselectionmethod(grades)
        # 破坏——pass
        R_de = destroy(destroy_method,R_best)
        # 修复——pass
        R_re = repair(repair_method,R_de)
        # 更新得分和R_best函数
        R_best,grades = update_gradesandR_best(R_re,R_best,index_dr,grades)
        i += 1