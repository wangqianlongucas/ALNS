# -*- coding: utf-8 -*-
# @author: wangqianlong
# @email: 1763423314@qq.com
# @date: 2021/12/1

import pandas as pd
import random
import math

class Data_parameter():
    def __init__(self,path_of_file):
        # 订单数量
        self.no = 15  # 个
        # 配送员中心数量
        self.np = 1  # 配送中心个数
        # 订单分布半径，直径为2*R
        self.R = 5  # 千米
        self.distance_P_and_D_max = 3
        # 订单时间窗长度
        self.TWL = 1  # 小时
        self.TWL_wave = 0.1  # 小时
        # 规划时间窗最大值，最小值为0
        self.Tmax = 4  # 小时
        # 订单需求下界
        self.dmmin = 0.5  # 千克
        # 订单需求上界
        self.dmmax = 0.75  # 千克
        # 更换电池的时间之一半
        self.s_d = 0 / 2 / 60  # 小时
        # 提取商品或者交付商品的时间
        self.s_o = 2 / 60  # 小时
        self.outpath = path_of_file

# 订单生成
def OAs_generate(data_parameter):
    OAs_title = ['OID', 'Pickup', 'Deliver', 'Fi']
    OAs_data = [[o, o, o + data_parameter.no, 5] for o in range(1, (data_parameter.no + 1))]
    OAs = pd.DataFrame(OAs_data, columns=OAs_title)
    OAs_to_path = data_parameter.outpath + '\\OAs%s.csv' % data_parameter.no
    OAs.to_csv(OAs_to_path, index=False)

#o_Pickup_deliver生成函数
def o_Pickup_Deliver(o,data_parameter):
    o_Pickup_r = random.uniform(0,data_parameter.R)
    o_Pickup_sita = random.uniform(0,2 * math.pi)
    a = random.uniform(0,data_parameter.Tmax - data_parameter.TWL)
    o_TWL = data_parameter.TWL + random.uniform(-data_parameter.TWL_wave, data_parameter.TWL_wave)
    b = min(a + o_TWL,data_parameter.Tmax)
    dm = random.uniform(data_parameter.dmmin,data_parameter.dmmax)
    o_Pickup_r_x = o_Pickup_r * math.cos(o_Pickup_sita)
    o_Pickup_r_y = o_Pickup_r * math.sin(o_Pickup_sita)
    o_Pickup = ['pickup%s'%o,o_Pickup_r_x,o_Pickup_r_y,a,b,dm,data_parameter.s_o]
    o_Deliver_r = random.uniform(0,data_parameter.R)
    o_Deliver_sita = random.uniform(0,2 * math.pi)
    o_Deliver_r_x = o_Pickup_r_x + o_Deliver_r * math.cos(o_Deliver_sita)
    o_Deliver_r_y = o_Pickup_r_y + o_Deliver_r * math.sin(o_Deliver_sita)
    o_Deliver = ['deliver%s'%o,o_Deliver_r_x,o_Deliver_r_y,a,b,-dm,data_parameter.s_o]
    return o_Pickup,o_Deliver

# Nodes函数 生成Nodes：无人机服务站：index = 0，Pickup节点（index）1···no和Deliver节点（index）：no+1···2*no
def Nodes_generate(data_parameter):
    N_sevice = [['sevice_D', 0, 0, 0, data_parameter.Tmax, 0, data_parameter.s_d]]
    P = []
    D = []
    for o in range(1, (data_parameter.no + 1)):
        o_Pickup, o_Deliver = o_Pickup_Deliver(o,data_parameter)
        P.append(o_Pickup)
        D.append(o_Deliver)

    Nodes_title = ['NID', 'x', 'y', 'a', 'b', 'dm', 'st']
    Nodes_data = N_sevice + P + D
    Nodes = pd.DataFrame(Nodes_data, columns=Nodes_title)
    Nodes_to_path = data_parameter.outpath + '\\Nodes%s.csv' % data_parameter.no
    Nodes.to_csv(Nodes_to_path, index=False)

def log_generate(data_parameter):
    txt_path = data_parameter.outpath + '\\日志%s-%s-%s.txt' % (data_parameter.no, data_parameter.np, data_parameter.R)
    with open(txt_path, 'w') as f:
        text = ['订单个数\t', '配送员个数\t', '节点半径\t', '订单时间窗长度\t', '总时间长度\t', '载重下限\t', '载重上限\t', '节点服务时间\t', '无人机服务站服务时间\t']
        text_value = [data_parameter.no, data_parameter.np, data_parameter.R, data_parameter.TWL, data_parameter.Tmax, data_parameter.dmmin, data_parameter.dmmax, data_parameter.s_d, data_parameter.s_o]
        for text_index in range(len(text)):
            f.write(text[text_index] + str(text_value[text_index]) + '\n')
# 算例生成
def data_generate(data_parameter):
    OAs_generate(data_parameter)
    Nodes_generate(data_parameter)
    log_generate(data_parameter)

if __name__ == '__main__' :
    path_of_file = '..//data_15_new_2'
    data_parameter = Data_parameter(path_of_file)
    data_generate(data_parameter)