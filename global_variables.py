import numpy as np

global outputFileName
global calibratedFileName

global endYear
global projectLife
global techLife
techLife = 30  # of grid
global ACT_COST_2GRID
global ACT_COST_2OFFGRID
ACT_COST_2GRID = 1.05
ACT_COST_2OFFGRID = 0.9

global settlementGridInvestment
#settlementGridInvestment = 0
global settlementOperAndMaint

#global counter #todo _OUR: for counting iterations in get_lcoe
global fuelCost

global gtLatestDecision
gtLatestDecision = 0


global people
global new_connections
global prev_code
global total_energy_per_cell
global energy_per_cell
global additional_mv_line_length
global additional_transformer
global productive_nodes
global elec_loop
