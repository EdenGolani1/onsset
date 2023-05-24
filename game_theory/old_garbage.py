import math
import pandas as pd
import numpy as np
import time


def verion01():
    all_db = pd.read_csv('dj-1-1_1_1_1_0_0.csv')
    grid_list = (all_db[all_db['FinalElecCode2030'] == 1.0]).sort_values(by="Y_deg")
    not_grid_list = all_db[all_db['FinalElecCode2030'] != 1.0]
    row, col = not_grid_list.shape
    new_dots_to_grid_list = pd.DataFrame(data=np.zeros((row, col)), index=range(row), columns=range(col))
    print("gridded dots before: " + str(len(grid_list)))


    # check decision #1:
    # if one dot (or more) under a radius of R km from me will be connected to the grid - I want to connect too
    Radius = 1  #[km] TODO
    orig_grid_list = grid_list
    st = time.time()

    index = 0
    for _, uc_row in not_grid_list.iterrows():
        # UnConnected
        uc_x = uc_row["X_deg"]
        uc_y = uc_row["Y_deg"]

        # the boundaries of the search, since the dots are sorted by the Y deg column
        max_y = hf.calculate_latitude(uc_y, Radius)
        min_y = hf.calculate_latitude(uc_y, -Radius)
        grid_list_Y_deg = grid_list['Y_deg'].tolist()
        min_dot = bisect.bisect_left(grid_list_Y_deg, min_y)
        max_dot = bisect.bisect_right(grid_list_Y_deg, max_y)
        grid_list_cut = orig_grid_list[min_dot:max_dot+1]

        for _, c_row in grid_list_cut.iterrows():
            # Connected
            c_x = c_row["X_deg"]
            c_y = c_row["Y_deg"]
            distance = SettlementProcessor.haversine_vector(uc_x, uc_y, c_x, c_y)  # [km]
            if distance <= Radius:
                # switch to a grid solution
                #new_dots_to_grid_list[index] = uc_row
                new_dots_to_grid_list.iloc[index] = uc_row.values[0]
                index += 1
                break


    et = time.time()
    new_dots_to_grid_list = new_dots_to_grid_list.loc[(new_dots_to_grid_list != 0).any(axis=1)]  # delete empty elements
    grid_list = pd.concat([grid_list,new_dots_to_grid_list], axis=0, ignore_index=True)  # merge the old and new list of gridded dots
    grid_list = grid_list.sort_values(by="Y_deg")
    print("gridded dots after: " + str(len(grid_list)))
    et = time.time()
    #elapsed_time = int(et-st)
    print('Execution time:', elapsed_time, 'seconds')


def calculate_latitude(lat1, distance):
    R = 6371  # Earth radius in kilometers
    lat2 = math.degrees(distance/R) + lat1  # Calculating the new latitude
    return lat2
