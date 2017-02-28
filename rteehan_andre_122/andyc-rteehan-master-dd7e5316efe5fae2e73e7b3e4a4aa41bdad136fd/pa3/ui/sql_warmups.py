#Warmup problems for SQL
#Andrew Chuang and Ryan Teehan

import sqlite3

connect = sqlite3.connect("course-info.db")
cursor = connect.cursor()

# Find the titles of all courses with department code “CMSC” in the course table.
code = ("CMSC",)
cursor.execute("SELECT title FROM courses WHERE dept = ?", code)
data = cursor.fetchall()
for row in data:
    print(row)

#Find the department names, course numbers, and section numbers for courses being offered on MWF at 10:30am (represented as 1030)

#inputs = ("MWF", "1030")
cursor.execute("""
    SELECT courses.dept, courses.course_id, sections.section_id, 
    FROM courses, 
    JOIN sections
        ON sections.course_id = course.course_id 
    JOIN meeting_patterns
        ON meeting_patterns.meeting_pattern_id = sections.meeting_pattern_id
    WHERE meeting_patterns.day == "MWF" AND meeting_patterns.time_start = 1030
    """)
data = cursor.fetchall()
for row in data:
    print(row)


#Find the department names and course numbers for courses being offered in Ryerson on MWF between 10:30am and 3pm (represented as 1500).


#Find the department names, course numbers, and course titles for courses 


#being offered on MWF at 9:30am (represented as 930) that have the words “programming” and “abstraction” in their title/course description.
