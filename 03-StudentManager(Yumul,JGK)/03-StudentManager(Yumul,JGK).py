"""
John Gareth Kyle C. Yumul
G3 - Level 5 - Cybersecurity
Exercise 3: Student Manager
"""

import tkinter as tk  # GUI toolkit
from pathlib import Path  # Build the data file's path from this script's location
from tkinter import messagebox, ttk  # This are the pop-up dialogs and themed widgets (table, drop-downs)

# Build the path from this file's location so it works from any working directory
Student_File = Path(__file__).parent / "studentMarks.txt"

Min_Code, Max_Code = 1000, 9999  # Valid input for student marks
Coursework_Count = 3  # This makrs three coursworks per student
Coursework_Max = 20  # Coursework of each marks cost 20
Exam_Max = 100  # Exam mark is 100
Max_Total = Coursework_Count * Coursework_Max + Exam_Max  # 160 marks available in total

# Highest first so the first match is the grade (minimum percentage, grade) 
Grade_Boundaries = [(70, "A"), (60, "B"), (50, "C"), (40, "D"), (0, "F")]

# The editable fields used for the "add" form and the "update" drop-down
Fields = ["Student number", "Name", "Coursework 1", "Coursework 2", "Coursework 3", "Exam mark"]

# Table column headings for the output
Column_Names = ("Name", "Student number", f"Coursework (/{Coursework_Count * Coursework_Max})", f"Exam (/{Exam_Max})", "Overall %", "Grade")

# This class is for the student record and the calculation that belongs to it
class Student:
    def __init__(self, code, name, coursework, exam):
        self.code = code  # For student number
        self.name = name  # Student full name
        self.coursework = coursework  # This is the list of the three coursework marks
        self.exam = exam  # Mark for the exam

    # The total amount of the three coursework marks
    def coursework_total(self):
        return sum(self.coursework)

    # Total amount of coursework and exam out of 160
    def total(self):
        return self.coursework_total() + self.exam

    # Overall percentage of the total amount by multiplying before deviding exact cases like 112/160 stay exact
    def percentage(self):
        return self.total() * 100 / Max_Total

    # This is the letter grade the first boundary for the percentage to reach 
    def grade(self):
        percentage = self.percentage()
        return next(letter for cutoff, letter in Grade_Boundaries if percentage >= cutoff)

    # In the format of the file the record is one line
    def to_line(self):
        marks = ",".join(str(mark) for mark in self.coursework)
        return f"{self.code},{self.name},{marks},{self.exam}"

# Sort options for menu item 5: function providing the value to sort on such as name shown
Sort_Keys = {
    "Name": lambda student: student.name.lower(),  # Example: lower() so "alice" and "Bob" sort fairly
    "Student number": lambda student: student.code,
    "Overall %": lambda student: student.percentage(),
}

# Data Handling (This pare has no GUI code so that it can be tested by its own)

# Turn text into a whole number within [low, high], or raise ValueError saying why
def parse_int(text, low, high, label):
    text = text.strip()  # This allow it to ignore spaces around the number
    if not (text.isascii() and text.isdigit()):  # Digits only allow like 0-9 no signsm, decimals or 1_0
        raise ValueError(f"{label} must be a whole number.")
    number = int(text)  # safe now that text is only digits
    if not low <= number <= high:  # This reminds user if user out of range 
        raise ValueError(f"{label} must be between {low} and {high}.")
    return number

# It builds a student from one line of the line or it raise a ValueError
def parse_line(line):
    parts = [part.strip() for part in line.split(",")]  # split on commas and trim each piece
    if len(parts) != 3 + Coursework_Count:  # code, name, three coursework marks, exam
        raise ValueError(f"expected {3 + Coursework_Count} comma-separated values")
    code = parse_int(parts[0], Min_Code, Max_Code, "Student number")  # first value
    name = parts[1]  # second value
    if not name:  # a blank name isn't a valid record
        raise ValueError("name is empty")
    coursework = [parse_int(mark, 0, Coursework_Max, "Coursework mark") for mark in parts[2:2 + Coursework_Count]]  # the three coursework marks
    exam = parse_int(parts[-1], 0, Exam_Max, "Exam mark")  # the last value
    return Student(code, name, coursework, exam)

# Read the file; return (list of students, list of warning messages about skipped lines)
def load_students(path):
    students, warnings, seen_codes = [], [], set()  # This shoes the results so far
    with open(path, encoding="utf-8-sig") as file:  # this is the utf-8-sig drops a Windows BOM
        lines = [line.strip() for line in file if line.strip()]  # This is for non-blank lines only
    if not lines:  # If file has nothing at all
        raise ValueError("The file is empty.")
    header = lines[0]  # The first line is the number of student 
    if not (header.isascii() and header.isdigit()):  # This must be a whole number
        raise ValueError("The first line must be the number of students.")
    for number, line in enumerate(lines[1:], start=1):  # The number of the records from 1
        try:
            student = parse_line(line)  # This try to read the record
        except ValueError as error:  # If bad recors it note it and move on
            warnings.append(f"Record {number} skipped: {error}")
            continue
        if student.code in seen_codes:  # If two students cant share the same student number
            warnings.append(f"Record {number} skipped: duplicate student number {student.code}")
            continue
        seen_codes.add(student.code)  # This allow to remember the student number
        students.append(student)  # It allows to keep the student
    if int(header) != len(students):  # It checks only valid lines even if there are other broken lines
        warnings.append(f"The file says {header} students but {len(students)} valid records were loaded.")
    return students, warnings

# This write all valid student line back to the file in the fist line with that being count
def save_students(path, students):
    lines = [str(len(students))] + [student.to_line() for student in students]  # Header plus Records
    temp = path.with_suffix(".tmp")  # This write a temporary file first
    temp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    temp.replace(path)  # Then it swap in so that a crash mid write cannot corrupt the read file

# Students matching the text: a number matches exactly, anything else matches part of a name
def find_students(students, query):
    query = query.strip()  #this ignores surrounding spaces like " Jake" = "Jake"
    if not query: 
        return []
    if query.isascii() and query.isdigit():  # This decides whether the text is a student number
        return [student for student in students if student.code == int(query)]
    return [student for student in students if query.lower() in student.name.lower()]

# The students in the list is sorted by order  
def sort_students(students, field, descending):
    return sorted(students, key=Sort_Keys[field], reverse=descending)

# This shows the student with the highist or lowest total score it also handles ties so the list may return more than one student
def extreme_students(students, highest):
    totals = [student.total() for student in students]  # This is a list of everyone's total score
    target = max(totals) if highest else min(totals)  # Is an if/else statement that shows the highest total is highest is trure and else lowest
    return [student for student in students if student.total() == target]

# This calculates the average overall percentage across the list of students but it will be 0 if there is no students
def average_percentage(students):
    if not students: # This helps avoud it bein g divided by zero since it will crash 
        return 0.0
    return sum(student.percentage() for student in students) / len(students)

# This checks what the user typed for one field of a studenr record and return a cleaned value or raise ValueErro
def validate_field(field, text, students, current=None):
    if field == "Student number":
        code = parse_int(text, Min_Code, Max_Code, field)  # Numbers must be 1000 - 9999 for student number
        if any(s.code == code and s is not current for s in students):  # The student number is used if user input a same student number 
            raise ValueError(f"Student number {code} is already used.")
        return code
    if field == "Name":
        name = text.strip()  # This trimp spaces
        if not name:
            raise ValueError("Name can't be empty.") # Name should not be empty
        if "," in name:
            raise ValueError("Name can't contain a comma.") # Name should not have a comma cause that will split the name in two inside the file
        return name
    if field == "Exam mark":
        return parse_int(text, 0, Exam_Max, field)  # Exam mark must only be from  0 to 100
    return parse_int(text, 0, Coursework_Max, field)  # Courseworks 1, 2, and 3 are worth 20 each so total is 60

# Changes one field of a student object using a value that has already been validated
def apply_field(student, field, value):
    if field == "Student number":
        student.code = value
    elif field == "Name":
        student.name = value
    elif field == "Exam mark":
        student.exam = value
    else:  # This is an else statement because courswrok 1,2,3 are left which are all storers in a same way
        student.coursework[int(field[-1]) - 1] = value

# The GUI part
