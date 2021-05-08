# -*- coding: utf-8 -*

import numpy as np
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__))) # 添加文件所在文件夹
#import global_var

def data_read():
	# 数据读取
	base_path=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	
	input_water_variable = ['年', '月', '日', '灌溉用水量', '水库来水量', '生活工业用水量', '其它外来水源1', '其它外来水源2', '其它外来水源3']

		# 输入水平衡变量读取
	node = pd.ExcelFile(os.path.join(base_path, '水利工程数据输入.xlsx')).sheet_names     # 获取各工程节点

	input_data = []     # 获取各工程节点数据
	for i in node:
		input_data.append(pd.read_excel(os.path.join(base_path, '水利工程数据输入.xlsx'), sheet_name=i).iloc[0:21916, 1:10][input_water_variable].values)
		
	return input_data, pd.read_excel(os.path.join(base_path, '水利工程数据输入.xlsx'), sheet_name=0)['水文年'].values


def global_var_def():
	
	base_path=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		# 基本参数读取
	engineering_param = pd.read_excel(os.path.join(base_path, '基本参数.xlsx'), sheet_name='工程参数')[['正常蓄水位对应库容','汛限水位对应库容','死库容','起调库容','生活工业限制供水库容', 
                                  '农业限制供水库容', '汛期开始月份', '汛期结束月份', '总来水量', '生态划分起始月份', '生态划分结束月份']].values
	charging_line = pd.read_excel(os.path.join(base_path, '基本参数.xlsx'), sheet_name='充库线').values.T[1:,:]

	return engineering_param, charging_line

	
if __name__ == "__main__":
	input_data, hydro_year = data_read()
	
	#global_var._init()
	engineering_param = global_var_def()[0]
	charging_line = global_var_def()[1]
	#global_var.set_value('engineering_param',global_var_def()[0])
	#global_var.set_value('charging_line',global_var_def()[1])