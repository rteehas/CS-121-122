# CS121: Current Population Survey (CPS) 
# Stephanie Williams & Ryan Teehan 
# We collaborated with Andrew Chuang on this project
# Functions for mining CPS data 

import csv
import math
import numpy as np
import os
import pandas as pd
import sys
import tabulate
import pa6_helpers

# Constants 
HID = "h_id" 
AGE = "age"
GENDER = "gender" 
RACE = "race" 
ETHNIC = "ethnicity" 
STATUS = "employment_status"
HRWKE = "hours_worked_per_week" 
EARNWKE = "earnings_per_week" 

FULLTIME_MIN_WORKHRS = 35

# CODE_TO_FILENAME: maps a code to the name for the corresponding code
# file
CODE_TO_FILENAME = {"gender_code":"data/gender_code.csv",
                    "employment_status_code": "data/employment_status_code.csv",
                    "ethnicity_code":"data/ethnic_code.csv",
                    "race_code":"data/race_code.csv"}


# VAR_TO_FILENAME: maps a variable-of-interest to the name for the
# corresponding code file
VAR_TO_FILENAME = {GENDER: CODE_TO_FILENAME["gender_code"],
                        STATUS: CODE_TO_FILENAME["employment_status_code"],
                        ETHNIC: CODE_TO_FILENAME["ethnicity_code"],
                        RACE: CODE_TO_FILENAME["race_code"]}

def build_morg_df(morg_filename):
    '''
    Construct a DF from the specified file.  Resulting dataframe will
    use names rather than coded values.
    
    Inputs:
        morg_filename: (string) filename for the morg file.

    Returns: pandas dataframe
    '''
    if os.path.exists(morg_filename) == False:
        return None
    df = pd.read_csv(morg_filename)
    df = df.rename(columns={ "gender_code" : GENDER, "race_code" : RACE, \
                             "ethnicity_code" : ETHNIC, \
                             "employment_status_code" : STATUS})
    l_codes = [GENDER, RACE, STATUS, ETHNIC]
    for i in l_codes:
        df[i] = df[i].fillna(0) 
        cf = pd.read_csv(VAR_TO_FILENAME[i])
        if i != ETHNIC:
            df[i] = df[i] - 1  # Converting to zero-base
        df[i] = pd.Categorical.from_codes(df[i], cf.ix[:,1])           
    return df
 

def calculate_weekly_earnings_stats_for_fulltime_workers(df, gender, race, ethnicity):
    '''
    Calculate statistics for different subsets of a dataframe.

    Inputs:
        df: morg dataframe
        gender: "Male", "Female", or "All"
        race: specific race from a small set, "All", or "Other",
            where "Other" means not in the specified small set
        ethnicity: "Hispanic", "Non-Hispanic", or "All"

    Returns: (mean, median, min, max) for the rows that match the filter.
    '''

    genders = ["Male", "Female"]
    races = ["WhiteOnly", "BlackOnly", "AmericanIndian/AlaskanNativeOnly", \
    "AsianOnly", "Hawaiian/PacificIslanderOnly", "Other"]

    # Generates lists of races, genders, and ethnicites for each input
    if race == "All":
        r_file = pd.read_csv("data/race_code.csv")
        r_df = r_file["race_string"]
        r_cats = r_df.tolist()
    elif race == "Other":
        r_file = pd.read_csv("data/race_code.csv")
        r_df = r_file["race_string"]
        r_list = r_df.tolist()
        r_cats = r_list[5:]
    elif race in races:
        r_cats = [race]
    else:
        return (0,0,0,0)

    if gender == "All":
        g_cats = genders
    elif gender in genders:
        g_cats = [gender]
    else:
        return (0,0,0,0)

    if ethnicity == "All":
        e_file = pd.read_csv("data/ethnic_code.csv")
        e_df = e_file["ethnic_string"]
        e_cats = e_df.tolist()
    elif ethnicity == "Hispanic":
        e_file = pd.read_csv("data/ethnic_code.csv")
        e_df = e_file["ethnic_string"]
        e_list = e_df.tolist()
        e_cats = e_list[1:]
    elif ethnicity == "Non-Hispanic":
        e_cats = [ethnicity]
    else:
        return (0,0,0,0)

    # Selects only workers who work full time
    employed = df[df.employment_status == "Working"]
    employed_fulltime = employed[employed.hours_worked_per_week \
                                >= FULLTIME_MIN_WORKHRS]
    # Selects only those who fit the desired race, gender, 
    # and ethnicity combination
    selection = employed_fulltime.ix[employed_fulltime['gender'].isin(g_cats) \
    & employed_fulltime['race'].isin(r_cats) & \
    employed_fulltime['ethnicity'].isin(e_cats)]
    if len(selection) == 0:
        return (0,0,0,0)

    earnings = selection.iloc[:,7]

    mean = earnings.mean()
    median = earnings.median()
    minimum = earnings.min()
    maximum = earnings.max()
    return (mean, median, minimum, maximum)


def create_histogram(df, var_of_interest, num_buckets, min_val, max_val):
    '''
    Compute the number of full time workers who fall into each bucket
    for a specified number of buckets and variable of interest.

    Inputs:
        df: morg dataframe
        var_of_interest: one of EARNWKE, AGE, HWKE
        num_buckets: the number of buckets to use.
        min_val: minimal value (lower bound) for the histogram (inclusive)
        max_val: maximum value (lower bound) for the histogram (non-inclusive).

    Returns:
        list of integers where ith element is the number of full-time workers
        who fall into the ith bucket.

        empty list if num_buckets <= 0 or max_val <= min_val
    '''
    if num_buckets <= 0 or max_val <= min_val:
        return []
    new_df = df[(df.employment_status == "Working") & \
    (df.hours_worked_per_week >= FULLTIME_MIN_WORKHRS)]
    array_boundaries = np.linspace(min_val, max_val, num_buckets+1)
    n_df = pd.cut(new_df[var_of_interest], bins = array_boundaries, right=False)
    counts = n_df.value_counts(sort=False)  # Sorting by bins  
    return list(counts)


def calculate_unemployment_rates(filenames, age_range, var_of_interest):
    '''
    Calculate the unemployment rate for participants in a given age range (inclusive)
    by values of the variable of interest.

    Inputs:
        filenames: (list of strings) list of morg filenames
        age_range: (pair of ints) (lower_bound, upper_bound)
        var_of_interest: one of "gender", "race", "ethnicity"

    Returns: pandas dataframe
    '''
    l = []
    processed = [] 
    if filenames == []:
        return None 
    for i in filenames:
        if i in processed:
            continue
        processed.append(i)
        start = i.find("morg_d")
        sliced = i[start+6:start+8]
        df = build_morg_df(i)
        (lower, upper) = age_range
        if lower > upper:
            return None  
        new_df = df[((df.age >= lower) & (df.age <= upper))]
        l_df = new_df[new_df[STATUS].isin(["Layoff", "Working", "Looking"])]
        u_df = new_df[new_df[STATUS].isin(["Layoff", "Looking"])]
        labor_counts = l_df[var_of_interest].value_counts(sort = False)
        unemployed_counts = u_df[var_of_interest].value_counts(sort = False)
        percent = unemployed_counts.div(labor_counts)
        l.append(percent.to_frame(name = sliced))  # Sorting by year number

    t_df = pd.concat(l, axis = 1).sort_index(axis = 1)
    t_dfr = t_df.reindex(t_df.index.astype("str")).sort_index().fillna(0)

    return t_dfr

