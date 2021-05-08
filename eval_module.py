# -*- coding: utf-8 -*-

import numpy as np
from numba import jit

@jit
def eval_func(hydro_year, year, month, date, ind_lif_demand_reserv, ind_lif_supply, irr_demand_reserv, irr_supply,irr_demand_total, mon_period=60, date_period=21915): # 输入为array数组
    

    
    # 生活工业缺水
    ind_lif_lack=ind_lif_supply - ind_lif_demand_reserv
    
    # 生活工业缺水破坏深度
    ind_lif_lack_ext=[]
    for i, j in zip(ind_lif_demand_reserv, ind_lif_lack):
        if i > 0:
            ind_lif_lack_ext.append(j/i)
        else:
            ind_lif_lack_ext.append(0)
    ind_lif_lack_ext=np.array(ind_lif_lack_ext)
    
    # 灌溉缺水
    irr_lack=irr_supply - irr_demand_reserv
    
    # 灌溉月缺水
    irr_lack_mon=[]
    for i, j, k in zip(year, month, date):
        if k == 1:
            irr_lack_mon.append(sum(irr_lack[np.where((year == i) & (month == j))]))
        else:
            irr_lack_mon.append(0)
    irr_lack_mon=np.array(irr_lack_mon)
            
    # 总灌溉月需水（即包括所有的）
    irr_demand_mon_total=[]
    for i, j, k in zip(year, month, date):
        if k == 1:
            irr_demand_mon_total.append(sum(irr_demand_total[np.where((year == i) & (month == j))]))
        else:
            irr_demand_mon_total.append(0)
    irr_demand_mon_total=np.array(irr_demand_mon_total)
    
    
    # 灌溉月缺水破坏深度
    irr_lack_mon_ext=[]
    for i, j, k in zip(irr_lack_mon, irr_demand_mon_total, date):
        if k == 1:
            if j !=0:
                irr_lack_mon_ext.append(float(i/j))
            else:
                irr_lack_mon_ext.append(0)
        else:
            irr_lack_mon_ext.append(0)
    irr_lack_mon_ext=np.array(irr_lack_mon_ext)
    
            
    # 年破坏性灌溉缺水
    irr_lack_yr=[]
    for i, j, k in zip(hydro_year, month, date):
        if (j == 5) & (k == 1):
            irr_lack_yr.append(sum(irr_lack_mon[np.where((hydro_year == i) & (irr_lack_mon_ext < -0.05))]))
        else:
            irr_lack_yr.append(0)
    irr_lack_yr=np.array(irr_lack_yr)   
            
    # 灌溉月保证率
    irr_mon_rate=(mon_period-len(np.where(irr_lack_yr < 0)[0]))/(mon_period+1)
    
    # 生活工业日保证率
    ind_lif_date_rate=(date_period-len(np.where(ind_lif_lack < 0)[0]))/(date_period+1)
    
    return [ind_lif_lack, ind_lif_lack_ext, irr_lack, irr_lack_mon, irr_lack_mon_ext, irr_lack_yr], irr_mon_rate, ind_lif_date_rate
    
@jit
def eval_func_opt(hydro_year, year, month, date, ind_lif_demand_reserv, ind_lif_supply, irr_demand_reserv, irr_supply,irr_demand_total, mon_period=60, date_period=21915): # 输入为array数组
    
    
    # 生活工业缺水
    ind_lif_lack=ind_lif_supply - ind_lif_demand_reserv
    
    # 生活工业缺水破坏深度
    ind_lif_lack_ext=[]
    for i, j in zip(ind_lif_demand_reserv, ind_lif_lack):
        if i > 0:
            ind_lif_lack_ext.append(j/i)
        else:
            ind_lif_lack_ext.append(0)
    ind_lif_lack_ext=np.array(ind_lif_lack_ext)
    
    # 灌溉缺水
    irr_lack=irr_supply - irr_demand_reserv
    
    # 灌溉月缺水
    irr_lack_mon=[]
    for i, j, k in zip(year, month, date):
        if k == 1:
            irr_lack_mon.append(sum(irr_lack[np.where((year == i) & (month == j))]))
        else:
            irr_lack_mon.append(0)
    irr_lack_mon=np.array(irr_lack_mon)
            
    # 总灌溉月需水（即包括所有的）
    irr_demand_mon_total=[]
    for i, j, k in zip(year, month, date):
        if k == 1:
            irr_demand_mon_total.append(sum(irr_demand_total[np.where((year == i) & (month == j))]))
        else:
            irr_demand_mon_total.append(0)
    irr_demand_mon_total=np.array(irr_demand_mon_total)
    
    
    # 灌溉月缺水破坏深度
    irr_lack_mon_ext=[]
    for i, j, k in zip(irr_lack_mon, irr_demand_mon_total, date):
        if k == 1:
            if j !=0:
                irr_lack_mon_ext.append(float(i/j))
            else:
                irr_lack_mon_ext.append(0)
        else:
            irr_lack_mon_ext.append(0)
    irr_lack_mon_ext=np.array(irr_lack_mon_ext)
    
            
    # 年破坏性灌溉缺水
    irr_lack_yr=[]
    for i, j, k in zip(hydro_year, month, date):
        if (j == 5) & (k == 1):
            irr_lack_yr.append(sum(irr_lack_mon[np.where((hydro_year == i) & (irr_lack_mon_ext < -0.05))]))
        else:
            irr_lack_yr.append(0)
    irr_lack_yr=np.array(irr_lack_yr)   
            
    # 灌溉月保证率
    irr_mon_rate=(mon_period-len(np.where(irr_lack_yr < 0)[0]))/(mon_period+1)
    
    # 生活工业日保证率
    #ind_lif_date_rate=(date_period-len(np.where(ind_lif_lack < 0)[0]))/(date_period+1)
    
    return irr_mon_rate, irr_lack_mon_ext
    
    
    
@jit
def opt_index_calc(hydro_year, Results, Nandu_storage, Final_total_diversion, init_disc_water):
    
    disc_water=[]
    irr_lack_mon_ext=[]
    Irr_mon_rate=[]
    
    disc_water.append(np.mean(np.array(init_disc_water).reshape(len(Final_total_diversion),1))*365)
    
    Data = np.array(np.array(Results)[:,0].tolist())[:,0:-1]
    irr_mon_rate, irr_lack_ext = eval_func_opt(hydro_year, year=Data[:,0], month=Data[:,1], date=Data[:,2], ind_lif_demand_reserv=Data[:,10], ind_lif_supply=Data[:,12], 
                  irr_demand_reserv=Data[:,9], irr_supply=Data[:,11], irr_demand_total=Data[:,3], mon_period=60, date_period=21915)

    irr_lack_mon_ext.append(min(irr_lack_ext))
    Irr_mon_rate.append(irr_mon_rate)
                  


    
    for node in np.arange(len(Results[0])-1):
        
        Data = np.array(np.array(Results)[:,node+1].tolist())
        
        disc_water.append(np.mean(Data[:,-1])*365)
        
        irr_mon_rate, irr_lack_ext = eval_func_opt(hydro_year, year=Data[:,0], month=Data[:,1], date=Data[:,2], ind_lif_demand_reserv=Data[:,10], ind_lif_supply=Data[:,12], 
                  irr_demand_reserv=Data[:,9], irr_supply=Data[:,11], irr_demand_total=Data[:,3], mon_period=60, date_period=21915)
        
        irr_lack_mon_ext.append(min(irr_lack_ext))
        Irr_mon_rate.append(irr_mon_rate)

    # 总弃水量
    total_disc_water=sum(disc_water)
    # 最严重破坏深度
    max_irr_lack_mon_ext=min(irr_lack_mon_ext)
    
    #print(Irr_mon_rate)
    #print(max_irr_lack_mon_ext)
    #print(total_disc_water)

    return Irr_mon_rate, max_irr_lack_mon_ext, total_disc_water
    
   
    
    
    