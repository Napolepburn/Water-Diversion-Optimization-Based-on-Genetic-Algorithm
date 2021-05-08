# -*- coding: utf-8 -*

import numpy as np
from numba import jit
#import global_var

#engineering_param = global_var.get_value('engineering_param')

@jit
def initial_water_balance(input, node, total_inflow, engineering_param, lim_irr_storage_disc_rate=1.0, lim_ind_lif_storage_disc_rate=1.0, irr_rate = 0.6, 
                              ind_lif_rate = 0.7, diversion_storage=3370, storage=0):   

    flood_start = engineering_param[node,6];
    flood_end = engineering_param[node,7];
    eco_start = engineering_param[node,9];
    eco_end = engineering_param[node,10];
    
    dead_storage = engineering_param[node,2];
    limited_irr_storage = engineering_param[node,5]*lim_irr_storage_disc_rate;
    limited_ind_lif_storage = engineering_param[node,4]*lim_ind_lif_storage_disc_rate;
    diver_storage = diversion_storage;   # 取水对应库容

    if (input[1] <= flood_end) and (input[1] >= flood_start):    # 汛期判断
        is_flood_season = 1;
    else:
        is_flood_season = 0;
        
        
    if (input[1] <= eco_end) and (input[1] >= eco_start):                # 生态周期判断
        is_eco_season = 1;
    else:
        is_eco_season = 0;


    if storage==0:
        storage = engineering_param[node,3];    # 起调库容定义
    else:
        pass

    loss=storage*0.02/30.4   # 水库损失水量

    if is_eco_season==1:
        ecological_demand=total_inflow/365*0.3
    else:
        ecological_demand=total_inflow/365*0.1   # 水库生态用水量

    net_inflow=max(0, input[4]+input[6]+input[7]+input[8]-loss-ecological_demand)   # 水库净来水量

    irr_demand_reserv = input[3]    # 灌溉需水量（针对水库）

    if storage<limited_irr_storage:
        irr_supply=min(storage+net_inflow-dead_storage, irr_rate*irr_demand_reserv)          # 水库灌溉供水量 (先计算灌溉供水能力，说明灌溉优先)
    else:
        irr_supply=min(storage+net_inflow-dead_storage, irr_demand_reserv)

    ind_lif_demand_reserv = input[5]                # 水库生活工业需水量

    if storage<diver_storage:
        ind_lif_supply=0          # 水库生活工业供水量
    else:
        if storage < limited_ind_lif_storage:
            ind_lif_supply=min(storage + net_inflow - irr_supply- dead_storage, ind_lif_rate * ind_lif_demand_reserv)
        else:
            ind_lif_supply=min(storage + net_inflow - irr_supply- dead_storage, ind_lif_demand_reserv)

    avail_water=max(storage+net_inflow-ind_lif_supply-irr_supply-diver_storage, 0)    # 南渡河可引余水
    

    results = [input[0], input[1], input[2], input[3], input[5], input[4], loss, ecological_demand,
         net_inflow, irr_demand_reserv, ind_lif_demand_reserv, irr_supply, ind_lif_supply, avail_water, input[6], input[7], input[8], is_flood_season]

    return results