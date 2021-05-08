# -*- coding: utf-8 -*

import numpy as np
import pandas as pd
pd.set_option('display.max_columns',None)
pd.set_option('display.max_rows',None)

import os
import time
from numba import jit
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__))) # 添加文件所在文件夹
import joint_scheduling_balance_module
from eval_module import eval_func, eval_func_opt, opt_index_calc


# 平衡过程输出
def balance_process(Results, Nandu_storage, Final_total_diversion, init_disc_water, save_path=None, save_or_not=0):
    
    #base_path=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    water_rate=[]; other_index=[]
    
    Data = np.concatenate([np.array(np.array(Results)[:,0].tolist())[:,0:-1], np.array(Nandu_storage[1:]).reshape(len(Final_total_diversion),1), 
        np.array(Final_total_diversion).reshape(len(Final_total_diversion),1), np.array(init_disc_water).reshape(len(Final_total_diversion),1)], axis=1)
    
    water_lack, irr_mon_rate, ind_lif_date_rate = eval_func(hydro_year, year=Data[:,0], month=Data[:,1], date=Data[:,2], ind_lif_demand_reserv=Data[:,10], ind_lif_supply=Data[:,12], 
                  irr_demand_reserv=Data[:,9], irr_supply=Data[:,11], irr_demand_total=Data[:,3], mon_period=60, date_period=21915)
    
    water_rate.append([irr_mon_rate, ind_lif_date_rate])
      
    table_sum1=pd.concat([pd.DataFrame(data= Data, columns=['年', '月', '日', '总灌溉需水量', '总生活工业需水量', '水库来水量', '水库损失水量',
                '水库生态用水量','水库净入水量','水库灌溉需水','水库生活工业需水','水库灌溉供水','水库生活工业供水','可引水量',
                    '其它外来水源1','其它外来水源2','其它外来水源3', '库容水量', '总引水', '弃水量'],dtype=np.float),
                    pd.DataFrame(data= np.array(water_lack).T, columns=['生活工业缺水', '生活工业缺水破坏深度', '灌溉缺水', 
                                 '灌溉月缺水', '灌溉月缺水破坏深度', '年破坏性灌溉缺水'],dtype=np.float)], axis=1)
    
    other_index.append([365*table_sum1['弃水量'].mean(), 365*table_sum1['灌溉缺水'].mean(),
                        table_sum1['灌溉月缺水破坏深度'].min(), np.sum(np.array(table_sum1['灌溉月缺水破坏深度'].tolist())<-0.05), 30*table_sum1['灌溉月缺水破坏深度'].mean(), 
                            365*table_sum1['生活工业缺水'].mean(), 0])

    if save_or_not==1:
        writer=pd.ExcelWriter(save_path)
        table_sum1.to_excel(writer, sheet_name='0')
        writer.save()  
    else:
        pass
    
    for node in np.arange(len(Results[0])-1):
        
        Data = np.array(np.array(Results)[:,node+1].tolist())
        
        water_lack, irr_mon_rate, ind_lif_date_rate = eval_func(hydro_year, year=Data[:,0], month=Data[:,1], date=Data[:,2], ind_lif_demand_reserv=Data[:,10], ind_lif_supply=Data[:,12], 
                  irr_demand_reserv=Data[:,9], irr_supply=Data[:,11], irr_demand_total=Data[:,3], mon_period=60, date_period=21915)
        
        table_sum2=pd.concat([pd.DataFrame(data=Data, columns=['年','月','日','总灌溉需水量','总生活工业需水量','水库来水量','水库损失水量',
                                                '水库生态用水量','水库净入水量','水库灌溉需水','水库生活工业需水','水库灌溉供水','水库生活工业供水',
                                               '计算引水', '实际引水',  '经调节计算所得其它水源', '库容水量','其它外来水源1',
                                               '其它外来水源2','其它外来水源3','弃水量'],dtype=np.float), 
                pd.DataFrame(data= np.array(water_lack).T, columns=['生活工业缺水', '生活工业缺水破坏深度', '灌溉缺水', 
                                 '灌溉月缺水', '灌溉月缺水破坏深度', '年破坏性灌溉缺水'],dtype=np.float)], axis=1)
    
        other_index.append([365*table_sum2['弃水量'].mean(), 365*table_sum2['灌溉缺水'].mean(),
                        table_sum2['灌溉月缺水破坏深度'].min(),  np.sum(np.array(table_sum2['灌溉月缺水破坏深度'].tolist())<-0.05), 30*table_sum2['灌溉月缺水破坏深度'].mean(), 
                            365*table_sum2['生活工业缺水'].mean(), table_sum2['实际引水'].max()/8.64])
    
        if save_or_not==1:
            table_sum2.to_excel(writer, sheet_name=str(node+1))
            writer.save()  
        else:
            pass
    
        water_rate.append([irr_mon_rate, ind_lif_date_rate])
        
    Rate=pd.DataFrame(data=np.hstack((np.array(water_rate),np.array(other_index))), columns=['灌溉月保证率','生活工业日保证率',
                      '年均弃水量','年均灌溉缺水量','最大月灌溉缺水破坏深度','月灌溉缺水破坏深度<-0.05月份个数','平均月灌溉缺水破坏深度','年均生活工业缺水量','最大引水流量'])
    print(Rate)
    
    if save_or_not==1:
        Rate.to_excel(writer, sheet_name='指标汇总')
        writer.save()
    else:
        pass
        
    

if __name__ == "__main__":
    # 联合调度参数
    design_diversion = [0,
2,	2,	4.5,	0.8

]
    into_reserv_or_not = [0,1,0,0,1]
    eco_demand_vary = [0,0,0,1,0]
    other_modul_water_or_not = [0,0,0,1,0]
    other_modul_water_design = [0,0,0,3,0]
    charging_line_disc_rate = [1,
0.632081784,	0.975779009,	0.585394771,	0.836771527
]
    lim_irr_storage_disc_rate = [9.21963E-05,	0.028245302,	0.051124125,	0.022424391,	0.004174111
]
    lim_ind_lif_storage_disc_rate = [1]*5
    
    
    time_start0=time.time()
    Results, reserv_ahead_storage, Nandu_storage, Available_Diversion, Final_total_diversion, init_disc_water = joint_scheduling_balance_module.joint_dispatch_balance(input_data, 
                    engineering_param, charging_line, design_diversion, 
                    into_reserv_or_not, eco_demand_vary, other_modul_water_or_not, 
                           other_modul_water_design, charging_line_disc_rate, lim_irr_storage_disc_rate, lim_ind_lif_storage_disc_rate,
                           diversion_storage=3370, irr_rate1=0.6, ind_lif_rate1=0.7, irr_rate2=0.6, ind_lif_rate2=0.8, div_loss_rate=0.95)
                           
    print('all cost1', time.time() - time_start0, 's')
    balance_process(Results, Nandu_storage, Final_total_diversion, init_disc_water, save_path=r'C:\Users\hu.jy\Desktop\results2.xls', save_or_not=0) # save_path=r'C:\Users\Administrator\Desktop\南渡河四库日进库程序\results\results.xls',
    #print(opt_index_calc(hydro_year, Results, Nandu_storage, Final_total_diversion, init_disc_water))
    print('all cost2', time.time() - time_start0, 's')