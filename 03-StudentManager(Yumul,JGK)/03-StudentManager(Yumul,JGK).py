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
