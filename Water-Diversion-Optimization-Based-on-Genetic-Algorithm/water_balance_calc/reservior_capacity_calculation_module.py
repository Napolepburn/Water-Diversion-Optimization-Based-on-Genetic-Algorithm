# -*- coding: utf-8 -*

import numpy as np
from numba import jit
#import global_var

#engineering_param = global_var.get_value('engineering_param')
	
@jit
def storage_calc(node, engineering_param, net_inflow, ind_lif_supply, irr_supply, is_flood_season = 1, other_inflow=0, other_supply=0, ahead_storage=0):

    usable_storage= engineering_param[node,0];
    flood_limit_storage = engineering_param[node,1];

    if is_flood_season == 1:
        storage = min(ahead_storage + net_inflow + other_inflow - ind_lif_supply - irr_supply - other_supply, flood_limit_storage);
    else:
        storage = min(ahead_storage + net_inflow + other_inflow - ind_lif_supply - irr_supply - other_supply, usable_storage);

    return storage