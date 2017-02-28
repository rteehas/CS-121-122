### CS122, Winter 2017: Course search engine: search
###
### Andrew Chuang and Ryan Teehan
### Referenced Jae Ahn's question on ordering
### for help on the attributes to be returned.

from math import radians, cos, sin, asin, sqrt
import sqlite3
import json
import re
import os


# Use this filename for the database
DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'course-info.db')

def query_constructor(args_from_ui):
    '''
    Constructs SQL query from list of arguments.

    Inputs:
        args_from_ui (dictionary): input dictionary
        formed from user's inputs

    Outputs:
        query_list (list): list containing items to be
        included in sql query. 
    '''
    query_list = []
    tuple_list = []
    dept_num = ["courses.dept", "courses.course_num"]
    multiple_attributes = ["sections.section_num", "meeting_patterns.day", 
        "meeting_patterns.time_start", "meeting_patterns.time_end"]

    if "day" in args_from_ui or "time_start" in args_from_ui \
     or "time_end" in args_from_ui or "section_num" in args_from_ui:
        query_list = query_list + dept_num + multiple_attributes
        multiple_attributes = []
        dept_num = []
        
    if "walking_time" in args_from_ui and "building" in args_from_ui:
        query_list = query_list + dept_num + multiple_attributes + \
        ["a.building_code", "b.building_code", \
        "time_between(a.lon, a.lat, b.lon, b.lat) AS walking_time"]
        multiple_attributes = []
        dept_num = []

    if "enroll_lower" in args_from_ui or "enroll_upper" in args_from_ui:
        query_list = query_list + dept_num + multiple_attributes + \
        ["enrollment"]
        multiple_attributes = []
        dept_num = [] 

    if "terms" in args_from_ui or "dept" in args_from_ui:
        query_list =  query_list + dept_num + ["courses.title"]

    return query_list


def table_builder(args_from_ui):
    '''
    Function takes list of attributes to be returned and
    returns tables that need to be joined together.

    Inputs:
        query_list (list): list of attributes to be found

    Outputs:
        query_string (string): string that contains the SQL
        query to be run.
    '''
    table_string = " FROM courses"
    section_meet_string = (" JOIN sections ON courses.course_id ==" 
    " sections.course_id JOIN meeting_patterns ON " 
    "meeting_patterns.meeting_pattern_id == sections.meeting_pattern_id")


    if "day" in args_from_ui or "time_start" in args_from_ui \
     or "time_end" in args_from_ui or "section_num" in args_from_ui:
        table_string = table_string + section_meet_string
        section_meet_string = ""

    if "terms" in args_from_ui:
        table_string = table_string + (" JOIN catalog_index ON "
        "courses.course_id == catalog_index.course_id")

    if "enroll_lower" in args_from_ui \
    or "enroll_upper" in args_from_ui:
        table_string = table_string + section_meet_string 

    if "walking_time" in args_from_ui and "building" in args_from_ui:
        table_string = table_string + section_meet_string + \
        (" JOIN gps AS a JOIN gps AS b ON sections.building_code = b.building_code")

    return table_string


def where_builder(args_from_ui, query_list):
    '''
    Function takes user input dictionary and 
    produces the inputs for the query. 

    Inputs: 
        query_list (list): list made from query

    Outputs:
        where_string (string): 
        string that specifies parameters for sql query. 

    '''
    where_string = " WHERE"
    and_string = ""
    for condition in query_list:
        if "dept" in condition:
            if "dept" in args_from_ui:
                where_string = where_string + and_string \
                + " courses.dept = ?"
        if "day" in condition:
            if "day" in args_from_ui:
                if len(args_from_ui["day"]) == 1:
                    where_string = where_string + and_string \
                    + " meeting_patterns.day = ?"
                if len(args_from_ui["day"]) > 1:
                    where_string = where_string + and_string + " meeting_patterns.day = ?" + (( " OR"
                    + " meeting_patterns.day = ?") * (len(args_from_ui["day"]) - 1))

        if "time_start" in condition:
            if "time_start" in args_from_ui:
                where_string = where_string + and_string \
            + " meeting_patterns.time_start >= ?" 
        
        if "time_end" in condition:
            if "time_end" in args_from_ui:
                where_string = where_string + and_string \
            + " meeting_patterns.time_end <= ?"
        
        if "a.building_code" in condition:
            where_string = where_string + and_string \
            + " a.building_code = ?"

        if "walking_time" in condition:
            where_string = where_string + and_string \
            + " a.building_code < b.building_code AND walking_time <= ?"

        if "enrollment" in condition:
            if "enroll_lower" in args_from_ui:
                where_string = where_string + and_string \
                + " sections.enrollment <= ?"
            if "enroll_upper" in args_from_ui:
                where_string = where_string + and_string \
                + " sections.enrollment >= ?"
        
        if "title" in condition:
            if len(args_from_ui["terms"].split()) == 1:
                where_string = where_string + and_string \
                + " courses.title LIKE ?"
            if len((args_from_ui["terms"].split())) > 1:
                where_string = where_string + and_string + " courses.title LIKE ?" + (( " AND" 
                + " courses.title LIKE ?") * (len((args_from_ui["terms"].split())) - 1))
        
        if where_string != " WHERE":
            and_string = " AND"

    return where_string
            #Add walking_time  title if conditional on this 

def sql_combiner(args_from_ui):
    '''
    Function takes outputs of where_builder, table_builder
    as well as the query_constructor to produce the string
    that is eventually used in the SQL 

    Inputs:
        args_from_ui (dictionary): dictionary from inputs of
        the user

    Outputs:
        sql_query (string): string used in sql query
    '''

    sql_query_list = query_constructor(args_from_ui)
    if "courses.dept" not in sql_query_list:
        sql_query_list = ["courses.dept", "courses.course_num"] + sql_query_list
    select_string = "SELECT " + ", ".join(sql_query_list)
    table_string = table_builder(args_from_ui)
    where_string = where_builder(args_from_ui, sql_query_list)
    sql_query = select_string + table_string + where_string
    return sql_query


def find_courses(args_from_ui):
    '''
    Takes a dictionary containing search criteria and returns courses
    that match the criteria.  The dictionary will contain some of the
    following fields:

      - dept a string
      - day is array with variable number of elements  
           -> ["'MWF'", "'TR'", etc.]
      - time_start is an integer in the range 0-2359
      - time_end is an integer an integer in the range 0-2359
      - enroll is an integer
      - walking_time is an integer
      - building ia string
      - terms is a string: "quantum plato"]

    Returns a pair: list of attribute names in order and a list
    containing query results.
    '''

    attribute_list = ["dept", "day", "course_num", "section_num", 
    "time_start", "time_end", "walking_time", "building", 
    "enroll_upper","enroll_lower", "terms"]
    param_list = []
    for attribute in attribute_list:
        if attribute in args_from_ui:
            if attribute == "day":
                for i in args_from_ui["day"]:
                    param_list.append(i)
            elif attribute == "terms":
                if len(args_from_ui["terms"].split()) >= 1:
                    for i in args_from_ui["terms"].split():
                        param_list.append("%" + i + "%")
                elif len(args_from_ui["terms"].split()) == 1:
                    param_list.append("%" + args_from_ui['terms'] + "%")
            else:
                param_list.append(args_from_ui[attribute])
    param_list = tuple(param_list)
    query_list = query_constructor(args_from_ui)
    attribute_names = []

    query_string = sql_combiner(args_from_ui)
    course_conn = sqlite3.connect(DATABASE_FILENAME)
    course_cursor = course_conn.cursor()
    course_conn.create_function("time_between", 4, compute_time_between)
    
    result_rows = course_cursor.execute(query_string, param_list)
    actual_rows = []

    for row in result_rows:
        actual_rows.append(row)

    headers = []
    if actual_rows == []:
        headers == []
    else:
        headers = get_header(course_cursor)
    course_conn.close()
    return (headers, actual_rows)
    


########### auxiliary functions #################
########### do not change this code #############

def compute_time_between(lon1, lat1, lon2, lat2):
    '''
    Converts the output of the haversine formula to walking time in minutes
    '''
    meters = haversine(lon1, lat1, lon2, lat2)

    #adjusted downwards to account for manhattan distance
    walk_speed_m_per_sec = 1.1 
    mins = meters / (walk_speed_m_per_sec * 60)

    return mins


def haversine(lon1, lat1, lon2, lat2):
    '''
    Calculate the circle distance between two points 
    on the earth (specified in decimal degrees)
    '''
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 

    # 6367 km is the radius of the Earth
    km = 6367 * c
    m = km * 1000
    return m 



def get_header(cursor):
    '''
    Given a cursor object, returns the appropriate header (column names)
    '''
    desc = cursor.description
    header = ()

    for i in desc:
        header = header + (clean_header(i[0]),)

    return list(header)


def clean_header(s):
    '''
    Removes table name from header
    '''
    for i in range(len(s)):
        if s[i] == ".":
            s = s[i+1:]
            break

    return s



########### some sample inputs #################

example_0 = {"time_start":930,
             "time_end":1500,
             "day":["MWF"]}

example_1 = {"building":"RY",
             "dept":"CMSC",
             "day":["MWF", "TR"],
             "time_start":1030,
             "time_end":1500,
             "enroll_lower":20,
             "terms":"computer science"}

