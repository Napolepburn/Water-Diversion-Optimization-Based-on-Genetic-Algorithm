# -*- coding: utf-8 -*-

import numpy as np
from deap import base, tools, creator, algorithms
from scoop import futures
from multiprocessing.pool import ThreadPool
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
import time
import random
import matplotlib.pyplot as plt
from tqdm import tqdm
#for i in tqdm(range(10000)):
import pickle
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
import joint_scheduling_balance_module_chargline_vary_with_month
from eval_module import eval_func_opt, opt_index_calc



#Define the problem
creator.create('MultiObj',base.Fitness,weights=(1, 1, 1))     
creator.create('Individual',list,fitness = creator.MultiObj)
    # Encoding
def genInd(low, up):
    return [random.uniform(i, j) for i,j in zip(low, up)]# Real number encoding

toolbox  = base.Toolbox()

    # Define the number of decision variables and the upper and lower boundaries
Ndim = 57
low = [0,0,0,0]+ [0.5]*48 + [0]*5
up = [5,5,8,5,]+ [1]*48 + [0.3]*5

toolbox.register('genInd',genInd,low,up)    
toolbox.register('individual', tools.initIterate, creator.Individual,toolbox.genInd)
#print(toolbox.individual())


    #Objective function definition
def joint_scheduling(ind, input_data=input_data, engineering_param=engineering_param, 
                     charging_line=charging_line, hydro_year=hydro_year):
    start_time=time.time()
    
    charging_line_disc_rate = [[1, 1,	1,	1,	1, 1, 1, 1,	1, 1, 1, 1],
            [ind[4], ind[5],ind[6],ind[7],ind[8],ind[9],ind[10],ind[11],ind[12],ind[13],ind[14],ind[15]],
            [ind[16], ind[17],ind[18],ind[19],ind[20],ind[21],ind[22],ind[23],ind[24],ind[25],ind[26],ind[27]],
            [ind[28], ind[29],ind[30],ind[31],ind[32],ind[33],ind[34],ind[35],ind[36],ind[37],ind[38],ind[39]],
            [ind[40], ind[41],ind[42],ind[43],ind[44],ind[45],ind[46],ind[47],ind[48],ind[49],ind[50],ind[51]]]
    
    Results, reserv_ahead_storage, Nandu_storage, Available_Diversion, Final_total_diversion, init_disc_water = joint_scheduling_balance_module_chargline_vary_with_month.joint_dispatch_balance(input_data, 
                    engineering_param, charging_line, design_diversion=[0,ind[0],ind[1],ind[2],ind[3]], 
                    into_reserv_or_not = [0,1,0,0,1], eco_demand_vary = [0,0,0,1,0], other_modul_water_or_not = [0,0,0,1,0], 
                           other_modul_water_design = [0,0,0,3,0], charging_line_disc_rate = charging_line_disc_rate, lim_irr_storage_disc_rate = [ind[52],ind[53],ind[54],ind[55],ind[56]], lim_ind_lif_storage_disc_rate = [1]*5,
                           diversion_storage=3370, irr_rate1=0.6, ind_lif_rate1=0.7, irr_rate2=0.6, ind_lif_rate2=0.8, div_loss_rate=0.95)
                           
    Irr_mon_rate, max_irr_lack_mon_ext, total_disc_water=opt_index_calc(hydro_year, Results, Nandu_storage, Final_total_diversion, init_disc_water)
    
    f1 = total_disc_water
    f2 = -1*max_irr_lack_mon_ext
    f3 = Irr_mon_rate[0]
    f4 = Irr_mon_rate[1]
    f5 = Irr_mon_rate[2]
    f6 = Irr_mon_rate[3]
    f7 = Irr_mon_rate[4]
    
    print('totally cost', time.time() - start_time, 's')

    return f3, 0.8*f4+0.75*f5+0.9*f6+0.8*f7, f3+f6 


toolbox.register('evaluate',joint_scheduling, input_data=input_data, engineering_param=engineering_param, 
                 charging_line=charging_line, hydro_year=hydro_year)



# Optimize parameter settings
N_POP = 148# selTournamentDCD: individuals length must be a multiple of 4
toolbox.register('population', tools.initRepeat, list, toolbox.individual)

    # Evolution parameters
toolbox.register('selectGen1', tools.selTournament, tournsize=2)
toolbox.register('select', tools.emo.selTournamentDCD) 
toolbox.register('mate', tools.cxSimulatedBinaryBounded, eta=20.0, low=low, up=up)# This implementation is similar to the one implemented in the original NSGA-II C code presented by Deb.
toolbox.register('mutate', tools.mutPolynomialBounded, eta=20.0, low=low, up=up, indpb=1.0/Ndim)  #Polynomial mutation as implemented in original NSGA-II algorithm in C by Deb.

NGEN = 100
CXPB = 0.8
MUTPB = 0.2

    
# Evolutionary computing
def opt_main(save_it=0, data_save_path=None):
    
    pop0 = toolbox.population(n=N_POP) 
       
    #First generation
    fitnesses = toolbox.map(toolbox.evaluate, pop0)    
    for ind, fitness in zip(pop0,fitnesses):    
        ind.fitness.values = fitness    
    
    pop = toolbox.clone(pop0)
    
    start_time2=time.time()
    fronts = tools.emo.sortNondominated(pop0,k=N_POP,first_front_only=False)#Fast non-dominated sorting
    print('sort_cost1', time.time() - start_time2, 's')
    
    for idx,front in enumerate(fronts):
        for ind in front:
            ind.fitness.values = (idx+1),
    
    offspring = toolbox.selectGen1(pop0,N_POP)
    offspring = algorithms.varAnd(offspring,toolbox,CXPB,MUTPB)
    
        
        #First, the parental population Pp is duplicated using the toolbox.clone() method and the result is put into the offspring population Po.
        #A first loop over Po is executed to mate pairs of consecutive individuals. 
        #According to the crossover probability cxpb, the individuals xi and xi+1 are mated using the toolbox.mate() method. 
        #The resulting children yi and yi+1 replace their respective parents in Po. 
        #A second loop over the resulting Po is executed to mutate every individual with a probability mutpb. 
        #When an individual is mutated it replaces its not mutated version in Po. The resulting Po is returned.
        
    
    
    BestInd=[]
    BestFit=[]
    Preto_front=[]
    Preto_front_fitness=[]

    #The second generation begins to cyclically evolve
    for gen in tqdm(range(1,NGEN)):
        
        BestInd0=[]
        BestFit0=[]
        
        Preto_front0=[]
        Preto_front_fitness0=[]
        
        fitnesses = toolbox.map(toolbox.evaluate,offspring)
        for ind,fitness in zip(offspring,fitnesses):
            ind.fitness.values = fitness
            
        combinedPop = pop + offspring  
    
        start_time3=time.time()
        fronts = tools.emo.sortNondominated(combinedPop,k=N_POP,first_front_only=False)
        print('sort_cost2', time.time() - start_time3, 's')
    
        for front in fronts:
            tools.emo.assignCrowdingDist(front)
        pop = []
        for front in fronts:
            pop += front
        pop = toolbox.clone(pop)
        pop = tools.selNSGA2(pop,k=N_POP,nd='standard')
    
        offspring = toolbox.select(pop,N_POP)
        offspring = toolbox.clone(offspring)
        offspring = algorithms.varAnd(offspring,toolbox,CXPB,MUTPB)
        
        
        # Select and print out the best frontier individuals in the population
        bestInd = tools.selBest(pop,1)
        BestInd0.append(bestInd)
        BestInd.append(BestInd0)
        
        for bestfit in bestInd:
            BestFit0.append(bestfit.fitness.values)
        BestFit.append(BestFit0)
        
        print('best solution:',bestInd)
        print('best fitness:',BestFit0)
        
       
         # Select the individual with the best preto
        preto_front = tools.emo.sortNondominated(pop,len(pop))[0]
        Preto_front0.append(preto_front)
        Preto_front.append(Preto_front0)
        
        for preto_fitness in preto_front:
            Preto_front_fitness0.append(preto_fitness.fitness.values)
        Preto_front_fitness.append(Preto_front_fitness0)
        
        
        
    if save_it==1:
        fw=open(data_save_path, 'wb')
        pickle.dump(Preto_front, fw)
        pickle.dump(Preto_front_fitness, fw)
        fw.close()
    else:
        pass

    return Preto_front, Preto_front_fitness


if __name__ == "__main__":

    start_time4=time.time()
    Preto_front, Preto_front_fitness = opt_main(save_it=1, data_save_path=r'F:\Pycharm_python\python_test\南渡河四库日进库程序\results\option3.txt')
    print('sort_cost3', time.time() - start_time4, 's')

    # Output result
    Gen_id=[]
    Preto_Front_Set=[]
    Preto_Front_Fitness_Set=[]
    Gen=len(Preto_front)
    for gen in range(Gen):
        for ind in range(len(Preto_front[gen][0])):
            Gen_id.append(gen+2)
            Preto_Front_Set.append(Preto_front[gen][0][ind])
            Preto_Front_Fitness_Set.append(list(Preto_front_fitness[gen][ind]))
        
        writer=pd.ExcelWriter(r'F:\Pycharm_python\python_test\XX河四库日进库程序\results\option3_result.xlsx')
        Merge=np.concatenate((np.array(Gen_id).reshape(len(Gen_id), 1), np.array(Preto_Front_Set), np.array(Preto_Front_Fitness_Set)), axis=1)
        pd.DataFrame(data=Merge).to_excel(writer, sheet_name='1')
        writer.save()  
