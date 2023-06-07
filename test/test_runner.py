"""Performs a regression test of the OnSSET modules

Notes
-----

Run ``python test/test_runner.py`` to update the test files,
if an intended modification is made to the codebase which
changes the contents of the output files.

"""

import filecmp
import os
from shutil import copyfile
from tempfile import TemporaryDirectory

import pandas as pd

from onsset.runner import calibration, scenario

import global_variables as gv
import game_theory
import numpy as np

gv.counter = 0

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

    actual = os.path.join(tmpdir, 'dj-1-1_1_1_1_0_0_summary.csv')
    expected = os.path.join('test', 'test_results', 'expected_summary.csv')
    if not summary:
        copyfile(actual, expected)

    actual = os.path.join(tmpdir, 'dj-1-1_1_1_1_0_0.csv')
    expected = os.path.join('test', 'test_results', 'expected_full.csv')
    if not actual:
        copyfile(actual, expected)


if __name__ == '__main__':
    update_test_file()

df2 = pd.read_csv(gv.calibratedFileName)
last_iter_changes = True
iter_counter = 0
while 1:
    df = pd.read_csv(gv.outputFileName)
    df['GT_CalibratedConnectGrid'] = df2['FinalElecCode2018']

    iter_counter += 1

    # play the game
    last_iter_changes = game_theory.game_iterations(df, 0.15)

    # stop conditions
    print(last_iter_changes)
    if last_iter_changes == 0:
        print("\ntest_runner: STOPPED >> last_iter_changes is 0, iter_count == " + str(iter_counter))
        break
    max_iter = 6
    if iter_counter == max_iter:
        print("\ntest_runner: STOPPED >> iter_count == " + str(max_iter))
        break

    # insert game results to onsset
    update_test_file()

print(df[df['GT_LatestDecision'] > 1 ]['GT_LatestDecision'])