import global_variables as gv
import numpy as np


# calculate the cost function for all the relavent players
def game_iterations(df, alpha):
    # initializing parameters for the loop
    df['GT_LatestDecision'] = df['MinimumOverallCode' + str(gv.endYear)]  # create new column in the main df
    df['GT_played_flag'] = 1  #todo _OUR: implement as a counter or delete it!
    #df_last_iter = df['GT_LatestDecision'].copy()  # create new df for comparison between two following iterations
    iter_counter = 0
    offset = 0
    max_iter = 1400
    done = False
    while not done:
        iter_counter += 1
        df_last_iter = df['GT_LatestDecision'].copy()  # save last iteration state

        # play the game
        get_cost_function(df, alpha)
        #offset = player_move_new(df, offset)  # changes the df['GT_LatestDecision'] values
        played = False
        while not played:
            played, player_id = player_move_new_proMax(df)
            df['GT_played_flag'][player_id] = 0
            if (df['move_prio'] <= 0).all():
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
    #print('game_iterations: GT_LatestDecision:\n', df['GT_LatestDecision'])
    return diff_counter_init

def get_cost_function(df, alpha = 0.5):
    # New columns (preparation to the parameters)
    df['GT_GridInvestment'] = gv.settlementGridInvestment
    df['GT_OperationAndMaintenance'] = gv.settlementOperAndMaint[:, -1]

    # Setting the parameters to the function
    beta = 1 - alpha
    gridPop = df.loc[df['GT_LatestDecision'] == 1, 'Pop' + str(gv.endYear)].sum()
    settlementPop = df['Pop' + str(gv.endYear)]
    gridInvestment = df.loc[df['GT_LatestDecision'] == 1, 'GT_GridInvestment'].sum()
    #gridInvestment = gv.settlementGridInvestment
    operationAndMaintenance = df.loc[df['GT_LatestDecision'] == 1, 'GT_OperationAndMaintenance'].sum()
    gridConsumption = df.loc[df['GT_LatestDecision'] == 1, 'EnergyPerSettlement' + str(gv.endYear)].sum()
    settlementConsumption = df['EnergyPerSettlement' + str(gv.endYear)]

    priceVariable = gv.fuelCost*gridConsumption
    priceConstant = gridInvestment / min(gv.projectLife, gv.techLife) + operationAndMaintenance

    # Cost Function if the tech is grid
    gridCostFunc = alpha*(settlementPop/gridPop)*priceConstant + (settlementConsumption/gridConsumption)*(priceVariable + beta*priceConstant)
    df['GT_GridCostFunction'] = gridCostFunc

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
    # print("Our Cost Function: \n", df.loc[df['GT_LatestDecision'] == 1, 'GT_GridCostFunction'], "\n")


def player_move(df):
    settlementConsumption = df['EnergyPerSettlement' + str(gv.endYear)]
    df['GT_LatestDecision'] = \
            np.where(df['GT_GridCostFunction'] > df['Minimum_LCOE_Off_grid' + str(gv.endYear)]*settlementConsumption,
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


def player_move_new(df, offset):
    settlementConsumption = df['EnergyPerSettlement' + str(gv.endYear)]
    print(offset)
    for index, _ in df.iterrows():
        i = (index + offset) % (len(df) - 1)
        if df['GT_CostFunction'][i] > df['Minimum_LCOE_Off_grid' + str(gv.endYear)][i]*settlementConsumption[i] \
                and df['GT_played_flag'][i] == 1:
            if df['GT_LatestDecision'][i] == 1:
                if df['GT_CalibratedConnectGrid'][i] != 1:
                    df['GT_LatestDecision'][i] = df['Off_Grid_Code' + str(gv.endYear)][i]
                    print(i)
                    df['GT_played_flag'][i] = 0
                    return i+1
            elif df['GT_LatestDecision'][i] != 1:
                df['GT_LatestDecision'][i] = 1
                print(i)
                df['GT_played_flag'][i] = 0
                return i+1
    return 0


def player_move_new_proMax(df):
    settlementConsumption = df['EnergyPerSettlement' + str(gv.endYear)]
    df['delta'] = abs((df['GT_GridCostFunction'] - df['Minimum_LCOE_Off_grid' + str(gv.endYear)] * settlementConsumption) * df[
        'GT_played_flag'])
    #print(df['delta'])
    df['move_prio'] = np.where(df['GT_LatestDecision'] == 1, df['delta'], -df['delta'])
    i = df['move_prio'].idxmax()

    print(i)
    print("move_prio:", df['move_prio'][i])


    if df['GT_LatestDecision'][i] == 1:
        if df['GT_CalibratedConnectGrid'][i] != 1:
            df['GT_LatestDecision'][i] = df['Off_Grid_Code' + str(gv.endYear)][i]
            print("player id: ", i)
            return (True, i)
    elif df['GT_LatestDecision'][i] != 1:
        df['GT_LatestDecision'][i] = 1
        print("player id: ", i)
        return (True, i)
    return (False, i)


