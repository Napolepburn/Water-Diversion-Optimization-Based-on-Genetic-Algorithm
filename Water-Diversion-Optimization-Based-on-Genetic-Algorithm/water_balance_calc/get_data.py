# -*- coding: utf-8 -*

import numpy as np
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Read water conservancy project data
def data_read():

	base_path=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	
	input_water_variable = ['year', 'month', 'date', 'Irrigation water consumption', 'Reservoir inflow', 'Domestic and industrial water consumption', 'Other water source 1', 'Other water source 2', 'Other water source 3']

	# Read water conservancy project data
	node = pd.ExcelFile(os.path.join(base_path, 'water conservancy project data.xlsx')).sheet_names

	input_data = []
	for i in node:
		input_data.append(pd.read_excel(os.path.join(base_path, 'water conservancy project data.xlsx'), sheet_name=i).iloc[0:21916, 1:10][input_water_variable].values)
		
	return input_data, pd.read_excel(os.path.join(base_path, 'water conservancy project data.xlsx'), sheet_name=0)['hydro_year'].values

# Read characteristic parameters of water conservancy project
def global_var_def():
	
	base_path=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

	engineering_param = pd.read_excel(os.path.join(base_path, 'Basic parameters.xlsx'), sheet_name='Engineering parameters')[['Normal storage capacity','Flood storage capacity','Dead capacity','Start capacity','Domestic Limited Capacity', 
                                  'Agricultural Limited Capacity', 'Flood Start', 'Flood End', 'Annual average inflow', 'Ecological Start', 'Ecological End']].values
	charging_line = pd.read_excel(os.path.join(base_path, 'Basic parameters.xlsx'), sheet_name='Charging line').values.T[1:,:]

	return engineering_param, charging_line

	
if __name__ == "__main__":
	input_data, hydro_year = data_read()
	
	#global_var._init()
	engineering_param = global_var_def()[0]
	charging_line = global_var_def()[1]
	#global_var.set_value('engineering_param',global_var_def()[0])
	#global_var.set_value('charging_line',global_var_def()[1])