from game_theory import global_variables as gv
import numpy as np

TotalCost = 0


# calculate the cost function for all the relevant players
def game_iterations(df, alpha):
    # initializing parameters for the loop
    df['GT_LatestDecision'] = df['MinimumOverallCode' + str(gv.endYear)]  # create new column in the main df
    df['GT_played_flag'] = 1  #todo _OUR: implement as a counter or delete it!
    iter_counter = 0
    offset = 0
    max_iter = 1400
    done = False
    player_id = 0
    while not done:
        iter_counter += 1
        df_last_iter = df['GT_LatestDecision'].copy()  # save last iteration state

        # play the game
        get_cost_function(df, alpha , player_id)
        played = False
        while not played:
            played, player_id = player_move(df)
            df['GT_played_flag'][player_id] = 0
            if (df['delta'] <= 0).all():
                done = True
                break

        # comparison to last iteration
        comparison_to_last_iter = df['GT_LatestDecision'].compare(df_last_iter, keep_shape=True, keep_equal=True)
        diff_counter_iter = len(comparison_to_last_iter[comparison_to_last_iter['self'] != comparison_to_last_iter['other']])

        # stop conditions
        if diff_counter_iter == 0:
            print("\ngame_iterations: STOPPED >> diff_counter_iter == 0")
            break

        if iter_counter == max_iter:
            print("\ngame_iterations: STOPPED >> iter_count == " + str(max_iter))
            break

    df['GT_LatestDecision'] = np.where(df['MinimumOverallCode' + str(gv.endYear)] == df['GT_LatestDecision'], 0, df['GT_LatestDecision'])
    diff_counter_init = (df['GT_LatestDecision'] != 0).sum()
    print("game_iterations: ITER COUNT:\t", iter_counter, "| DIFF COUNTER:\t", diff_counter_init)
    print("========================================================================")
    gv.gtLatestDecision = df['GT_LatestDecision'].copy()
    return diff_counter_init


def get_cost_function(df, alpha = 0.5 , player_id = 0):
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
    df['GT_PotentialGridInvestment'] = np.where(df['GT_LatestDecision'] == 1, gridInvestment, gridInvestment + df['GT_GridInvestment'])

    operationAndMaintenance = df.loc[df['GT_LatestDecision'] == 1, 'GT_OperationAndMaintenance'].sum()
    df['GT_PotentialOperationAndMaintenance'] = np.where(df['GT_LatestDecision'] == 1, operationAndMaintenance, operationAndMaintenance + df['GT_OperationAndMaintenance'])

    settlementConsumption = df['EnergyPerSettlement' + str(gv.endYear)]
    gridConsumption = df.loc[df['GT_LatestDecision'] == 1, 'EnergyPerSettlement' + str(gv.endYear)].sum()
    df['GT_PotentialGridConsumption'] = np.where(df['GT_LatestDecision'] == 1, gridConsumption, gridConsumption + df['EnergyPerSettlement' + str(gv.endYear)])

    priceVariableScalar = gv.fuelCost * gridConsumption
    priceVariable = gv.fuelCost * df['GT_PotentialGridConsumption']
    priceConstant = gridInvestment / min(gv.projectLife, gv.techLife) + operationAndMaintenance
    df['GT_PotentialPriceConstant'] = np.where(df['GT_LatestDecision'] == 1, priceConstant, df['GT_PotentialGridInvestment'] / min(gv.projectLife, gv.techLife) + df['GT_PotentialOperationAndMaintenance'])
    print(f"df['GT_PotentialPriceConstant']: {df['GT_PotentialPriceConstant'][player_id]}")
    # Cost Function if the tech is grid
    gridCostFunc = alpha*(settlementPop/df['GT_PotentialGridPop'])*df['GT_PotentialPriceConstant'] + (settlementConsumption/df['GT_PotentialGridConsumption'])*(priceVariable + beta * df['GT_PotentialPriceConstant'])
    df['GT_GridCostFunction'] = gridCostFunc

    PrevTotalCost = TotalCost
    TotalCost = np.where(df['GT_LatestDecision'] == 1, df['GT_GridCostFunction'], (df['Minimum_LCOE_Off_grid' + str(gv.endYear)] * settlementConsumption))
    TotalCostScalar = 0
    TotalCostScalar = TotalCost.sum()
    if player_id != 0:
        print(f"TotalCost: {TotalCost[player_id]}\nPrevTotalCost: {PrevTotalCost[player_id]} " )
    # Prints
    print('---------------------------------------------')
    print("gridConsumption\t-\t",format(int(gridConsumption),','))
    print("gridInvestment\t-\t", format(int(gridInvestment),','))
    print("gridPop\t\t\t-\t", format(int(gridPop), ','))
    print("operationAndMaintenance\t-\t", format(int(operationAndMaintenance), ','))
    print("TotalCost\t\t\t-\t", format(int(TotalCostScalar), ','))


def player_move(df):
    settlementConsumption = df['EnergyPerSettlement' + str(gv.endYear)]
    df['delta'] = np.where(df['GT_LatestDecision'] == 1,
                           (df['GT_GridCostFunction'] - gv.ACT_COST_2OFFGRID * df['Minimum_LCOE_Off_grid' + str(gv.endYear)] * settlementConsumption)
                                     / df['Pop' + str(gv.endYear)] * df['GT_played_flag'],
                           (df['Minimum_LCOE_Off_grid' + str(gv.endYear)] * settlementConsumption - gv.ACT_COST_2GRID * df['GT_GridCostFunction'])
                                     / df['Pop' + str(gv.endYear)] * df['GT_played_flag'])

    i = df['delta'].idxmax()
    print(f"df['GT_LatestDecision']: {df['GT_LatestDecision'][i]}\ndf['delta']: {df['delta'][i]}\ndf['GT_GridCostFunction']: {df['GT_GridCostFunction'][i]}\ndf['Minimum_LCOE_Off_grid' + str(gv.endYear)] * settlementConsumption: {df['Minimum_LCOE_Off_grid' + str(gv.endYear)][i] * settlementConsumption[i]}")
    if df['GT_LatestDecision'][i] == 1 and df['delta'][i] > 0:
        if df['GT_CalibratedConnectGrid'][i] != 1:  # if was connected to grid from the beginning, don't disconnect it
            df['GT_LatestDecision'][i] = df['Off_Grid_Code' + str(gv.endYear)][i]
            return (True, i)
    elif df['GT_LatestDecision'][i] != 1 and df['delta'][i] > 0:
        df['GT_LatestDecision'][i] = 1
        return (True, i)
    return (False, i)
