import sqlite3
import pandas as pd

conn = sqlite3.connect('school_database.db')
c = conn.cursor()

c.execute("""CREATE TABLE students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            date_of_birth DATE)

""")

c.execute("""
            CREATE TABLE classes (
            class_id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT NOT NULL,
            teacher_name TEXT NOT NULL,
            class_time TIME)
""")

c.execute("""
            CREATE TABLE attendance (
            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            attendance_date DATE NOT NULL,
            student_id INTEGER,
            class_id INTEGER,
            status TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES Students(student_id),
            FOREIGN KEY (class_id) REFERENCES Classes(class_id))

""")