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
        self.code = code # For student number
        self.name = name # Student full name
        self.coursework = coursework # This is the list of the three coursework marks
        self.exam = exam # Mark for the exam

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
    "Name": lambda student: student.name.lower(), # Example: lower() so "alice" and "Bob" sort fairly
    "Student number": lambda student: student.code,
    "Overall %": lambda student: student.percentage(),
}

# Data Handling (This pare has no GUI code so that it can be tested by its own)

# Turn text into a whole number within [low, high], or raise ValueError saying why
def parse_int(text, low, high, label):
    text = text.strip() # This allow it to ignore spaces around the number
    if not (text.isascii() and text.isdigit()): # Digits only allow like 0-9 no signsm, decimals or 1_0
        raise ValueError(f"{label} must be a whole number.")
    number = int(text) # safe now that text is only digits
    if not low <= number <= high: # This reminds user if user out of range 
        raise ValueError(f"{label} must be between {low} and {high}.")
    return number

# It builds a student from one line of the line or it raise a ValueError
def parse_line(line):
    parts = [part.strip() for part in line.split(",")] # split on commas and trim each piece
    if len(parts) != 3 + Coursework_Count: # code, name, three coursework marks, exam
        raise ValueError(f"expected {3 + Coursework_Count} comma-separated values")
    code = parse_int(parts[0], Min_Code, Max_Code, "Student number") # first value
    name = parts[1] # second value
    if not name: # a blank name isn't a valid record
        raise ValueError("name is empty")
    coursework = [parse_int(mark, 0, Coursework_Max, "Coursework mark") for mark in parts[2:2 + Coursework_Count]] # the three coursework marks
    exam = parse_int(parts[-1], 0, Exam_Max, "Exam mark") # the last value
    return Student(code, name, coursework, exam)

# Read the file; return (list of students, list of warning messages about skipped lines)
def load_students(path):
    students, warnings, seen_codes = [], [], set() # This shoes the results so far
    with open(path, encoding="utf-8-sig") as file: # this is the utf-8-sig drops a Windows BOM
        lines = [line.strip() for line in file if line.strip()] # This is for non-blank lines only
    if not lines: # If file has nothing at all
        raise ValueError("The file is empty.")
    header = lines[0] # The first line is the number of student 
    if not (header.isascii() and header.isdigit()): # This must be a whole number
        raise ValueError("The first line must be the number of students.")
    for number, line in enumerate(lines[1:], start=1): # The number of the records from 1
        try:
            student = parse_line(line) # This try to read the record
        except ValueError as error: # If bad recors it note it and move on
            warnings.append(f"Record {number} skipped: {error}")
            continue
        if student.code in seen_codes: # If two students cant share the same student number
            warnings.append(f"Record {number} skipped: duplicate student number {student.code}")
            continue
        seen_codes.add(student.code) # This allow to remember the student number
        students.append(student) # It allows to keep the student
    if int(header) != len(students): # It checks only valid lines even if there are other broken lines
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
    query = query.strip() #this ignores surrounding spaces like " Jake" = "Jake"
    if not query: 
        return []
    if query.isascii() and query.isdigit(): # This decides whether the text is a student number
        return [student for student in students if student.code == int(query)]
    return [student for student in students if query.lower() in student.name.lower()]

# The students in the list is sorted by order  
def sort_students(students, field, descending):
    return sorted(students, key=Sort_Keys[field], reverse=descending)

# This shows the student with the highist or lowest total score it also handles ties so the list may return more than one student
def extreme_students(students, highest):
    totals = [student.total() for student in students] # This is a list of everyone's total score
    target = max(totals) if highest else min(totals) # Is an if/else statement that shows the highest total is highest is trure and else lowest
    return [student for student in students if student.total() == target]

# This calculates the average overall percentage across the list of students but it will be 0 if there is no students
def average_percentage(students):
    if not students: # This helps avoud it bein g divided by zero since it will crash 
        return 0.0
    return sum(student.percentage() for student in students) / len(students)

# This checks what the user typed for one field of a studenr record and return a cleaned value or raise ValueErro
def validate_field(field, text, students, current=None):
    if field == "Student number":
        code = parse_int(text, Min_Code, Max_Code, field) # Numbers must be 1000 - 9999 for student number
        if any(s.code == code and s is not current for s in students): # The student number is used if user input a same student number 
            raise ValueError(f"Student number {code} is already used.")
        return code
    if field == "Name":
        name = text.strip() # This trimp spaces
        if not name:
            raise ValueError("Name can't be empty.") # Name should not be empty
        if "," in name:
            raise ValueError("Name can't contain a comma.") # Name should not have a comma cause that will split the name in two inside the file
        return name
    if field == "Exam mark":
        return parse_int(text, 0, Exam_Max, field) # Exam mark must only be from  0 to 100
    return parse_int(text, 0, Coursework_Max, field) # Courseworks 1, 2, and 3 are worth 20 each so total is 60

# Changes one field of a student object using a value that has already been validated
def apply_field(student, field, value):
    if field == "Student number":
        student.code = value
    elif field == "Name":
        student.name = value
    elif field == "Exam mark":
        student.exam = value
    else: # This is an else statement because courswrok 1,2,3 are left which are all storers in a same way
        student.coursework[int(field[-1]) - 1] = value

# The GUI part

# This hold all the student list and menu that builds the whole window
class StudentManager:
    # This builds the menu, input area, result tables and the summary line
    def __init__(self, root, students, path):
        self.root = root # This is the main window
        self.students = students # This is the list of student object and the working copy that can either add, delete or edit
        self.path = path # This is to show where the user inputs changes are saved

        menu = tk.Frame(root) # This is the left column where it holds all the menu buttons
        menu.pack(side="left", fill="y", padx=10, pady=10)
        tk.Label(menu, text="MENU", font=("Times New Roman", 16, "bold")).pack(pady=(0, 8))
        options = [  # Button text and the function to run
            ("1. View all student records", self.show_all),
            ("2. View individual student record", self.show_find),
            ("3. Show student with highest total score", lambda: self.show_extreme(True)),
            ("4. Show student with lowest total score", lambda: self.show_extreme(False)),
            ("5. Sort student records", self.show_sort),
            ("6. Add a student record", self.show_add),
            ("7. Delete a student record", self.show_delete),
            ("8. Update a student's record", self.show_update),
        ]
        for text, command in options:  # This is a one button per action
            tk.Button(menu, text=text, width=34, anchor="w", command=command).pack(pady=3)
        tk.Button(menu, text="Quit", width=34, command=root.destroy).pack(pady=(15, 0))

        main = tk.Frame(root) # The right side shows the input, table and summary
        main.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)

        self.controls = tk.Frame(main) # This is the input area where contents change per menu items
        self.controls.pack(fill="x", pady=(0, 8))

        table_frame = tk.Frame(main) # This hold the table and its scrollbar
        table_frame.pack(fill="both", expand=True)
        self.table = ttk.Treeview(table_frame, columns=Column_Names, show="headings", height=16)
        widths = (180, 110, 120, 90, 90, 60) # The pixels width of each column
        for name, width in zip(Column_Names, widths): # pair each heading with its width
            self.table.heading(name, text=name) # The column heading text
            self.table.column(name, width=width, anchor="w" if name == "Name" else "center")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set) # The link table and scrollbar
        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.summary = tk.Label(main, text="", anchor="w", justify="left", font=("Times New Roman", 12))
        self.summary.pack(fill="x", pady=(8, 0)) # This is the summry or status line under the table 

        self.show_all() # This start by showing every student on the list

# Helpers for the menu

    #This replace the tables rows with students and set the summary line
    def _show(self, students, summary):
        self.table.delete(*self.table.get_children()) # This remove the old rows
        for student in students:
            self.table.insert("", "end", values=(student.name, student.code, student.coursework_total(), student.exam, f"{student.percentage():.1f}%", student.grade())) # It add one row per student with the values in the same order as the columns
        self.summary.config(text=summary) # This shows the caller's message under the table

    # This empties the input area so each menu item starts with a blank space
    def _clear_controls(self):
        for widget in self.controls.winfo_children():
            widget.destroy()

    # This is a summary text it shows how many student are there and their average percentage
    def _class_summary(self, students):
        return f"Students in class: {len(students)} Average percentage: {average_percentage(students):.1f}%"

    # This saves the student list to the file but shows an error and return False if that fails
    def _save(self):
        try:
            save_students(self.path, self.students)
        except OSError as error: # this is if the file locked or disk full but in general a file problem
            messagebox.showerror("Could not save", f"The file was not updated: {error}")
            return False
        return True

    # This finds exactly one student from what the user input or return none if it cant
    def _select_one(self, query):
        matches = find_students(self.students, query) # This shows everyone who matches
        if not matches:# This shows id user input not match
            messagebox.showinfo("Not found", "No student matches that name or number.")
            return None
        if len(matches) > 1: # This shows more the one student that match user input and will ask for student number instead
            self._show(matches, "More than one match - enter the student number instead.")
            messagebox.showinfo("Several matches", "More than one student matches. Enter the student number instead.")
            return None
        return matches[0]    

# Menu items helpers for 1-8
    
    # Item 1: This shows every student and thier class summary
    def show_all(self):
        self._clear_controls() # item 1 does not need user input
        self._show(self.students, self._class_summary(self.students))

    # Item 2: This is for when user shows where the user can find a specific student by typing student name or number
    def show_find(self):
        self._clear_controls()
        tk.Label(self.controls, text="Student name or number:").pack(side="left")
        entry = tk.Entry(self.controls, width=24) # This is for where the user types the search
        entry.pack(side="left", padx=6)
        entry.focus_set() # This is for the cursor that is ready to type

        def search(event=None): # This is where the action is run on the button or enter key
            matches = find_students(self.students, entry.get())
            self._show(matches, f"{len(matches)} matching student(s)." if matches else "No student found.") # If the match has found no student

        entry.bind("<Return>", search) # This is the enter that triggers the search
        tk.Button(self.controls, text="Search", command=search).pack(side="left")
        self._show([], "Enter a name (or one part of the name) or a student number.")  # This shows the instructions for the user input

    # Items 3 and 4: This is for when output shows the highest (Item 3) or lowest (Item 4) total score it also shows all ties to the user
    def show_extreme(self, highest):
        self._clear_controls()
        if not self.students: # If there is no student to show
            self._show([], "There are no students.")
            return
        chosen = extreme_students(self.students, highest) # This is for one student or several if tied will be shown
        word = "Highest" if highest else "Lowest"
        self._show(chosen, f"{word} total score: {chosen[0].total()} / {Max_Total} ({len(chosen)} student(s)).")

    # Item 5: This is for when user wants to sort the student by a choosen a field then has button to know if its ascending or descending
    def show_sort(self):
        self._clear_controls()
        tk.Label(self.controls, text="Sort by:").pack(side="left")
        field = ttk.Combobox(self.controls, values=list(Sort_Keys), state="readonly", width=16)  # drop-down
        field.current(0) # This is for the preselect the first option but user can edit it 
        field.pack(side="left", padx=6)
        order = tk.StringVar(value="asc") # This holds which radio button is chosen
        tk.Radiobutton(self.controls, text="Ascending", variable=order, value="asc").pack(side="left")
        tk.Radiobutton(self.controls, text="Descending", variable=order, value="desc").pack(side="left")

        def apply_sort(): # This runs whenuser clikecd Sort button
            ordered = sort_students(self.students, field.get(), order.get() == "desc")
            self._show(ordered, self._class_summary(ordered))

        tk.Button(self.controls, text="Sort", command=apply_sort).pack(side="left", padx=6)
        apply_sort() # This show a sorted table straight away

    # Item 6: This is for when user create a new student by the user
    def show_add(self):
        self._clear_controls()
        entries = {} # The field name are also its entry widget
        for row, field in enumerate(Fields): # This is the labelled box per field
            tk.Label(self.controls, text=f"{field}:").grid(row=row, column=0, sticky="e", padx=4, pady=2)
            entries[field] = tk.Entry(self.controls, width=24)
            entries[field].grid(row=row, column=1, pady=2)

        def add(): # This runs when "Add student" button is clicked
            try:
                values = {f: validate_field(f, entries[f].get(), self.students) for f in Fields}  # check every box
            except ValueError as error: # This will show when the first invalid box stops the add
                messagebox.showerror("Invalid input", str(error))
                return
            student = Student(values["Student number"], values["Name"], [values[f"Coursework {n}"] for n in range(1, Coursework_Count + 1)], values["Exam mark"])
            self.students.append(student)  # This add in memory of the newly added student
            if not self._save():  # If file couldn't be updated it undo the change
                self.students.remove(student)
                return
            for entry in entries.values():  # This clear the form for the next new student to be added
                entry.delete(0, tk.END)
            self._show([student], f"Added {student.name} ({student.code}). Students in class: {len(self.students)}.")

        tk.Button(self.controls, text="Add student", command=add).grid(row=len(Fields), column=1, sticky="w", pady=6)

    # Item 7: This is for when user deletes a student info after confirmation
    def show_delete(self):
        self._clear_controls()
        tk.Label(self.controls, text="Student name or number to delete:").pack(side="left")
        entry = tk.Entry(self.controls, width=24)
        entry.pack(side="left", padx=6)

        def delete(event=None): # This runs on the button or the enter key
            student = self._select_one(entry.get())  # This shows exactly one match or none
            if student is None:
                return
            if not messagebox.askyesno("Confirm delete", f"Delete {student.name} ({student.code})?"):
                return  # If user changed their mind mid way
            index = self.students.index(student)  # This remember the position in case we must undo
            del self.students[index] # This removes in memory
            if not self._save(): # This file couldn't be updated the student will be put back
                self.students.insert(index, student)
                return
            entry.delete(0, tk.END) # This clear the box
            self._show([], f"Deleted {student.name} ({student.code}). Students in class: {len(self.students)}.")

        entry.bind("<Return>", delete)
        tk.Button(self.controls, text="Delete", command=delete).pack(side="left")

    # Item 8: This is for when user updates a field of one student
    def show_update(self):
        self._clear_controls()
        tk.Label(self.controls, text="Student name or number:").grid(row=0, column=0, sticky="e", padx=4, pady=2)
        who = tk.Entry(self.controls, width=24) # This is to identify which student user want to update
        who.grid(row=0, column=1, pady=2)
        tk.Label(self.controls, text="Field to update:").grid(row=1, column=0, sticky="e", padx=4, pady=2)
        which = ttk.Combobox(self.controls, values=Fields, state="readonly", width=21) # This is the the sub-menu
        which.current(0)
        which.grid(row=1, column=1, pady=2)
        tk.Label(self.controls, text="New value:").grid(row=2, column=0, sticky="e", padx=4, pady=2)
        new = tk.Entry(self.controls, width=24) # This is the the replacement value
        new.grid(row=2, column=1, pady=2)

        def update(): # This runs when "Update" button is clicked
            student = self._select_one(who.get()) # This shows exactly one match or none
            if student is None:
                return
            field = which.get() # This is where which field will change
            try:
                value = validate_field(field, new.get(), self.students, current=student)
            except ValueError as error:
                messagebox.showerror("Invalid input", str(error))
                return
            backup = (student.code, student.name, list(student.coursework), student.exam)
            apply_field(student, field, value)  # This changes the memory
            if not self._save(): # If file couldn't be updated it will undo the changes
                student.code, student.name, student.coursework, student.exam = backup
                return
            new.delete(0, tk.END) # This clear the value box for the next student that the user wants to update
            self._show([student], f"Updated {field} for {student.name}. File saved.")

        tk.Button(self.controls, text="Update", command=update).grid(row=3, column=1, sticky="w", pady=6)

# This Loads the data and then builds the window or will shows an error and quits
def main():
    root = tk.Tk() # This is for the one main window
    root.title("Student Manager")
    root.geometry("1000x560")

    try:
        students, warnings = load_students(Student_File) # THis read the data file
    except (OSError, ValueError) as error:
        # THis is for the error in the file OSError: file missing/unreadable while ValueError: empty file, bad first line or bad encoding (UnicodeDecodeError is a subclass of ValueError)
        root.withdraw() # This does not flash an empty window behind the error
        messagebox.showerror("Could not load students", f"{Student_File.name}: {error}")
        root.destroy()
        return

    StudentManager(root, students, Student_File)  # build the interface
    if warnings: # If some lines were skipped: tell the user
        shown = "\n".join(warnings[:10]) + ("\n..." if len(warnings) > 10 else "")
        messagebox.showwarning("Some records were skipped", shown + "\n\nSkipped lines are NOT kept if you later add, delete or update a record.")
    root.mainloop() # It wait for user to click


# This runs only when this file is executed directly not when imported
if __name__ == "__main__":
    main()
