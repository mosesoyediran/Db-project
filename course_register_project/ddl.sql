DROP DATABASE IF EXISTS railway;
CREATE DATABASE railway;
USE railway;

CREATE TABLE students 
(
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    unix_id VARCHAR(10) NOT NULL UNIQUE
);

CREATE TABLE courses 
(
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    moniker VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    department VARCHAR(255) NOT NULL
); 

CREATE TABLE prerequisites
(
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    course VARCHAR(10) NOT NULL,
    prereq VARCHAR(10) NOT NULL,
    min_grade INTEGER,
    FOREIGN KEY (course) REFERENCES courses(moniker),
    FOREIGN KEY (prereq) REFERENCES courses(moniker),
    CHECK (min_grade >= 0 AND min_grade <= 100 )
);

CREATE TABLE student_course 
(
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    student VARCHAR(10) NOT NULL,
    course VARCHAR(10) NOT NULL,
    year INTEGER,
    grade INTEGER,
    FOREIGN KEY (student) REFERENCES students(unix_id),
    FOREIGN KEY (course) REFERENCES courses(moniker),
    UNIQUE (student, course, year),
    CHECK (grade >= 0 AND grade <= 100 )
);

DROP TRIGGER IF EXISTS before_student_course_insert;
CREATE TRIGGER before_student_course_insert
    BEFORE INSERT
    ON student_course
    FOR EACH ROW
BEGIN
    # create some temp tables to holds 1) prereqs and 2) unmet prereqs
    DROP TEMPORARY TABLE IF EXISTS temp_prereq;
    DROP TEMPORARY TABLE IF EXISTS unmet_prereqs;
    CREATE TEMPORARY TABLE IF NOT EXISTS temp_prereq
    (
        prereq    VARCHAR(10) REFERENCES courses (moniker),
        min_grade INTEGER
    );

    CREATE TEMPORARY TABLE IF NOT EXISTS unmet_prereqs
    (
        prereq VARCHAR(10) REFERENCES courses (moniker)
    );

    # does this course have prereqs? insert them into the first temp table
    INSERT INTO temp_prereq (prereq, min_grade)
    SELECT prereq, min_grade
    FROM prerequisites as p
    WHERE p.course = NEW.course;

    # are there any prereqs that the student has not met? insert them into the second temp table
    INSERT INTO unmet_prereqs (prereq)
    SELECT prereq
    FROM temp_prereq as tp
    WHERE tp.prereq NOT IN
          (SELECT sc.course FROM student_course as sc WHERE sc.student = NEW.student AND sc.grade > tp.min_grade);

    # if there exist unmet prereq
    if (exists(select 1 from unmet_prereqs) > 0) THEN
        SET @message = CONCAT('Student ', NEW.student, ' cannot take course ', NEW.course, ' because not all the prereqs are met.' );

        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = @message;
    end if;
end;

CREATE TABLE IF NOT EXISTS letter_grade
(
    grade  INTEGER    NOT NULL,
    letter VARCHAR(1) NOT NULL,
    CHECK ( grade >= 0 AND grade <= 100 )
);

