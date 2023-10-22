"""Performs a regression test of the OnSSET modules

Notes
-----

Run ``python test/test_runner.py`` to update the test files,
if an intended modification is made to the codebase which
changes the contents of the output files.

"""

import filecmp
import os
import sys
from shutil import copyfile
from tempfile import TemporaryDirectory
from game_theory import global_variables as gv
from onsset.runner import calibration, scenario
from game_theory import game_theory
import pandas as pd
import time


st = time.time()
start = time.localtime()
print(f"\nStart of running: {start.tm_hour}:{start.tm_min}")

# Baseline Configuration:
bl_alpha = 0.1
bl_ACT_COST_2OFFGRID = 0.2
bl_num_of_moves = 10

# Configuration:
alpha = 0.8
num_of_moves = bl_num_of_moves
gv.ACT_COST_2OFFGRID = bl_ACT_COST_2OFFGRID
gv.ACT_COST_2GRID = 0  # 0 means not in use
gv.moves_per_player = 1
numOfSettlements_dj = 1473
gv.numOfSettlements = numOfSettlements_dj

gv.run_name = os.path.join('test', 'test_results', 'game_theory_results', "alpha=" + str(alpha))
gv.counter = 0
gv.iter_counter = 0
gv.techLife = 30  # of grid
gv.settlementGridInvestment = 0
gv.gtLatestDecision = 0
gv.played_flag = [1] * gv.numOfSettlements
gv.moves_cnt_down = [gv.moves_per_player] * gv.numOfSettlements

def run_analysis(tmpdir):
    """

    Arguments
    ---------
    tmpdir : str
        Temporary directory to use for the calculated files

    Returns
    -------
    tuple
        Returns a tuple of bool for whether the summary or full files match

    """

    specs_path = os.path.join('test', 'test_data', 'dj-specs-test.xlsx')
    csv_path = os.path.join('test', 'test_data', 'dj-test.csv')
    calibrated_csv_path = os.path.join(tmpdir, 'dj-calibrated.csv')
    specs_path_calib = os.path.join(tmpdir, 'dj-specs-test-calib.xlsx')

    calibration(specs_path, csv_path, specs_path_calib, calibrated_csv_path)

    scenario(specs_path_calib, calibrated_csv_path, tmpdir, tmpdir)

    actual = os.path.join(tmpdir, 'dj-1-1_1_1_1_0_0_summary.csv')
    expected = os.path.join('test', 'test_results', 'expected_summary.csv')
    summary = filecmp.cmp(actual, expected)
    if summary == False:
        print(actual)

    actual = os.path.join(tmpdir, 'dj-1-1_1_1_1_0_0.csv')
    expected = os.path.join('test', 'test_results', 'expected_full.csv')
    full = filecmp.cmp(actual, expected)
    return summary, full


def test_regression_summary():
    """A regression test to track changes to the summary results of OnSSET

    """

    with TemporaryDirectory() as tmpdir:
        summary, full = run_analysis(tmpdir)

    assert summary
    assert full


def update_test_file():
    """A utility function to produce a new test file if intended changes are made
    """
    tmpdir = '.'

    summary, actual = run_analysis(tmpdir)
"""
    actual = os.path.join(tmpdir, 'dj-1-1_1_1_1_0_2_summary.csv')
    expected = os.path.join('test', 'test_results', 'expected_summary.csv')
    if not summary:
        copyfile(actual, expected)

    actual = os.path.join(tmpdir, 'dj-1-1_1_1_1_0_2.csv')
    expected = os.path.join('test', 'test_results', 'expected_full.csv')
    if not actual:
        copyfile(actual, expected)
"""


if __name__ == '__main__':
    update_test_file()

df2 = pd.read_csv(gv.calibratedFileName)
max_iter = gv.numOfSettlements

terminal = sys.stdout
log_name = gv.run_name + "_log.txt"

sys.stdout = open(log_name, 'w')
total_moves_made = 0


while 1:

    df = pd.read_csv(gv.outputFileName)
    df['GT_CalibratedConnectGrid'] = df2['FinalElecCode2018']
    gv.iter_counter += 1

    """ play the game """
    last_iter_changes = game_theory.game_iterations(df, alpha, num_of_moves, False)
    print(f"\nlast_iter_changes: {last_iter_changes}\n\n")
    total_moves_made += last_iter_changes

    # stop conditions
    if last_iter_changes == 0:
        print(f"\ntest_runner: STOPPED >> no changes, iter_count == " + str(gv.iter_counter - 1) + "with num of changes == " + str(total_moves_made))
        break

    if gv.iter_counter == max_iter:
        print(f"\ntest_runner: STOPPED >> reached to max iter_count ({max_iter}" + "with num of changes == " + str(total_moves_made))
        break

    # insert game results to onsset
    gv.settlementGridInvestment = 0
    update_test_file()


et = time.time()
# print(df[df['GT_LatestDecision'] > 1]['GT_LatestDecision'])

print(f"total moves made: {total_moves_made}")
print(f"Runtime: {round((et-st), 3)} seconds")
