import global_variables as gv

# calculate the cost function for all the relavent players
def get_cost_function(df, alpha):
    beta = 1 - alpha
    df['Power'] = gv.settlementPower
    df['GridInvestment'] = gv.settlementGridInvestment
    df['OperationAndMaintenance'] = gv.settlementOperationAndMaintenance[:, -1]

    gridPower = df.loc[df['MinimumOverallCode' + str(gv.endYear)] == 1, 'Power'].sum()
    gridInvestment = df.loc[df['MinimumOverallCode' + str(gv.endYear)] == 1, 'GridInvestment'].sum()
    operationAndMaintenance = df.loc[df['MinimumOverallCode' + str(gv.endYear)] == 1, 'OperationAndMaintenance'].sum()
    priceConstant = gridInvestment/min(gv.projectLife, gv.techLife) + operationAndMaintenance
    settlementConsumption = df['EnergyPerSettlement' + str(gv.endYear)]
    gridConsumption = df.loc[df['MinimumOverallCode' + str(gv.endYear)] == 1, 'EnergyPerSettlement' + str(gv.endYear)].sum()
    priceVariable = gv.fuelCost*gridConsumption
    print(priceVariable)
    print(priceConstant)
    costFuncGrid = alpha*(gv.settlementPower/gridPower)*priceConstant + (settlementConsumption/gridConsumption)*(priceVariable + beta*priceConstant)
    costFuncNotGrid = df['MinimumOverallLCOE' + str(gv.endYear)]*settlementConsumption
    print(gv.settlementPower/gridPower)
    print(settlementConsumption/gridConsumption)

    # Tech is grid
    df.loc[df['MinimumOverallCode' + str(gv.endYear)] == 1, 'CostFunction'] = costFuncGrid
    # Tech is not grid
    df.loc[df['MinimumOverallCode' + str(gv.endYear)] != 1, 'CostFunction'] = costFuncNotGrid
