from game_theory import global_variables as gv
import numpy as np

TotalCost = 0


# calculate the cost function for all the relevant players
def game_iterations(df, alpha, num_of_moves=1, enableConnection=False):
    # initializing parameters for the loop
    df['GT_LatestDecision'] = df['MinimumOverallCode' + str(gv.endYear)]  # create new column in the main df

    # make one move
    get_cost_function(df, alpha)
    players_cntr = gv.numOfSettlements
    moves_cntr = 0
    while moves_cntr < num_of_moves:
        played = player_move(df, enableConnection)
        players_cntr -= 1
        if played:
            moves_cntr += 1
        if players_cntr == 0 or not (df['delta'] > 0).any():
            break
    """df['GT_played_flag'] = gv.played_flag
    df['GT_LatestDecision'] = np.where(df['GT_played_flag'] == 2, 0, df['GT_LatestDecision'])
    print("========================================================================")"""
    gv.gtLatestDecision = df['GT_LatestDecision'].copy()
    return moves_cntr


def get_cost_function(df, alpha=0.5):
    global TotalCost
    # New columns (preparation to the parameters)
    df['GT_GridInvestment'] = gv.settlementGridInvestment
    df['GT_OperationAndMaintenance'] = gv.settlementOperAndMaint[:, -1]

    # Setting the parameters to the function
    beta = 1 - alpha
    settlementPop = df['Pop' + str(gv.endYear)]
    gridPop = df.loc[df['GT_LatestDecision'] == 1, 'Pop' + str(gv.endYear)].sum()
    df['GT_PotentialGridPop'] = np.where(df['GT_LatestDecision'] == 1, gridPop, gridPop + df['Pop' + str(gv.endYear)])

    gridInvestment = df.loc[df['GT_LatestDecision'] == 1, 'GT_GridInvestment'].sum()

    df['GT_PotentialGridInvestment'] = np.where(df['GT_LatestDecision'] == 1, gv.settlementGridInvestment, gv.settlementGridInvestment + df['GT_GridInvestment'])

    operationAndMaintenance = df.loc[df['GT_LatestDecision'] == 1, 'GT_OperationAndMaintenance'].sum()
    df['GT_PotentialOperationAndMaintenance'] = np.where(df['GT_LatestDecision'] == 1, operationAndMaintenance, operationAndMaintenance + df['GT_OperationAndMaintenance'])

    settlementConsumption = df['EnergyPerSettlement' + str(gv.endYear)]
    gridConsumption = df.loc[df['GT_LatestDecision'] == 1, 'EnergyPerSettlement' + str(gv.endYear)].sum()
    df['GT_PotentialGridConsumption'] = np.where(df['GT_LatestDecision'] == 1, gridConsumption, gridConsumption + df['EnergyPerSettlement' + str(gv.endYear)])

    priceVariableScalar = gv.fuelCost * gridConsumption
    priceVariable = gv.fuelCost * df['GT_PotentialGridConsumption']
    priceConstant = gv.settlementGridInvestment / min(gv.projectLife, gv.techLife) + operationAndMaintenance
    df['GT_PotentialPriceConstant'] = np.where(df['GT_LatestDecision'] == 1, priceConstant, df['GT_PotentialGridInvestment'] / min(gv.projectLife, gv.techLife) + df['GT_PotentialOperationAndMaintenance'])
    #print(f"df['GT_PotentialPriceConstant']: {df['GT_PotentialPriceConstant'][player_id]}")
    # Cost Function if the tech is grid
    gridCostFunc = alpha*(settlementPop/df['GT_PotentialGridPop'])*df['GT_PotentialPriceConstant'] + (settlementConsumption/df['GT_PotentialGridConsumption'])*(priceVariable + beta * df['GT_PotentialPriceConstant'])
    df['GT_GridCostFunction'] = gridCostFunc

    PrevTotalCost = TotalCost
    TotalCost = np.where(df['GT_LatestDecision'] == 1, df['GT_GridCostFunction'], (df['Minimum_LCOE_Off_grid' + str(gv.endYear)] * settlementConsumption))
    TotalCostScalar = 0
    TotalCostScalar = TotalCost.sum()
    print("gridPop\t\t\t-\t", format(int(gridPop), ','))
    print("gridInvestment\t-\t", format(int(gv.settlementGridInvestment), ','))
    print("TotalCost\t\t-\t", format(int(TotalCostScalar), ','))
    """
    if player_id != 0:
        print(f"TotalCost: {TotalCost[player_id]}\nPrevTotalCost: {PrevTotalCost[player_id]} " )
    print('---------------------------------------------')
    print("gridConsumption\t-\t",format(int(gridConsumption),','))
    print("gridPop\t\t\t-\t", format(int(gridPop), ','))
    print("operationAndMaintenance\t-\t", format(int(operationAndMaintenance), ','))
    """



def player_move(df, enableConnection=False):
    settlementConsumption = df['EnergyPerSettlement' + str(gv.endYear)]
    df['delta'] = np.where(df['GT_LatestDecision'] == 1,
                           (df['GT_GridCostFunction'] - (gv.ACT_COST_2OFFGRID + df['Minimum_LCOE_Off_grid' + str(gv.endYear)]) * settlementConsumption)
                                     / df['Pop' + str(gv.endYear)] * gv.played_flag,
                           ((df['Minimum_LCOE_Off_grid' + str(gv.endYear)] - gv.ACT_COST_2GRID) * settlementConsumption - df['GT_GridCostFunction'])
                                     / df['Pop' + str(gv.endYear)] * gv.played_flag)
    #df['delta'] = np.where(df['GT_LatestDecision'] == 1,
    #                       np.where

    i = df['delta'].idxmax()
    print(f"Delta:\t\t{df['delta'][i]}")
    print(f"GridCost:\t{df['GT_GridCostFunction'][i]}")
    print(f"LCOE:\t\t{df['Minimum_LCOE_Off_grid' + str(gv.endYear)][i]}")
    if gv.moves_cnt_down[i] == 0:
        gv.played_flag[i] = 0
        return False
    if df['GT_LatestDecision'][i] == 1 and df['delta'][i] > 0:
        #if df['GT_CalibratedConnectGrid'][i] != 1:  # if was connected to grid from the beginning, don't disconnect it
        df.loc[i, 'GT_LatestDecision'] = df['Off_Grid_Code' + str(gv.endYear)][i]
        print(f">>>>>>> {i} disconnected")
        gv.moves_cnt_down[i] -= 1
        if gv.moves_cnt_down[i] == 0:
            gv.played_flag[i] = 0
        return True
    elif df['GT_LatestDecision'][i] != 1 and df['delta'][i] > 0:
        gv.moves_cnt_down[i] -= 1
        if enableConnection:
            df.loc[i, 'GT_LatestDecision'] = 1
            print(f">>>>>>> {i} connected")
            if gv.moves_cnt_down[i] == 0:
                gv.played_flag[i] = 0
            return True
    return False
