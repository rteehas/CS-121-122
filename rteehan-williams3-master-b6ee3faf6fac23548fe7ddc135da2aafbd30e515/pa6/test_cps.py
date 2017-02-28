# CS121: CPS Assignment
#
# Original:
#   Yanjing Li 
#   October 2015
#
# Revised:
#   Anne Rogers
#   April 2016
#
# Included in automatically generated test code.

import json
import math
import os
import pandas as pd
import pytest
import sys

# Handle the fact that the grading code may not
# be in the same directory as schelling.py
sys.path.append(os.getcwd())

import cps

# Get the test files from the same directory as this file.
BASE_DIR = os.path.dirname(__file__)
TEST_DIR = "data"

EPS = 0.000001

expected_dfs = {}

def gen_morg_filename(tag, prefix=""):
    return os.path.join(BASE_DIR, TEST_DIR, prefix + "morg_d{}.csv".format(tag))

def get_expected(tag):
    '''
    Read tranformed morg data from a file.  Convert categorical
    columns to have type category.

    Input:
        tag: (string) year and possibly "_mini"

    Returns: dataframe with morg data.
    '''

    global expected_dfs

    if tag in expected_dfs:
        return expected_dfs[tag]

    expected_filename = gen_morg_filename(tag, prefix="expected_")
    expected_morg_dict = pd.read_csv(expected_filename)
    for field in ["gender", "race", "employment_status", "ethnicity"]:
        expected_morg_dict[field] =  expected_morg_dict[field].astype("category")

    expected_dfs[tag] = expected_morg_dict

    return expected_morg_dict


def helper_build_morg(tag):
    '''
    Helper function for testing build_morg function.

    Input:
        tag: (string) year and possible "_mini"

    '''
    input_filename = gen_morg_filename(tag)
    actual = cps.build_morg_df(input_filename)
    expected = get_expected(tag)
    flag, msg = validate_result(actual, expected)
    if not flag:
        pytest.fail(msg)


def helper_test_create_histogram(tag, field, num_buckets, min_val, max_val, expected):
    '''
    Helper function for testing create_histogram.
    
    Input: 
        tags: (list of string) tags
        field: (string) name of the field for this histogram
        num_buckets: (int) number of buckets for the histogram
        min_val, max_val: (floats) range of values to include
        expected: list of integers
    '''
    # use the transformed morg file in case the student's build is
    # broken.
    morg_dict = get_expected(tag)    
    actual = cps.create_histogram(morg_dict, field, num_buckets, min_val, max_val)
    if actual != expected:
        msg = "Actual and expected histograms do not match\n\tActual:{}\nExpected:{}"
        pytest.fail(msg.format(actual, expected))



def validate_result(actual, expected):
    '''
    Compare two dataframes.  Inputs can contain a mix of types,
    including floats.

    Inputs:
        actual: pandas dataframe
        expected: pandas dataframe

    Returns: boolean, string with an error message
    '''

    if actual is None:
        if expected is not None:
            return (False, "Actual is None, when expected is not None\n")
        else:
            return (True, None)

    if expected is None:
        return (False, "Actual is not None, when expected is None\n")

    if actual.equals(expected):
        return (True, None)

    actual_row_names = actual.index.get_values().tolist()
    actual_col_names = actual.columns.get_values().tolist()

    expected_row_names = expected.index.get_values().tolist()
    expected_col_names = expected.columns.get_values().tolist()

    if actual_row_names != expected_row_names:
        msg = "Row names differ.    Expected: {}\n    Actual: {}"
        return False, msg.format(expected_row_names, actual_row_names)

    if actual_col_names != expected_col_names:
        msg = "Column names differ.    Expected: {}\n    Actual: {}"
        return False, msg.format(expected_col_names, actual_col_names)

    for col_name in actual_col_names:
        for row_name in actual_row_names:
            a = actual[col_name][row_name]
            e = expected[col_name][row_name]
            
            msg = "Actual and expected differ at {}, {}.\n    Expected: {}\n    Actual: {}"

            if isinstance(e, float):
                if (abs(a - e) > EPS) or \
                   (math.isnan(a) and not math.isnan(e)) or \
                   (not math.isnan(a) and math.isnan(e)):
                    return False, msg.format(col_name, row_name, e, a)
            elif a != e:
                return False, msg.format(col_name, row_name, e, a)

    return True, None


def helper_test_calculate_unemployment_rates(tags, age_range, var_of_interest, expected_filename):
    '''
    Helper function for testing calculate_unemployment_rates.

    Input:
       tags: (list of strings) list of tags
       age_range: (pair of integers) range of ages to include
       var_of_interest: (string) variable to group by for computing rates
       expected_filename: name of the file with the expected results
    '''

    filenames = [gen_morg_filename(tag) for tag in tags]
    actual = cps.calculate_unemployment_rates(filenames, age_range, var_of_interest)
    if actual is not None:
        actual.columns.name = var_of_interest
    
    if expected_filename is not None:
        if not os.path.exists(expected_filename):
            pytest.fail("Cannot find expected file:", expected_filename)
        expected = pd.read_csv(os.path.join(BASE_DIR, expected_filename), index_col=0)
        expected.columns.name = var_of_interest
    else:
        expected = None

    flag, msg = validate_result(actual, expected)
    if not flag:
        pytest.fail(msg)


def helper_calculate_weekly_earnings_stats_for_fulltime_workers(tag, gender, race, ethnicity, expected):
    '''
    Helper function for testing calculate_weekly_earnings_stats_for_fulltime_workers

    Inputs:
        tag: (string) year and possibly "_mini"
        gender: one of "Male", "Female", or "All"
        race: one of "WhiteOnly", "BlackOnly", "AmericanIndian/AlaskanNativeOnly",
           "AsianOnly", "Hawaiian/PacificIslanderOnly", "Other", or "All"
        ethnicity: one of "Hispanic", "Non-Hispanic", or "All"
    '''

    # use the transformed morg file in case the student's build is
    # broken.
    morg_dict = get_expected(tag)
    actual = cps.calculate_weekly_earnings_stats_for_fulltime_workers(morg_dict, gender, race, ethnicity)

    if len(actual) != 4:
        pytest.fail("Actual result has length {:d}.  Expected length is 4.".format(len(actual)))

    EPS = 0.000001
    for i in range(len(actual)):
        if abs(actual[i] - expected[i]) > EPS:
            msg = "Actual and expected do not match.\n    Actual: {}\n    Expected: {}"
            pytest.fail(msg.format(actual, expected))

def test_build_00():
    '''
    Check: build_morg on file: morg_d07_mini
    '''
    helper_build_morg("07_mini")


def test_build_01():
    '''
    Check: build_morg on file: morg_d10_mini
    '''
    helper_build_morg("10_mini")


def test_build_02():
    '''
    Check: build_morg on file: morg_d14_mini
    '''
    helper_build_morg("14_mini")


def test_weekly_earnings_00():
    '''
    Basic test: tests for specific values
    '''
    helper_calculate_weekly_earnings_stats_for_fulltime_workers("10_mini", "Female", "WhiteOnly", "Non-Hispanic", [1451.92, 1403.84, 576.91999999999996, 2375.0])


def test_weekly_earnings_01():
    '''
    Check: correct definition of Hispanic
    '''
    helper_calculate_weekly_earnings_stats_for_fulltime_workers("10_mini", "Male", "WhiteOnly", "Hispanic", [680.5, 680.5, 400.0, 961.0])


def test_weekly_earnings_02():
    '''
    Check: out All for race
    '''
    helper_calculate_weekly_earnings_stats_for_fulltime_workers("10_mini", "Male", "All", "Hispanic", [876.7433333333333, 961.0, 400.0, 1269.23])


def test_weekly_earnings_03():
    '''
    Check: bad filter values
    '''
    helper_calculate_weekly_earnings_stats_for_fulltime_workers("07_mini", "Black-White", "All", "All", (0, 0, 0, 0))


def test_weekly_earnings_04():
    '''
    Check: definition of full-time
    '''
    helper_calculate_weekly_earnings_stats_for_fulltime_workers("07", "All", "All", "All", [862.5145338157122, 700.0, 0.0, 2884.6100000000001])


def test_histogram_00():
    '''
    Boundary condition: no buckets
    '''
    expected = []
    helper_test_create_histogram("07_mini", "hours_worked_per_week", 0, 0.000000, 40.000000, expected)


def test_histogram_01():
    '''
    Boundary condition: 2 buckets, where floating point issues can make it difficult to get the boundaries right.
    '''
    expected = [0, 0]
    helper_test_create_histogram("14_mini", "hours_worked_per_week", 2, 1000.000000, 1001.000000, expected)


def test_histogram_02():
    '''
    Basic test
    '''
    expected = [1, 0, 1, 1, 9, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0]
    helper_test_create_histogram("07_mini", "hours_worked_per_week", 20, 35.000000, 60.000000, expected)


def test_histogram_03():
    '''
    Basic test: includes all ages
    '''
    expected = [0, 0, 0, 0, 0, 1, 1, 0, 1, 2, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    helper_test_create_histogram("10_mini", "earnings_per_week", 50, 0.000000, 3000.000000, expected)


def test_histogram_04():
    '''
    Boundary case: no particpants in this age range
    '''
    expected = [4, 2, 5]
    helper_test_create_histogram("14_mini", "earnings_per_week", 3, 99.500000, 1500.000000, expected)


def test_unemployment_00():
    '''
    Basic test
    '''
    helper_test_calculate_unemployment_rates(['14_mini', '10_mini'], (17, 30), "race", "data/expected_calculate_unemployment_rates_test_0.csv")


def test_unemployment_01():
    '''
    Boundary case: 14_mini occurs twice
    '''
    helper_test_calculate_unemployment_rates(['14_mini', '10_mini', '14_mini', '07_mini'], (17, 80), "gender", "data/expected_calculate_unemployment_rates_test_1.csv")


def test_unemployment_02():
    '''
    Boundary case: no participants match the filter 
    '''
    helper_test_calculate_unemployment_rates(['10_mini'], (1000, 1001), "ethnicity", "data/expected_calculate_unemployment_rates_test_2.csv")


