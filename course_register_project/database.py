from os import environ as env

import data
import mysql.connector
import typer
from dotenv import load_dotenv
from mysql.connector import Error, connect

# Load environment variables
load_dotenv()

"""
This module provides a set of functions for interacting with a MySQL database in a school
or university context. It allows operations like student enrollment, course management, 
setting grades, and obtaining various information from the database.

Modules Required:
    - mysql.connector: For connecting and interacting with MySQL databases.
    - dotenv: For loading environment variables from a .env file.
    - os: To access environment variables.
    - typer: For command-line interfaces and styled output.
    - data: Custom module providing initial data for database population.

Functions:
    - get_connection(): Establishes a connection to the MySQL database using environment variables.
    - reset(): Resets the database structure by executing DDL statements from a file.
    - query(connection, q, data=None, many=False, fetch=None): Executes SQL queries on the given connection.
    - initialize_data(): Populates the database with initial data like students, courses, and prerequisites.
    - add_a_student(first_name, last_name, unix_id): Adds a new student to the database.
    - add_a_new_course(moniker, name, department): Adds a new course to the database.
    - add_a_prerequisite(course, prereq, min_grade): Adds a new prerequisite to the database.
    - set_grade(student, course, grade, year): Sets a grade for a specific student in a course.
    - show_courses_a_student_is_currently_taking(student): Returns a list of courses a student is currently taking.
    - enroll_student(student, course, year): Enrolls a student in a specific course.
    - unenroll_student(student, course, year): Unenrolls a student from a specific course.
    - show_prerequisites_for(course): Shows the prerequisites for a given course.
    - show_student_by(last_name): Returns students whose last name matches a pattern.
    - show_courses_by(department): Returns courses offered by a specific department.
    - get_transcript_for(student): Returns a transcript for a student, including grades and letter grades.
    - get_courses_with_most_enrolled_students(n): Returns the courses with the most enrolled students.
    - get_top_performing_students(n): Returns the top-performing students based on average grades.

Usage:
    1. Ensure that the environment variables are properly set for database connection.
    2. Use the functions to interact with the database as required.
    3. The `typer` module is used for CLI outputs and styling.

Note:
    - Ensure that the database is set up and accessible before using these functions.
    - Customize SQL queries and database structure as required for your use case.
"""

def get_connection():
    """Establishes a connection to the MySQL database using environment variables."""
    connection = None
    try:
        connection = connect(
            database=env.get("MYSQL_DATABASE"),
            host=env.get("MYSQL_HOST"),
            password=env.get("MYSQL_PASSWORD"),
            port=env.get("MYSQL_PORT"),
            user=env.get("MYSQL_USER"),
        )
        if env.get("MYSQL_VERBOSE") == "YES":
            print("Connected to MySQL successfully")
    except Error as e:
        print(f"Error '{e}' occurred while attempting to connect to the database.")

    return connection


def reset():
    """Resets the database structure by executing DDL statements from a file."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            with open("ddl.sql", "r") as f:
                for result in cursor.execute(f.read(), multi=True):
                    if env.get("MYSQL_VERBOSE") == "YES":
                        print("Executed:", result.statement)


def query(connection, q, data=None, many=False, fetch=None):
    """
    Executes a query on the given MySQL connection.

    Args:
        connection: The MySQL connection object.
        q (str): The SQL query to execute.
        data (optional): Data to be used in the query, if required.
        many (bool): Indicates if the query involves multiple rows of data.
        fetch (bool): If True, fetches the result after executing the query.

    Returns:
        If fetch is True, returns the fetched result from the query. Otherwise, commits the changes.

    Raises:
        mysql.connector.IntegrityError, mysql.connector.DatabaseError: If there's an error in the query execution.
    """
    cursor = connection.cursor()

    try:
        if many:
            cursor.executemany(q, data)
        else:
            cursor.execute(q, data)

        if fetch:
            return cursor.fetchall()
        else:
            connection.commit()

        if env.get("MYSQL_VERBOSE") == "YES":
            print("Executed successfully:", q)

        typer.echo(typer.style("Successful", bg=typer.colors.GREEN, fg=typer.colors.BLACK))
    except (mysql.connector.IntegrityError, mysql.connector.DatabaseError) as e:
        typer.echo(f"Statement execution failed: {typer.style(e, bg=typer.colors.RED, fg=typer.colors.BLACK)}")
    finally:
        cursor.close()


def initialize_data():
    """Populates the database with initial data like students, courses, prerequisites, and letter grades."""
    with get_connection() as conn:
        query(conn, "INSERT INTO students (first_name, last_name, unix_id) VALUES (%s, %s, %s);", data.students, many=True)
        query(conn, "INSERT INTO courses (moniker, name, department) VALUES (%s, %s, %s);", data.courses, many=True)
        query(conn, "INSERT INTO prerequisites (course, prereq, min_grade) VALUES (%s, %s, %s);", data.prerequisites, many=True)
        query(conn, "INSERT INTO letter_grade (grade, letter) VALUES (%s, %s);", data.letter_grades, many=True)


def add_a_student(first_name, last_name, unix_id):
    """
    Adds a new student to the database.

    Args:
        first_name (str): The student's first name.
        last_name (str): The student's last name.
        unix_id (str): The student's unique identifier.
    """
    with get_connection() as conn:
        q = "INSERT INTO students (first_name, last_name, unix_id) VALUES(%s, %s, %s);"
        data = (first_name, last_name, unix_id)
        query(conn, q, data)


def add_a_new_course(moniker, name, department):
    """
    Adds a new course to the database.

    Args:
        moniker (str): The course's unique moniker.
        name (str): The name of the course.
        department (str): The department offering the course.
    """
    with get_connection() as conn:
        q = "INSERT INTO courses (moniker, name, department) VALUES(%s, %s, %s);"
        data = (moniker, name, department)
        query(conn, q, data)


def add_a_prerequisite(course, prereq, min_grade):
    """
    Adds a new prerequisite relationship to the database.

    Args:
        course (str): The moniker of the course.
        prereq (str): The moniker of the prerequisite course.
        min_grade (int): The minimum grade required to fulfill the prerequisite.
    """
    with get_connection() as conn:
        q = "INSERT INTO prerequisites (course, prereq, min_grade) VALUES (%s, %s, %s);"
        data = (course, prereq, min_grade)
        query(conn, q, data)


def set_grade(student, course, grade, year):
    """
    Sets a grade for a specific student in a specific course and year.

    Args:
        student (str): The student's unique identifier.
        course (str): The moniker of the course.
        grade (int): The grade to set.
        year (int): The year of the course enrollment.
    """
    with get_connection() as conn:
        q = "UPDATE student_course SET grade = %s WHERE student = %s AND course = %s AND year = %s;"
        data = (grade, student, course, year)
        query(conn, q, data)


def show_courses_a_student_is_currently_taking(student):
    """
    Returns a list of courses that a student is currently taking (without a grade).

    Args:
        student (str): The student's unique identifier.

    Returns:
        List of courses that the student is currently taking.
    """
    with get_connection() as conn:
        q = "SELECT course, year FROM student_course WHERE student = %s AND grade IS NULL;"
        data = (student,)
        
        return query(conn, q, data=data, fetch=True)


def enroll_student(student, course, year):
    """
    Enrolls a student in a specific course for a given year.

    Args:
        student (str): The student's unique identifier.
        course (str): The moniker of the course.
        year (int): The year of enrollment.
    """
    with get_connection() as conn:
        q = "INSERT INTO student_course (student, course, year) VALUES (%s, %s, %s);"
        data = (student, course, year)
        query(conn, q, data)


def unenroll_student(student, course, year):
    """
    Unenrolls a student from a specific course for a given year.

    Args:
        student (str): The student's unique identifier.
        course (str): The moniker of the course.
        year (int): The year of unenrollment.
    """
    with get_connection() as conn:
        q = "DELETE FROM student_course WHERE student = %s AND course = %s AND year = %s;"
        data = (student, course, year)
        query(conn, q, data)


def show_prerequisites_for(course):
    """
    Shows the prerequisites for a specific course.

    Args:
        course (str): The course's moniker.

    Returns:
        List of prerequisites with the minimum required grade for each.
    """
    with get_connection() as conn:
        q = "SELECT prereq, min_grade FROM prerequisites WHERE course = %s"
        data = (course,)
        
        return query(conn, q, data, fetch=True)


def show_student_by(last_name):
    """
    Returns a list of students whose last name matches a specific pattern.

    Args:
        last_name (str): The pattern to match with the last name.

    Returns:
        List of students matching the pattern.
    """
    with get_connection() as conn:
        q = "SELECT first_name, last_name, unix_id FROM students WHERE last_name like %s;"
        data = ('%' + last_name + '%',)
        
        return query(conn, q, data, fetch=True)


def show_courses_by(department):
    """
    Shows courses offered by a specific department.

    Args:
        department (str): The department's name.

    Returns:
        List of courses offered by the department.
    """
    with get_connection() as conn:
        q = "SELECT moniker, name, department FROM courses WHERE department = %s;"
        data = (department,)
        
        return query(conn, q, data, fetch=True)


def get_transcript_for(student):
    """
    Returns a student's transcript, including grades and letter grades.

    Args:
        student (str): The student's unique identifier.

    Returns:
        A list of courses with year, grade, and corresponding letter grade.
    """
    with get_connection() as conn:
        q = """
            SELECT course, year, grade, 
            (select letter
                from letter_grade as lg
                where lg.grade <= sc.grade
                order by lg.grade desc 
                limit 1
            ) as letter 
            FROM student_course as sc 
            WHERE student = %s 
            AND grade IS NOT NULL 
            ORDER BY year;        
        """
        data = (student,)

        return query(conn, q, data, fetch=True)


def get_courses_with_most_enrolled_students(n):
    """
    Returns the courses with the most enrolled students.

    Args:
        n (int): The number of top courses to return.

    Returns:
        List of courses with the highest number of enrolled students.
    """
    with get_connection() as conn:
        q = """
            SELECT course, c.name, count(*) AS enrolled_students
            FROM student_course AS sc
            JOIN courses c on sc.course = c.moniker
            GROUP BY course
            ORDER BY enrolled_students DESC
            LIMIT %s
         """
        data = (n,)

        return query(conn, q, data, fetch=True)


def get_top_performing_students(n):
    """
    Returns the top-performing students based on average grade.

    Args:
        n (int): The number of top students to return.

    Returns:
        List of the top-performing students, including their average grade and other details.
    """
    with get_connection() as conn:
        q = """
            SELECT student, s.first_name, s.last_name, count(*) as courses_taken, 
            avg(grade) as average_grade
            FROM student_course AS sc
                JOIN students s on sc.student = s.unix_id
            WHERE grade IS NOT NULL
            GROUP BY student
            ORDER BY average_grade DESC
            LIMIT %s
        """
        data = (n,)

        return query(conn, q, data, fetch=True)
