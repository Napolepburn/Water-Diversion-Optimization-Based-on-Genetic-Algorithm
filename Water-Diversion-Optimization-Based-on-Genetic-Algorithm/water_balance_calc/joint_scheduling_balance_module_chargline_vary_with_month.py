# -*- coding: utf-8 -*

import numpy as np
import time
from numba import jit
import initial_unit_water_balance_module, watered_unit_water_balance_module_chargline_vary_with_month, reservior_capacity_calculation_module
#import global_var

#engineering_param = global_var.get_value('engineering_param')

@jit
def joint_dispatch_balance(input, engineering_param, charging_line, design_diversion, into_reserv_or_not, eco_demand_vary, other_modul_water_or_not, 
                           other_modul_water_design, charging_line_disc_rate, lim_irr_storage_disc_rate, lim_ind_lif_storage_disc_rate,
                           diversion_storage=3370, irr_rate1=0.6, ind_lif_rate1=0.7, irr_rate2=0.6, ind_lif_rate2=0.8, div_loss_rate=0.95):
    
    # 计时
    #time_start = time.time()
    #module1_cost=[]; module2_cost=[]; module3_cost=[]

    Nandu_storage = [3602]             
    Available_Diversion = []             
    Final_total_diversion = []            
    Results_all = []
    init_disc_water = []            
    
    node_num = len(input)
    
    reserv_ahead_storage = [[0,0,0,0]]
    for day in np.arange(len(input[0])): 
        
        Available_Diversion_0 = []
        final_total_diversion = []
        Results_step = []
        reserv_ahead_storage_0 = []
        
        #time_start1 = time.time()
        
        Results_step.append(initial_unit_water_balance_module.initial_water_balance(input[0][day,:], 0, total_inflow=engineering_param[0,8], 
            engineering_param = engineering_param, lim_irr_storage_disc_rate=lim_irr_storage_disc_rate[0], lim_ind_lif_storage_disc_rate=lim_ind_lif_storage_disc_rate[0], 
                irr_rate=irr_rate1,ind_lif_rate=ind_lif_rate1, diversion_storage=diversion_storage, storage=Nandu_storage[-1]))   
                
        #module1_cost.append(time.time() - time_start1)
        
        Available_Diversion_0.append(Results_step[-1][13])
        
        for node in np.arange(node_num-1):
        
            #time_start2 = time.time()
            Results_step.append(watered_unit_water_balance_module_chargline_vary_with_month.reservior_water_balance(input[node+1][day,:], engineering_param, charging_line, 
                node+1,total_inflow=engineering_param[node+1,8], design_diversion=design_diversion[node+1], 
                available_diversion=Available_Diversion_0[-1], 
                charging_line_disc_rate=charging_line_disc_rate[node+1],lim_irr_storage_disc_rate=lim_irr_storage_disc_rate[node+1], lim_ind_lif_storage_disc_rate=lim_ind_lif_storage_disc_rate[node+1], 
                into_reserv_or_not=into_reserv_or_not[node+1], eco_demand_vary=eco_demand_vary[node+1], other_modul_water_or_not=other_modul_water_or_not[node+1], 
                        other_modul_water_design=other_modul_water_design[node+1], 
                        irr_rate=irr_rate2,ind_lif_rate=ind_lif_rate2, div_loss_rate=div_loss_rate, storage=reserv_ahead_storage[-1][node]))  
            
            #module2_cost.append(time.time() - time_start2)
            
            reserv_ahead_storage_0.append(Results_step[-1][16])
            
            diversion = Results_step[-1][14]/div_loss_rate
            Available_Diversion_0.append(Available_Diversion_0[-1]-diversion)
            final_total_diversion.append(diversion)


        Available_Diversion.append(Available_Diversion_0)

        Final_total_diversion.append(sum(final_total_diversion))
        
        #time_start3 = time.time()
        Nandu_storage.append(reservior_capacity_calculation_module.storage_calc(0, engineering_param, Results_step[0][8], Results_step[0][12], Results_step[0][11],
                                                                                is_flood_season = Results_step[0][17], other_supply=Final_total_diversion[-1], ahead_storage=Nandu_storage[-1]))
        #module3_cost.append(time.time() - time_start3)
        
        Results_all.append(Results_step)
        reserv_ahead_storage.append(reserv_ahead_storage_0)
        
        init_disc_water.append(Nandu_storage[-2]+Results_step[0][8]-Nandu_storage[-1]-Results_step[0][11]-Results_step[0][12]-Final_total_diversion[-1])
        
    #time_end = time.time()
    
    #print('module1 cost', sum(module1_cost), 's')
    #print('module2 cost', sum(module2_cost), 's')
    #print('module3 cost', sum(module3_cost), 's')
    #print('totally cost', time_end - time_start, 's')
    
    return Results_all, reserv_ahead_storage, Nandu_storage, Available_Diversion, Final_total_diversion, init_disc_water