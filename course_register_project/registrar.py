from datetime import datetime
from os import environ as env

import typer
from database import (add_a_new_course, add_a_prerequisite, add_a_student,
                      enroll_student, get_courses_with_most_enrolled_students,
                      get_top_performing_students, get_transcript_for,
                      initialize_data, reset, set_grade,
                      show_courses_a_student_is_currently_taking,
                      show_courses_by, show_prerequisites_for, show_student_by,
                      unenroll_student)
from rich.console import Console
from rich.table import Table

# Create a Typer application for command-line interactions
app = typer.Typer()
console = Console()

"""
This module defines a command-line interface for managing a university/school database system. 
It uses the Typer library to define CLI commands and the Rich library to create styled console output.

Commands:
    - enroll(student, course, year): Enrolls a student in a course for a specific year.
    - unenroll(student, course, year): Unenrolls a student from a course for a specific year.
    - grade(student, course, grade, year): Sets a grade for a student in a specific course and year.
    - add_student(first_name, last_name, unix_id): Adds a new student to the database.
    - add_course(moniker, name, department): Adds a new course to the database.
    - reset_database(verbose, with_data): Resets the database structure and optionally initializes data.
    - add_prereq(course, prereq, min_grade): Adds a prerequisite relationship for a specific course.
    - show_prereqs(course): Shows prerequisites for a specific course.
    - show_students(last_name): Displays students whose last name matches a pattern.
    - show_courses(department): Shows courses offered by a specific department.
    - current_courses(student): Shows the courses a student is currently taking.
    - transcript(student): Displays the transcript for a specific student.
    - most_enrolled(n): Shows the courses with the most enrolled students.
    - top_students(n): Shows the top-performing students based on average grades.

Usage:
    - Use the `typer` module to run the CLI with the defined commands.
    - Each command can be executed from the command line with appropriate parameters.

Note:
    - The `database` module must be properly configured for interaction with MySQL.
    - Ensure environment variables are set for database connection.
"""

def pretty_table(with_headers, data, in_color):
    """
    Creates and displays a table with Rich library styling.

    Args:
        with_headers (list): A list of column headers for the table.
        data (list of tuples): Data to populate the table.
        in_color (str): The color to use for table headers.

    Returns:
        None. The table is displayed on the console.
    """
    table = Table(*with_headers, show_header=True, header_style=f"bold {in_color}")

    for row in data:
        table.add_row(*map(str, row))

    console.print(table)


@app.command()
def enroll(student: str, course: str, year: int = datetime.now().year):
    """
    Enrolls a student in a specific course for a given year.

    Args:
        student (str): The student's unique identifier.
        course (str): The course's moniker.
        year (int): The year for enrollment (default is the current year).

    Usage:
        `python script.py enroll <student> <course> [year]`
    """
    enroll_student(student, course, year)


@app.command()
def unenroll(student: str, course: str, year: int = datetime.now().year):
    """
    Unenrolls a student from a specific course for a given year.

    Args:
        student (str): The student's unique identifier.
        course (str): The course's moniker.
        year (int): The year for unenrollment (default is the current year).

    Usage:
        `python script.py unenroll <student> <course> [year]`
    """
    unenroll_student(student, course, year)


@app.command()
def grade(student: str, course: str, grade: int, year: int = datetime.now().year):
    """
    Sets a grade for a specific student in a specific course and year.

    Args:
        student (str): The student's unique identifier.
        course (str): The course's moniker.
        grade (int): The grade to set.
        year (int): The year for which the grade is set (default is the current year).

    Usage:
        `python script.py grade <student> <course> <grade> [year]`
    """
    set_grade(student, course, grade, year)


@app.command()
def add_student(first_name: str, last_name: str, unix_id: str):
    """
    Adds a new student to the database.

    Args:
        first_name (str): The student's first name.
        last_name (str): The student's last name.
        unix_id (str): The student's unique identifier.

    Usage:
        `python script.py add_student <first_name> <last_name> <unix_id>`
    """
    add_a_student(first_name, last_name, unix_id)


@app.command()
def add_course(moniker: str, name: str, department: str):
    """
    Adds a new course to the database.

    Args:
        moniker (str): The course's unique moniker.
        name (str): The name of the course.
        department (str): The department offering the course.

    Usage:
        `python script.py add_course <moniker> <name> <department>`
    """
    add_a_new_course(moniker, name, department)


@app.command()
def reset_database(verbose: bool = False, with_data: bool = True):
    """
    Resets the database structure and optionally initializes data.

    Args:
        verbose (bool): If set to True, additional output is displayed.
        with_data (bool): If set to True, the database is initialized with default data.

    Usage:
        `python script.py reset_database [--verbose] [--with_data]`
    """
    answer = input("This will delete all the data. Are you sure? (Y/N): ")
    
    if verbose:
        env["MYSQL_VERBOSE"] = "YES"

    if answer.strip().lower() == "y":
        reset()
        typer.echo("Database reset successfully.")
        
        if with_data:
            initialize_data()
            typer.echo("Data initialized successfully.")
    else:
        typer.echo("Database reset aborted.")


@app.command()
def add_prereq(course: str, prereq: str, min_grade: int):
    """
    Adds a prerequisite relationship for a specific course.

    Args:
        course (str): The moniker of the course.
        prereq (str): The moniker of the prerequisite course.
        min_grade (int): The minimum grade required to fulfill the prerequisite.

    Usage:
        `python script.py add_prereq <course> <prereq> <min_grade>`
    """
    add_a_prerequisite(course, prereq, min_grade)


@app.command()
def show_prereqs(course: str):
    """
    Shows prerequisites for a specific course in a styled table.

    Args:
        course (str): The course's moniker.

    Usage:
        `python script.py show_prereqs <course>`
    """
    pretty_table(["Prerequisites", "Minimum Grade"], data=show_prerequisites_for(course), in_color="yellow")


@app.command()
def show_students(last_name: str):
    """
    Displays students whose last name matches a pattern in a styled table.

    Args:
        last_name (str): The pattern to match with the last name.

    Usage:
        `python script.py show_students <last_name>`
    """
    data = show_student_by(last_name)
    pretty_table(["First Name", "Last Name", "UnixId"], data, in_color="blue")


@app.command()
def show_courses(department: str):
    """
    Shows courses offered by a specific department in a styled table.

    Args:
        department (str): The name of the department.

    Usage:
        `python script.py show_courses <department>`
    """
    data = show_courses_by(department)
    pretty_table(["Moniker", "Name", "Department"], data, in_color="red")


@app.command()
def current_courses(student: str):
    """
    Shows the courses a student is currently taking in a styled table.

    Args:
        student (str): The student's unique identifier.

    Usage:
        `python script.py current_courses <student>`
    """
    data = show_courses_a_student_is_currently_taking(student)
    pretty_table(["Course", "Year"], data, in_color="green")


@app.command()
def transcript(student: str):
    """
    Displays the transcript for a specific student in a styled table, including average GPA.

    Args:
        student (str): The student's unique identifier.

    Usage:
        `python script.py transcript <student>`
    """
    data = get_transcript_for(student)
    pretty_table(["Course", "Year", "Grade", "Letter Grade"], data, in_color="magenta")
    console.print(f"Average GPA: {sum([row[2] for row in data]) / len(data):.2f}", style="bold")


@app.command()
def most_enrolled(n: int = 10):
    """
    Shows the courses with the most enrolled students in a styled table.

    Args:
        n (int): The number of top courses to show (default is 10).

    Usage:
        `python script.py most_enrolled [n]`
    """
    data = get_courses_with_most_enrolled_students(n)
    pretty_table(["Course", "Name", "Enrollment"], data, in_color="blue")


@app.command()
def top_students(n: int = 10):
    """
    Shows the top-performing students based on average grade in a styled table.

    Args:
        n (int): The number of top students to show (default is 10).

    Usage:
        `python script.py top_students [n]`
    """
    data = get_top_performing_students(n)
    pretty_table(
        ["UnixId", "First Name", "Last Name", "Courses Taken", "Average Grade"],
        data,
        in_color="green",
    )


if __name__ == "__main__":
    app()
