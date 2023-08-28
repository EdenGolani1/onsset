import numpy as np

global outputFileName
global calibratedFileName
global endYear
global projectLife
global techLife
techLife = 30  # of grid
global ACT_COST_2GRID
global ACT_COST_2OFFGRID
ACT_COST_2GRID = 0.2
ACT_COST_2OFFGRID = 0.05
global settlementGridInvestment
global settlementOperAndMaint
global fuelCost
global gtLatestDecision
gtLatestDecision = 0
global numOfSettlements
numOfSettlements = 1473
global played_flag
played_flag = [1] * numOfSettlements
global moves_cnt_down
moves_cnt_down = [2] * numOfSettlements

