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
    diver_storage = diversion_storage; 

    if (input[1] <= flood_end) and (input[1] >= flood_start):    # Flood season judgment
        is_flood_season = 1;
    else:
        is_flood_season = 0;
        
        
    if (input[1] <= eco_end) and (input[1] >= eco_start):                # Ecological cycle judgment
        is_eco_season = 1;
    else:
        is_eco_season = 0;


    if storage==0:
        storage = engineering_param[node,3];    # Adjust storage capacity definition
    else:
        pass

    loss=storage*0.02/30.4   # Water loss

    if is_eco_season==1:
        ecological_demand=total_inflow/365*0.3
    else:
        ecological_demand=total_inflow/365*0.1   # Ecological water consumption of reservoir

    net_inflow=max(0, input[4]+input[6]+input[7]+input[8]-loss-ecological_demand)   # Net inflow

    irr_demand_reserv = input[3]    # Irrigation water demand

    if storage<limited_irr_storage:
        irr_supply=min(storage+net_inflow-dead_storage, irr_rate*irr_demand_reserv)          # irrigation water supply from reservoir 
    else:
        irr_supply=min(storage+net_inflow-dead_storage, irr_demand_reserv)

    ind_lif_demand_reserv = input[5]                # domestic and industrial water demand for reservoir 

    if storage<diver_storage:
        ind_lif_supply=0          # domestic industrial water supply for reservoir 
    else:
        if storage < limited_ind_lif_storage:
            ind_lif_supply=min(storage + net_inflow - irr_supply- dead_storage, ind_lif_rate * ind_lif_demand_reserv)
        else:
            ind_lif_supply=min(storage + net_inflow - irr_supply- dead_storage, ind_lif_demand_reserv)

    avail_water=max(storage+net_inflow-ind_lif_supply-irr_supply-diver_storage, 0)    # Available water
    

    results = [input[0], input[1], input[2], input[3], input[5], input[4], loss, ecological_demand,
         net_inflow, irr_demand_reserv, ind_lif_demand_reserv, irr_supply, ind_lif_supply, avail_water, input[6], input[7], input[8], is_flood_season]

    return results