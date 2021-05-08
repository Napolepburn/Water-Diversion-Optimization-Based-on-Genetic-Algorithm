# -*- coding: utf-8 -*

import numpy as np
from numba import jit
import reservior_capacity_calculation_module
#import global_var

#engineering_param = global_var.get_value('engineering_param')
#charg_line = global_var.get_value('charging_line')

@jit
def reservior_water_balance(input, engineering_param, charging_line, node, total_inflow, design_diversion, 
                            available_diversion, charging_line_disc_rate=1.0, lim_irr_storage_disc_rate=1.0, lim_ind_lif_storage_disc_rate=1.0, 
                                into_reserv_or_not =1, eco_demand_vary = 0, other_modul_water_or_not = 0, 
                                    other_modul_water_design = 3, irr_rate = 0.6, ind_lif_rate = 0.8, div_loss_rate=0.95, storage=0):   

    flood_start = engineering_param[node,6];
    flood_end = engineering_param[node,7];
    eco_start = engineering_param[node,9];
    eco_end = engineering_param[node,10];
    
    dead_storage = engineering_param[node,2];
    limited_irr_storage = engineering_param[node,5]*lim_irr_storage_disc_rate;
    limited_ind_lif_storage = engineering_param[node,4]*lim_ind_lif_storage_disc_rate;
    charg_line = charging_line[node,int(input[1]-1)]*charging_line_disc_rate;

    if (input[1] <= flood_end) and (input[1] >= flood_start):                # 汛期判断
        is_flood_season = 1;
    else:
        is_flood_season = 0;
        
        
    if (input[1] <= eco_end) and (input[1] >= eco_start):                # 生态周期判断
        is_eco_season = 1;
    else:
        is_eco_season = 0;


    if storage==0:
        storage = engineering_param[node,3];     # 前期库容定义
    else:
        pass

    loss=storage*0.02/30.4   # 水库损失水量

    if eco_demand_vary == 0:                                                                            # 水库生态用水量
        ecological_demand = total_inflow / 365 * 0.1
    else:
        if is_eco_season == 1:
            ecological_demand=total_inflow/365*0.3
        else:
            ecological_demand=total_inflow/365*0.1                                                  # 水库生态用水量

    net_inflow=max(0, input[4]+input[6]+input[7]+input[8]-loss-ecological_demand)   # 水库净来水量（考虑其它水源后的净值; 此外来水源无需经过调节得到）

    if into_reserv_or_not==1:                                                                  
        irr_demand_reserv = input[3];
        theoretical_diversion=0;
        practical_diversion=min(design_diversion*8.64*div_loss_rate, available_diversion*div_loss_rate, max(0, charg_line-storage-net_inflow+irr_demand_reserv));                                                      # 引水量计算
    else:
        if storage+net_inflow > charg_line:                                                                         #  令不入库时不同时引、弃水
            theoretical_diversion = min(design_diversion*8.64*div_loss_rate, available_diversion*div_loss_rate, 0);
            practical_diversion = min(theoretical_diversion, input[3]);
            irr_demand_reserv = - (practical_diversion - input[3]);                                                # 灌溉需水量（引水后， 针对水库）
        else:
            theoretical_diversion=min(design_diversion*8.64*div_loss_rate, available_diversion*div_loss_rate, input[3]);
            practical_diversion = min(theoretical_diversion, input[3]);
            irr_demand_reserv = - (practical_diversion - input[3]);                                                # 灌溉需水量（引水后， 针对水库）

    ind_lif_demand_reserv = input[5]

    if other_modul_water_or_not == 0:                                                                                       # 其它外来水源（需调节得到）计算
        other_modul_water_source = 0;
    else:
        other_modul_water_source = min(other_modul_water_design*8.64, max(0, charg_line-storage-net_inflow+ind_lif_demand_reserv+irr_demand_reserv));


    if into_reserv_or_not == 1:
        if storage < limited_ind_lif_storage:                                                                                                            # 水库生活工业供水量 （生活工业供水优先）
            ind_lif_supply = min(storage + net_inflow + other_modul_water_source+practical_diversion - dead_storage, ind_lif_rate * ind_lif_demand_reserv);                                                                                                 # 水库生活工业供水量
        else:
            ind_lif_supply = min(storage + net_inflow + other_modul_water_source+practical_diversion - dead_storage, ind_lif_demand_reserv);
    else:
        if storage < limited_ind_lif_storage:                                                                                                            # 水库生活工业供水量 （生活工业供水优先）
            ind_lif_supply = min(storage + net_inflow + other_modul_water_source - dead_storage, ind_lif_rate * ind_lif_demand_reserv);                                                                                                 # 水库生活工业供水量
        else:
            ind_lif_supply = min(storage + net_inflow + other_modul_water_source - dead_storage, ind_lif_demand_reserv);


    if into_reserv_or_not == 1:
        if storage < limited_irr_storage:
            irr_supply = min(storage + net_inflow + other_modul_water_source + practical_diversion - ind_lif_supply - dead_storage, max(0, irr_rate * input[3]));                                          # 水库灌溉供水量
        else:
            irr_supply = min(storage + net_inflow + other_modul_water_source + practical_diversion - ind_lif_supply - dead_storage, irr_demand_reserv);
    else:
        if storage < limited_irr_storage:
            irr_supply = min(storage + net_inflow + other_modul_water_source - ind_lif_supply - dead_storage, max(0, irr_rate * input[3]-practical_diversion));
        else:
            irr_supply = min(storage + net_inflow + other_modul_water_source - ind_lif_supply - dead_storage, irr_demand_reserv);

    if into_reserv_or_not == 1:
        new_storage = reservior_capacity_calculation_module.storage_calc(node, engineering_param, net_inflow, ind_lif_supply, irr_supply, is_flood_season, other_inflow=practical_diversion+other_modul_water_source,
                 ahead_storage=storage);
    else:
        new_storage = reservior_capacity_calculation_module.storage_calc(node, engineering_param, net_inflow, ind_lif_supply, irr_supply, is_flood_season, other_inflow=other_modul_water_source, ahead_storage=storage);
        
    if into_reserv_or_not == 1:
        disc_water = max(storage + net_inflow + practical_diversion - new_storage - ind_lif_supply - irr_supply, 0)
    else:
        disc_water = max(storage + net_inflow - new_storage - ind_lif_supply - irr_supply, 0)

    results = [input[0], input[1], input[2], input[3], input[5], input[4], loss, ecological_demand, net_inflow, irr_demand_reserv,
                       ind_lif_demand_reserv, irr_supply, ind_lif_supply, theoretical_diversion, practical_diversion, other_modul_water_source, new_storage,
                            input[6], input[7], input[8], disc_water]

    return results