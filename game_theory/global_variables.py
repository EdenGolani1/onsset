import numpy as np

global outputFileName
global calibratedFileName
global endYear
global projectLife

global techLife
techLife = 30  # of grid

global ACT_COST_2GRID
global ACT_COST_2OFFGRID
ACT_COST_2GRID = 0  # currently not in use
ACT_COST_2OFFGRID = 0.2

global settlementGridInvestment
settlementGridInvestment = 0

global settlementOperAnzMaint

global fuelCost

global gtLatestDecision
gtLatestDecision = 0

global numOfSettlements
numOfSettlements_dj = 1473
numOfSettlements_ki = 27148
numOfSettlements = numOfSettlements_dj

global played_flag
played_flag = [1] * numOfSettlements

global moves_cnt_down
moves_cnt_down = [1] * numOfSettlements

