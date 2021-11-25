# -*- coding: utf-8 -*-
"""
Created on Wed Apr  7 13:34:24 2021

@author: Administrator
"""

import random
import numpy as np

##算法框架
#破坏方法：传入一套完整的路线
def destroy_method1(R):
    R_de = R
    print('选择的破坏方法为1')
    return R_de
def destroy_method2(R):
    R_de = R
    print('选择的破坏方法为2')
    return R_de
def destroy_method3(R):
    R_de = R
    print('选择的破坏方法为3')
    return R_de
#修复方法：传入破坏后的路线
def repair_method1(R):
    R_re = R
    print('选择的修复方法为1')
    return R_re
def repair_method2(R):
    R_re = R
    print('选择的修复方法为2')
    return R_re
def repair_method3(R):
    R_re = R
    print('选择的修复方法为1')
    return R_re
#轮盘赌选择法:传入破坏-修复方法的得分列表：grades = [1,1,1,1,1,1,1,1,1](3*3)
#区间定位函数：二分法，用于轮盘赌选择法
def dr_index(r,Q_list):
    up_index = len(Q_list) - 1 #指数减一
    low_index = 0
    Q_list_half_index = up_index
    while up_index - low_index > 1:
        Q_list_half_index = int((up_index + low_index) / 2)
        if r <= Q_list[Q_list_half_index]:
            up_index = Q_list_half_index
        else:
            low_index = Q_list_half_index
    return low_index
#轮盘赌选择破坏-修复方法
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
    destroy_method = int(index_dr / 3) + 1 #3为修复方法的个数
    repair_method =  index_dr % 3 + 1 #3为破坏方法的个数
    return destroy_method,repair_method,index_dr
#破坏函数
def destroy(destroy_method,R):
    #根据轮盘赌选择结果选择对应的方法
    if destroy_method == 1:
        R_de = destroy_method1(R)
    elif destroy_method == 2:
        R_de = destroy_method2(R)
    elif destroy_method == 3:
        R_de = destroy_method3(R) 
    return R_de
#修复函数
def repair(repair_method,R_de):
    #根据轮盘赌选择结果选择对应的方法
    if repair_method == 1:
        R_re = repair_method1(R_de)
    elif repair_method == 2:
        R_re = repair_method2(R_de)
    elif repair_method == 3:
        R_re = repair_method3(R_de) 
    return R_re
#更新得分,R_best函数
def update_gradesandR_best(R_re,R_best,index_dr,grades):
    print('update_gradesandR_best')
    #设置接受准则、计算得分并更新等
    return R_best,grades
    
#测试
R_best = [[0,1,2,3,4,5],[0,1,2,3,4,5]]
grades = [1,1,1,1,1,1,1,1,1]
#轮盘赌选择法——pass
destroy_method,repair_method,index_dr = rouletteselectionmethod(grades)
#破坏——pass
R_de = destroy(destroy_method,R_best)
#修复——pass
R_re = repair(repair_method,R_de)
#更新得分和R_best函数
R_best,grades = update_gradesandR_best(R_re,R_best,index_dr,grades)
#循环测试
i = 1
while i <= 100:
    #轮盘赌选择法——pass
    destroy_method,repair_method,index_dr = rouletteselectionmethod(grades)
    #破坏——pass
    R_de = destroy(destroy_method,R_best)
    #修复——pass
    R_re = repair(repair_method,R_de)
    #更新得分和R_best函数
    R_best,grades = update_gradesandR_best(R_re,R_best,index_dr,grades)
    i += 1


