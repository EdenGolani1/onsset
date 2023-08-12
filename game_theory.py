import global_variables as gv
import numpy as np


# calculate the cost function for all the relavent players
def game_iterations(df, alpha):
    # initializing parameters for the loop
    df['GT_LatestDecision'] = df['MinimumOverallCode' + str(gv.endYear)]  # create new column in the main df

    #df_last_iter = df['GT_LatestDecision'].copy()  # create new df for comparison between two following iterations
    iter_counter = 0
    print("ALPHA:\t", round(alpha,2))

    while 1:
        iter_counter += 1
        df_last_iter = df['GT_LatestDecision'].copy()  # save last iteration state

        # play the game
        get_cost_function(df, alpha)
        player_move(df)  # changes the df['GT_LatestDecision'] values

        # comparison to last iteration
        comparison_to_last_iter = df['GT_LatestDecision'].compare(df_last_iter, keep_shape=True, keep_equal=True)
        diff_counter_iter = len(comparison_to_last_iter[comparison_to_last_iter['self'] != comparison_to_last_iter['other']])

        # stop conditions
        if diff_counter_iter == 0:
            print("\ngame_iterations: STOPPED >> diff_counter_iter == 0")
            break
        max_iter = 30
        if iter_counter == max_iter:
            print("\ngame_iterations: STOPPED >> iter_count == " + str(max_iter))
            break

    df['GT_LatestDecision'] = np.where(df['MinimumOverallCode' + str(gv.endYear)] == df['GT_LatestDecision'], 0, df['GT_LatestDecision'])
    diff_counter_init = (df['GT_LatestDecision'] != 0).sum()
    print("game_iterations: ITER COUNT:\t", iter_counter, "| DIFF COUNTER:\t", diff_counter_init)
    print("========================================================================")
    gv.gtLatestDecision = df['GT_LatestDecision'].copy()
    #print('game_iterations: GT_LatestDecision:\n', df['GT_LatestDecision'])
    return diff_counter_init

def get_cost_function(df, alpha = 0.5):
    # New columns (preparation to the parameters)
    df['GT_GridInvestment'] = gv.settlementGridInvestment
    df['GT_OperationAndMaintenance'] = gv.settlementOperationAndMaintenance[:, -1]

    # Setting the parameters to the function
    beta = 1 - alpha
    gridPop = df.loc[df['GT_LatestDecision'] == 1, 'Pop' + str(gv.endYear)].sum()
    settlementPop = df['Pop' + str(gv.endYear)]
    gridInvestment = df.loc[df['GT_LatestDecision'] == 1, 'GT_GridInvestment'].sum()
    operationAndMaintenance = df.loc[df['GT_LatestDecision'] == 1, 'GT_OperationAndMaintenance'].sum()
    priceConstant = gridInvestment/min(gv.projectLife, gv.techLife) + operationAndMaintenance
    settlementConsumption = df['EnergyPerSettlement' + str(gv.endYear)]
    gridConsumption = df.loc[df['GT_LatestDecision'] == 1, 'EnergyPerSettlement' + str(gv.endYear)].sum()
    priceVariable = gv.fuelCost*gridConsumption

    # Cost Function if the tech is grid
    costFuncGrid = alpha*(settlementPop/gridPop)*priceConstant + (settlementConsumption/gridConsumption)*(priceVariable + beta*priceConstant)
    """df.loc[df['GT_LatestDecision'] == 1, 'GT_CostFunction'] = costFuncGrid
    # Cost Function if the tech is not grid
    costFuncNotGrid = df['MinimumOverallLCOE' + str(gv.endYear)]*settlementConsumption
    df.loc[df['GT_LatestDecision'] != 1, 'GT_CostFunction'] = costFuncNotGrid"""
    df['GT_CostFunction'] = costFuncGrid

    # Prints
    # print("First Coefficient: \n", settlementPop/gridPop, "\n")
    # print("Second Coefficient: \n", settlementConsumption/gridConsumption, "\n")
    # print("Our Cost Function: \n", costFuncGrid, "\n")
    # print("ONSSET's Cost Function: \n", costFuncNotGrid, "\n")
    print('---------------------------------------------')
    print("gridConsumption\t-\t",format(int(gridConsumption),','))
    print("priceConstant\t-\t", format(int(priceConstant),','))
    print("gridInvestment\t-\t", format(int(gridInvestment),','))
    print("gridPop\t\t\t-\t", format(int(gridPop), ','))
    print("operationAndMaintenance\t-\t", format(int(operationAndMaintenance), ','))
    # print("Our Cost Function: \n", df.loc[df['GT_LatestDecision'] == 1, 'GT_CostFunction'], "\n")


def player_move(df):
    settlementConsumption = df['EnergyPerSettlement' + str(gv.endYear)]
    """
    Conds and Values:
    off_grid_is_cheaper = (df['GT_CostFunction'] > df['Minimum_LCOE_Off_grid' + str(gv.endYear)]*settlementConsumption)
    is_connected_to_grid = (df['GT_LatestDecision'] == 1)
    was_connected_in_2018 = (df['GT_CalibratedConnectGrid'] != 1)
    no_change = df['GT_LatestDecision']
    """
    df['GT_LatestDecision'] = \
            np.where(df['GT_CostFunction'] > df['Minimum_LCOE_Off_grid' + str(gv.endYear)]*settlementConsumption,
                     # off grid is cheaper
                     np.where(df['GT_LatestDecision'] == 1,
                              np.where(df['GT_CalibratedConnectGrid'] != 1,
                                       df['Off_Grid_Code' + str(gv.endYear)],
                                       df['GT_LatestDecision']),
                              df['GT_LatestDecision']),
                     # grid is cheaper
                     np.where(df['GT_LatestDecision'] != 1,  # not connected to grid
                              1,  # connect it
                              df['GT_LatestDecision']),
                     )

